# -*- coding: utf-8 -*-
"""
An implementation of the training pipeline of AlphaZero for Gomoku

@author: Junxiao Song
"""

from __future__ import print_function
import random
import numpy as np
from collections import defaultdict

from .env import *
from .mcts_pure import MCTSPlayer as MCTS_Pure
from .mcts_alphaZero import MCTSPlayer_AlphaZero as MCTS_AlphaZero
from .game_collector import GameCollector

class TrainPipeline():
    def __init__(self, model, dir_save, game_args = dict()):
        # fixed training params
        self.learn_rate = 2e-3
        self.lr_multiplier = 1.0  # adaptively adjust the learning rate based on KL
        self.temp = 1e-3  # the temperature param
        self.n_playout = 1600  # num of simulations for each move
        self.pure_mcts_playout_num = 10000 # num of pure MCTS eval simulations
        self.c_puct = 5
        self.epochs = 5  # num of train_steps for each update
        self.kl_targ = 0.02
        self.check_freq = 50
        self.best_win_ratio = 0.0
        self.game_batch_num = 2
        self.batch_size = 1  # mini-batch size for training
        # num of simulations used for the pure mcts, which is used as
        # the opponent to evaluate the trained policy
        
        self.game_args = game_args
        self.game = Game(**game_args)
        self.policy_value_net = model
        self.dir_save = dir_save
        self.name = model.name
        self.game_collector = GameCollector()
        self.n_epoch = 0
    
        self.mcts_player = MCTS_AlphaZero(self.policy_value_net.policy_value_fn,
                                      c_puct=self.c_puct,
                                      n_playout=self.n_playout,
                                      selfplay=True)


    def train(self):
        plays = self.game_collector.collect_selfplay(self.mcts_player, batch_size = self.batch_size, 
                        temp=self.temp, filepath = self.dir_save+self.name+"_gamebatch"+str(self.n_epoch) + ".pkl")
        # plays = self.game_collector.load_selfplay(self.dir_save + "test_selfplay2.pkl")
        _, state_batch_tmp, mcts_probs_batch_tmp, policy_grad_batch = zip(*plays)
        state_batch = []
        mcts_probs_batch = []
        for states, mcts_probs in zip(state_batch_tmp, mcts_probs_batch_tmp):
            state_batch.extend(states)
            mcts_probs_batch.append(np.array(mcts_probs))
        mcts_probs_batch = np.concatenate(mcts_probs_batch, axis=0)
        policy_grad_batch = np.concatenate(policy_grad_batch, axis=0)
        # print(len(state_batch), mcts_probs_batch.shape, policy_grad_batch.shape)
        assert len(state_batch) == mcts_probs_batch.shape[0]
        assert len(state_batch) == policy_grad_batch.shape[0]

        vectors = [state.to_vector() for state in state_batch]
        vec_board_batch = np.stack((x[0] for x in vectors), axis=0)
        vec_state_batch = np.stack((x[1] for x in vectors), axis=0)
        state_batch = (vec_board_batch, vec_state_batch)

        old_probs, old_v = self.policy_value_net.policy_value_batch(state_batch)
        for i in range(self.epochs):
            loss, entropy = self.policy_value_net.train_step(
                    state_batch,
                    mcts_probs_batch,
                    policy_grad_batch,
                    self.learn_rate*self.lr_multiplier)
            new_probs, new_v = self.policy_value_net.policy_value_batch(state_batch)
            kl = np.mean(np.sum(old_probs * (
                    np.log(old_probs + 1e-10) - np.log(new_probs + 1e-10)),
                    axis=1)
            )
            if kl > self.kl_targ * 4:  # early stopping if D_KL diverges badly
                break
        # adaptively adjust the learning rate
        if kl > self.kl_targ * 2 and self.lr_multiplier > 0.1:
            self.lr_multiplier /= 1.5
        elif kl < self.kl_targ / 2 and self.lr_multiplier < 10:
            self.lr_multiplier *= 1.5

        explained_var_old = (1 -
                             np.var(np.array(policy_grad_batch) - old_v.flatten()) /
                             np.var(np.array(policy_grad_batch)))
        explained_var_new = (1 -
                             np.var(np.array(policy_grad_batch) - new_v.flatten()) /
                             np.var(np.array(policy_grad_batch)))
        print(("kl:{:.5f},"
               "lr_multiplier:{:.3f},"
               "loss:{},"
               "entropy:{},"
               "explained_var_old:{:.3f},"
               "explained_var_new:{:.3f}"
               ).format(kl,
                        self.lr_multiplier,
                        loss,
                        entropy,
                        explained_var_old,
                        explained_var_new))
        return loss, entropy

    def policy_evaluate(self, n_games=10):
        """
        Evaluate the trained policy by playing against the pure MCTS player
        Note: this is only for monitoring the progress of training
        """
        current_mcts_player = MCTS_AlphaZero(self.policy_value_net.policy_value_fn,
                                         c_puct=self.c_puct,
                                         n_playout=self.n_playout,
                                         selfplay=False)
        pure_mcts_player = MCTS_Pure(c_puct=self.c_puct,
                                     n_playout=self.pure_mcts_playout_num)
        alphazero_cnt, pure_cnt, draw_cnt = 0, 0, 0
        for i in range(n_games):
            print("Eval: game", (i+1))
            game = Game(self.game_args)
            white_player = current_mcts_player if i % 2 else pure_mcts_player
            black_player = pure_mcts_player if i % 2 else current_mcts_player
            while True:
                is_over, winner = game.is_over()
                if is_over:
                    break
                current_player = white_player if game.current_player == WHITE else black_player
                move, _ = current_player.get_action(game, self.temp)
                print(str(move))
                game.do_move(move)
            if winner is None:
                draw_cnt += 1
            elif (winner == WHITE and white_player is current_mcts_player) or (winner == BLACK and black_player is current_mcts_player):
                alphazero_cnt += 1
            elif (winner == WHITE and white_player is pure_mcts_player) or (winner == BLACK and black_player is pure_mcts_player):
                pure_cnt += 1
                
        win_ratio = 1.0*(alphazero_cnt + 0.5*draw_cnt) / n_games
        print("num_playouts:{}, win: {}, lose: {}, tie:{}".format(
                self.pure_mcts_playout_num,
                alphazero_cnt, pure_cnt, draw_cnt))
        return win_ratio

    def run(self):
        """run the training pipeline"""
        try:
            for i in range(self.game_batch_num):
                self.n_epoch += 1
                loss, entropy = self.train()
                # check the performance of the current model,
                # and save the model params
                if (i+1) % self.check_freq == 0:
                    print("current self-play batch: {}".format(i+1))
                    win_ratio = self.policy_evaluate()
                    self.policy_value_net.save_model(self.dir_save, self.n_epoch)
                    if win_ratio > self.best_win_ratio:
                        print("New best policy!!!!!!!!")
                        self.best_win_ratio = win_ratio
                        # update the best_policy
                        self.policy_value_net.save_model(self.dir_save, self.n_epoch, is_best=True)
                        if (self.best_win_ratio == 1.0 and
                                self.pure_mcts_playout_num < 5000):
                            self.pure_mcts_playout_num += 1000
                            self.best_win_ratio = 0.0
        except KeyboardInterrupt:
            print('\n\rquit')

