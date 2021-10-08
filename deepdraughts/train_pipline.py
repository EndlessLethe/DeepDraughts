# -*- coding: utf-8 -*-
"""
An implementation of the training pipeline of AlphaZero for Gomoku

@author: Junxiao Song
"""

from __future__ import print_function
from deepdraughts.env.py_env.env_utils import game_status_to_str
import random
import numpy as np
from collections import defaultdict
from tensorboardX import SummaryWriter

import datetime
from .mcts_pure import MCTSPlayer as MCTS_pure
from .mcts_alphazero import MCTSPlayer_alphazero as mcts_alphazero
from .game_collector import GameCollector
from .env import Game

class TrainPipeline():
    def __init__(self, model, dir_save, config, game_args = dict()):
        self.max_epoch = config.getint("training_args", "max_epoch")
        self.batch_size = config.getint("training_args", "batch_size")  # mini-batch size for training
        self.n_cores = config.getint("training_args", "n_cores") # number of cores for
        self.epochs = config.getint("training_args", "epochs")  # num of train_steps for each update
        self.check_freq = config.getint("training_args", "check_freq")
        self.n_eval_games = config.getint("training_args", "n_eval_games")

        self.learn_rate =config.getfloat("training_args", "learn_rate")
        self.lr_multiplier = config.getfloat("training_args", "lr_multiplier")  # adaptively adjust the learning rate based on KL
        self.temp = config.getfloat("training_args", "temp")  # the temperature param
        self.n_playout = config.getint("training_args", "n_playout")  # num of simulations for each move
        self.n_playout_pure_mcts = config.getint("training_args", "n_playout_pure_mcts") # num of pure MCTS eval simulations
        self.c_puct = config.getfloat("training_args", "c_puct")
        self.kl_targ = config.getfloat("training_args", "kl_targ")
        
        self.game_args = game_args
        self.game = Game(**game_args)
        self.model = model
        self.dir_save = dir_save
        self.name = model.name
        self.game_collector = GameCollector()
        self.n_epoch = 0
        self.best_win_ratio = 0.0
    
        self.mcts_player = mcts_alphazero(self.model.policy_value_fn,
                                      c_puct=self.c_puct,
                                      n_playout=self.n_playout,
                                      selfplay=True)
        self.writer = SummaryWriter(self.dir_save + self.name + "_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))


    def train(self):
        now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filepath = self.dir_save+self.name+"_gamebatch"+str(self.n_epoch)+"_"+str(now_time)+".pkl"
        plays = self.game_collector.parallel_collect_selfplay(n_cores = self.n_cores, 
                shared_model = self.model.policy_value_net, policy = self.mcts_player, batch_size = self.batch_size, filepath = filepath)
        
        _, _, state_batch_tmp, mcts_probs_batch_tmp, policy_grad_batch = zip(*plays)
        state_vecs_batch = []
        mcts_probs_batch = []
        for state_vecs, mcts_probs in zip(state_batch_tmp, mcts_probs_batch_tmp):
            state_vecs_batch.extend(state_vecs)
            mcts_probs_batch.append(np.array(mcts_probs))
        mcts_probs_batch = np.concatenate(mcts_probs_batch, axis=0)
        policy_grad_batch = np.concatenate(policy_grad_batch, axis=0)
        # print(len(state_batch), mcts_probs_batch.shape, policy_grad_batch.shape)
        assert len(state_vecs_batch) == mcts_probs_batch.shape[0]
        assert len(state_vecs_batch) == policy_grad_batch.shape[0]

        vec_board_batch = np.stack((x[0] for x in state_vecs_batch), axis=0)
        vec_state_batch = np.stack((x[1] for x in state_vecs_batch), axis=0)
        state_batch = (vec_board_batch, vec_state_batch)

        old_probs, old_v = self.model.policy_value_batch(state_batch)
        for i in range(self.epochs):
            loss, entropy = self.model.train_step(
                    state_batch,
                    mcts_probs_batch,
                    policy_grad_batch,
                    self.learn_rate*self.lr_multiplier)
            new_probs, new_v = self.model.policy_value_batch(state_batch)
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
        self.writer.add_scalar("loss", loss, self.n_epoch)
        self.writer.add_scalar("entropy", entropy, self.n_epoch)
        self.writer.add_scalar("kl_between_probs", kl, self.n_epoch)
        self.writer.add_scalar("lr_multiplier", self.lr_multiplier, self.n_epoch)
        self.writer.add_scalar("explained_var_old", explained_var_old, self.n_epoch)
        return loss, entropy

    def run(self):
        """run the training pipeline"""
        for i in range(self.max_epoch):
            self.n_epoch += 1
            print("New epoch:", self.n_epoch)
            loss, entropy = self.train()
            # check the performance of the current model,
            # and save the model params
            if (i+1) % self.check_freq == 0:
                print("Start evaluation.")
                current_mcts_player = mcts_alphazero(self.model.policy_value_fn, 
                    c_puct=self.c_puct, n_playout=self.n_playout, selfplay=False)
                pure_mcts_player = MCTS_pure(c_puct=self.c_puct, n_playout=self.n_playout_pure_mcts)
                win_ratio = self.game_collector.parallel_eval(current_mcts_player, 
                    self.model.policy_value_net, pure_mcts_player, self.n_cores, 
                    self.n_eval_games, self.temp, self.game_args)
                self.model.save(self.dir_save, self.n_epoch)
                print("win ratio:", win_ratio, "#games:", 
                    self.n_eval_games, "#pure mcts playout", self.n_playout_pure_mcts)
                if win_ratio > self.best_win_ratio:
                    print("New best model!")
                    self.best_win_ratio = win_ratio
                    self.model.save(self.dir_save, self.n_epoch, is_best=True)
                    if (self.best_win_ratio == 1.0 and self.n_playout_pure_mcts < 10000):
                        self.n_playout_pure_mcts += 1000
                        self.best_win_ratio = 0.0

