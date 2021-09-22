'''
Author: Zeng Siwei
Date: 2021-09-15 23:02:07
LastEditors: Zeng Siwei
LastEditTime: 2021-09-23 01:45:51
Description: 
'''

from logging import log

from torch import multiprocessing
from deepdraughts.env import *
from deepdraughts.gui import GUI
from deepdraughts.game_collector import GameCollector
from deepdraughts.mcts_pure import MCTSPlayer as MCTS_Pure
from deepdraughts.mcts_alphaZero import MCTSPlayer_AlphaZero as MCTS_AlphaZero
from deepdraughts.net_pytorch import Model
import time
import torch
    

def test_pure_mcts_selfplay(filename):
    dir_file = "deepdraughts/savedata/"

    gc = GameCollector()
    
    mcts_player = MCTS_Pure(c_puct=5, n_playout=1000)
    # start_time = time.time()
    # gc.collect_selfplay(mcts_player, batch_size, filepath= dir_file + "selfplay1.pkl")
    # end_time = time.time()
    # print("Non parallel " + str(batch_size) + " selfplay:", end_time-start_time, "s")
    # # Non parallel 2 selfplay: 388.1669747829437 s

    start_time = time.time()
    gc.parallel_collect_selfplay(n_core = 8, policy = mcts_player, batch_size = 20, filepath = dir_file + filename + ".pkl")
    end_time = time.time()
    print("Paralleled " + str(20) + " selfplay with " + str(8) + " core:", end_time-start_time, "s")
    # Paralleled 20 selfplay with 8 core: 1189.294320821762 s
    # Paralleled 20 selfplay with 8 core: 952.8826515674591 s
    # Paralleled 20 selfplay with 8 core: 1013.8065795898438 s using cython


def test_alphazero_selfplay(filename):
    dir_file = "deepdraughts/savedata/"
    
    gc = GameCollector()
    model = Model(N_SIZE_8, N_STATE_64, N_ACTION_64, MOVE_MAP_64, use_gpu=True)
    mcts_player = MCTS_AlphaZero(model.policy_value_fn, c_puct=5, n_playout=1000, selfplay=True)

    # batch_size = 1
    # start_time = time.time()
    # with torch.no_grad():
    #     gc.collect_selfplay(mcts_player, batch_size, filepath= dir_file + filename + ".pkl")
    # end_time = time.time()
    # print("Non parallel " + str(batch_size) + " selfplay:", end_time-start_time, "s")
    # Non parallel 2 selfplay: 922.9081609249115 s
    # Non parallel 1 selfplay: 486.6477029323578 s
    # Non parallel 1 selfplay: 455.86457991600037 s using cython
    # Non parallel 1 selfplay: 304.20654487609863 s using gpu

    batch_size = 20
    n_cores = 4
    start_time = time.time()
    with torch.no_grad():
        model.policy_value_net.share_memory()
        gc.parallel_collect_selfplay(n_cores = n_cores, policy = mcts_player, batch_size = batch_size, filepath = dir_file + filename + ".pkl")
    end_time = time.time()
    print("Paralleled " + str(batch_size) + " selfplay with " + str(n_cores) + " core:", end_time-start_time, "s")
    # Paralleled 20 selfplay with 8 core: 2545.431615114212 s

def test_load_selfplay():
    dir_file = "deepdraughts/savedata/"
    gc = GameCollector()
    datas = gc.load_selfplay(dir_file + "test_selfplay1.pkl")
    
    # datas = [datas[2]]
    for winner, states, mcts_probs, policy_grad in datas:
        print(winner)
        # print(states)
        print(mcts_probs)
        print(policy_grad)

        gui = GUI()
        gui.replay(states[-1])

        # for game in states:
        #     gui = GUI()
        #     gui.replay(game)
        # break



if __name__ == "__main__": 
    # test_pure_mcts_selfplay("test_selfplay1.pkl")    

    # torch.multiprocessing.set_start_method("spawn")
    test_alphazero_selfplay("test_selfplay2")
    # test_load_selfplay()
    
    