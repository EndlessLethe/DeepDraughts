# -*- coding: utf-8 -*-
"""
An implementation of the training pipeline of AlphaZero for Gomoku

@author: Junxiao Song
"""

from __future__ import print_function
import random
import numpy as np
from collections import defaultdict

from .env.game import Game
from .mcts_pure import MCTSPlayer as MCTS_Pure
from .mcts_alphaZero import MCTSPlayer_AlphaZero as MCTS_AlphaZero
from .game_collector import GameCollector

class TrainPipeline():
    def __init__(self, model, dir_save, game = None):
        # fixed training params
        self.learn_rate = 2e-3
        self.lr_multiplier = 1.0  # adaptively adjust the learning rate based on KL
        self.temp = 1.0  # the temperature param
        self.n_playout = 1600  # num of simulations for each move
        self.c_puct = 5
        self.epochs = 5  # num of train_steps for each update
        self.kl_targ = 0.02
        self.check_freq = 50
        self.best_win_ratio = 0.0
        self.game_batch_num = 1000
        self.batch_size = 2  # mini-batch size for training
        # num of simulations used for the pure mcts, which is used as
        # the opponent to evaluate the trained policy
        


        if game is None:
            game = Game()
        self.game = game
        self.policy_value_net = model
        self.dir_save = dir_save
        self.name = model.name
        self.game_collector = GameCollector()
        self.n_epoch = 0
    
        self.mcts_player = MCTS_AlphaZero(self.policy_value_net.policy_value_fn,
                                      c_puct=self.c_puct,
                                      n_playout=self.n_playout,
                                      inference=False)


    def train(self):
        # plays = self.game_collector.collect_selfplay(self.mcts_player, 
                    # batch_size = self.batch_size, filepath = self.dir_save + self.name + str(self.n_epoch) + ".pkl")
        plays = self.game_collector.load_selfplay(self.dir_save + "selfplay1.pkl")
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
                                         n_playout=self.n_playout)
        pure_mcts_player = MCTS_Pure(c_puct=5,
                                     n_playout=self.pure_mcts_playout_num)
        win_cnt = defaultdict(int)
        for i in range(n_games):
            winner = self.game.start_play(current_mcts_player,
                                          pure_mcts_player,
                                          start_player=i % 2,
                                          is_shown=0)
            win_cnt[winner] += 1
        win_ratio = 1.0*(win_cnt[1] + 0.5*win_cnt[-1]) / n_games
        print("num_playouts:{}, win: {}, lose: {}, tie:{}".format(
                self.pure_mcts_playout_num,
                win_cnt[1], win_cnt[2], win_cnt[-1]))
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
                    self.policy_value_net.save_model('./current_policy.model')
                    if win_ratio > self.best_win_ratio:
                        print("New best policy!!!!!!!!")
                        self.best_win_ratio = win_ratio
                        # update the best_policy
                        self.policy_value_net.save_model('./best_policy.model')
                        if (self.best_win_ratio == 1.0 and
                                self.pure_mcts_playout_num < 5000):
                            self.pure_mcts_playout_num += 1000
                            self.best_win_ratio = 0.0
        except KeyboardInterrupt:
            print('\n\rquit')

