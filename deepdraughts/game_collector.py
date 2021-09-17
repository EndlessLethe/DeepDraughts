'''
Author: Zeng Siwei
Date: 2021-09-15 16:32:59
LastEditors: Zeng Siwei
LastEditTime: 2021-09-17 12:56:27
Description: 
'''

from .env.game import Game
import numpy as np
import pickle
from .env.env_utils import *
import copy

class GameCollector():
    def self_play(self, policy, temp=1e-3):
        """ start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (state, mcts_probs, z) for training
        """
        print("Start one game for self playing")
        game = Game()
        states, mcts_probs, current_players = [], [], []
        while True:
            # move, move_probs = policy.get_action(game, temp=temp)
            move, move_probs = policy.get_action(game)
            # store the data
            states.append(game.current_board)
            mcts_probs.append(move_probs)
            current_players.append(game.current_player)
            # perform a move
            game.do_move(move)
            end, winner = game.is_over()
            if end:
                break

        policy_grad = np.zeros(len(current_players))
        if winner is not None:
            print("Game over.", "WHITE" if winner == WHITE else "BLACK", "wins")

            # winner from the perspective of the current player of each state
            current_players = np.array(current_players)
            policy_grad[current_players == winner] = 1.0
            policy_grad[current_players != winner] = -1.0
        else:
            print("Game Draw")

        # reset MCTS root node
        policy.reset()
            
        return winner, game, states, mcts_probs, policy_grad

    def collect_selfplay(self, policy, batch_size = 1000, temp = 1e-3, filepath = None):
        selfplay_data = []
        for i in range(batch_size):
            selfplay_data.append(self.self_play(policy, temp))
        if filepath:
            self.dump_selfplay(selfplay_data, filepath)
        return selfplay_data
    
    def parallel_collect_selfplay(self, n_core, policy, batch_size = 1000, temp = 1e-3, filepath = None):
        from  multiprocessing import Pool
        pool = Pool(n_core)
        pool_results = []
        
        for i in range(batch_size):
            result = pool.apply_async(self.self_play, (policy, temp))
            pool_results.append(result)
        pool.close() 
        pool.join()

        selfplay_data = [x.get() for x in pool_results]
        if filepath:
            self.dump_selfplay(selfplay_data, filepath)
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