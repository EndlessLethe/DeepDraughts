'''
Author: Zeng Siwei
Date: 2021-09-17 23:52:20
LastEditors: Zeng Siwei
LastEditTime: 2021-09-18 00:35:36
Description: 
'''

from deepdraughts.gui import GUI
from deepdraughts.game_collector import GameCollector
from deepdraughts.mcts_pure import MCTSPlayer as MCTS_Pure
from deepdraughts.env.env_utils import *
import time
    
def test_state2vec():
    dir_file = "deepdraughts/savedata/"
    gc = GameCollector()
    datas = gc.load_selfplay(dir_file + "selfplay1.pkl")
    
    # datas = [datas[2]]
    for winner, states, mcts_probs, policy_grad in datas:
        for game in states:
            vec_board, vec_state = state2vec(game)
            print(vec_board)
            print(vec_state)
        break


def test_actions2vec():
    pass

if __name__ == "__main__":
    test_state2vec()
    