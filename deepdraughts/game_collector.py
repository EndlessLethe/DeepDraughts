'''
Author: Zeng Siwei
Date: 2021-09-15 16:32:59
LastEditors: Zeng Siwei
LastEditTime: 2021-09-23 01:36:59
Description: 
'''


import numpy as np
import pickle
import copy

from .env import *

class GameCollector():
    @classmethod
    def self_play(cls, policy, temp=1e-3, game=None):
        """ start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (state, mcts_probs, z) for training
        """
        print("Start one game for self playing")
        if game is None:
            game = Game()
        states, mcts_probs, current_players = [], [], []
        while True:
            move, move_probs = policy.get_action(game, temp=temp)
            # store the data
            states.append(copy.deepcopy(game))
            mcts_probs.append(move_probs)
            current_players.append(game.current_player)
            # perform a move
            game.do_move(move)
            end, winner = game.is_over()
            if end:
                break

        policy_grad = np.zeros(len(current_players))
        if winner is not None:
            print("Game over." + "WHITE" if winner == WHITE else "BLACK" + "wins")

            # winner from the perspective of the current player of each state
            current_players = np.array(current_players)
            policy_grad[current_players == winner] = 1.0
            policy_grad[current_players != winner] = -1.0
        else:
            print("Game Draw")

        # reset MCTS root node
        policy.reset()
            
        return winner, states, mcts_probs, policy_grad

    @classmethod
    def collect_selfplay(cls, policy, batch_size = 1000, temp = 1e-3, filepath = None, game = None):
        selfplay_data = []
        for i in range(batch_size):
            selfplay_data.append(cls.self_play(policy, temp))
        if filepath:
            cls.dump_selfplay(selfplay_data, filepath)
        return selfplay_data
    
    @classmethod
    def parallel_collect_selfplay(cls, n_cores, policy, batch_size = 1000, temp = 1e-3, filepath = None, game = None):
        from torch.multiprocessing import Pool
        pool = Pool(n_cores)
        pool_results = []
        
        for i in range(batch_size):
            result = pool.apply_async(cls.self_play, (policy, temp))
            pool_results.append(result)
        pool.close() 
        pool.join()

        selfplay_data = [x.get() for x in pool_results]
        if filepath:
            cls.dump_selfplay(selfplay_data, filepath)
        return selfplay_data
            
    @classmethod
    def load_selfplay(cls, filepath):
        with open(filepath, "rb") as fp:
            selfplays = pickle.load(fp)
            return selfplays
    
    @classmethod
    def dump_selfplay(cls, selfplays, filepath):
        with open(filepath, "wb") as wfp:
            pickle.dump(selfplays, wfp)