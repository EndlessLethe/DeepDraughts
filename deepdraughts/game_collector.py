'''
Author: Zeng Siwei
Date: 2021-09-15 16:32:59
LastEditors: Zeng Siwei
LastEditTime: 2021-10-08 20:08:43
Description: 
'''

from .env import Game, game_status_to_str
import numpy as np
import pickle
import copy
import time


class GameCollector():
    @classmethod
    def self_play(cls, policy, temp=1e-3, game=None):
        """ start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (winner, game, states, mcts_probs, policy_grad) for training
        """
        np.random.seed()
        print("Start one game for self playing with random seed:", np.random.get_state()[1][:3])
        start_time = time.time()
        if game is None:
            game = Game()
        states, mcts_probs, current_players = [], [], []
        while True:
            move, move_probs = policy.get_action(game, temp=temp)
            # store the data
            states.append(game.to_vector())
            mcts_probs.append(move_probs)
            current_players.append(game.current_player)
            # perform a move
            game_status = game.do_move(move)
            end, winner = game.is_over()
            if end:
                end_time = time.time()
                print(game_status_to_str(game_status), 
                    "Using", end_time-start_time, "s")
                
                break

        policy_grad = np.zeros(len(current_players))
        if winner is not None:
            # winner from the perspective of the current player of each state
            current_players = np.array(current_players)
            policy_grad[current_players == winner] = 1.0
            policy_grad[current_players != winner] = -1.0

        # reset MCTS root node
        policy.reset()
        
        return winner, game, states, mcts_probs, policy_grad

    @classmethod
    def eval(cls, current_policy, eval_policy, i, temp = 1e-3, game_args=dict()):
        """
        Evaluate the trained policy by playing against the pure MCTS player
        Note: this is only for monitoring the progress of training
        """
        np.random.seed()
        print("Start one game for evaluation with random seed:", np.random.get_state()[1][:3])
        start_time = time.time()
        cnt_win, cnt_lose, cnt_draw = 0, 0, 0
        game = Game(**game_args)
        white_player = current_policy if i % 2 else eval_policy
        black_player = eval_policy if i % 2 else current_policy
        WHITE = game.current_player
        while True:
            current_player = white_player if game.current_player == WHITE else black_player
            move, _ = current_player.get_action(game, temp)
            game_status = game.do_move(move)
            is_over, winner = game.is_over()
            if is_over:
                end_time = time.time()
                print(game_status_to_str(game_status), 
                    "Using", end_time-start_time, "s")
                break
        if winner is None:
            cnt_draw += 1
        elif (winner == WHITE and white_player is current_policy) or (winner != WHITE and black_player is current_policy):
            cnt_win += 1
        elif (winner == WHITE and white_player is eval_policy) or (winner != WHITE and black_player is eval_policy):
            cnt_lose += 1
                
        return cnt_win, cnt_lose, cnt_draw

    @classmethod
    def parallel_eval(cls, current_policy, shared_model, eval_policy, n_cores, n_games, 
                    temp = 1e-3, game_args=dict()):
        import torch
        from torch.multiprocessing import Pool
        shared_model.share_memory()
        with torch.no_grad():
            pool = Pool(n_cores)
            pool_results = []
            
            for i in range(n_games):
                result = pool.apply_async(cls.eval, (current_policy, eval_policy, i, temp, game_args))
                pool_results.append(result)
            pool.close() 
            pool.join()
            results = [x.get() for x in pool_results]
            pool.close()

        cnt_win, cnt_lose, cnt_draw = 0, 0, 0
        for win, lose, draw in results:
            cnt_win += win
            cnt_lose += lose
            cnt_draw += draw
        win_ratio = 1.0*(cnt_win + 0.5*cnt_draw) / n_games
        print("win: {}, lose: {}, draw:{}".format(cnt_win, cnt_lose, cnt_draw))
        return win_ratio

    @classmethod
    def collect_selfplay(cls, policy, batch_size = 1000, temp = 1e-3, filepath = None, game = None):
        selfplay_data = []
        for i in range(batch_size):
            selfplay_data.append(cls.self_play(policy, temp))
        if filepath:
            cls.dump_selfplay(selfplay_data, filepath)
        return selfplay_data
    
    @classmethod
    def parallel_collect_selfplay(cls, n_cores, shared_model, policy, batch_size = 1000, temp = 1e-3, filepath = None, game = None):
        import torch
        from torch.multiprocessing import Pool
        if shared_model is not None:
            shared_model.share_memory()
        with torch.no_grad():
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
            pool.close()
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