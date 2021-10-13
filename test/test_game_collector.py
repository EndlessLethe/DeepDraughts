'''
Author: Zeng Siwei
Date: 2021-09-15 23:02:07
LastEditors: Zeng Siwei
LastEditTime: 2021-10-12 17:14:18
Description: 
'''

from logging import log

from deepdraughts.env import *
from deepdraughts.gui import GUI
from deepdraughts.game_collector import GameCollector
from deepdraughts.mcts_pure import MCTSPlayer as MCTS_pure
from deepdraughts.mcts_alphazero import MCTSPlayer_alphazero as MCTS_alphazero
from deepdraughts.net_pytorch import Model
import time
import datetime


def test_pure_mcts_selfplay(n_cores = 8, batch_size = 20, filename = "pure_mcts_selfplay"):
    dir_file = "./savedata/"
    now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filepath = dir_file + filename + "_" + now_time +".pkl"

    gc = GameCollector()
    mcts_player = MCTS_pure(c_puct=5, n_playout=1000)

    start_time = time.time()
    if n_cores == 1:
        gc.collect_selfplay(mcts_player, batch_size, filepath=filepath)
        # repeat 10 time, avg time: 64.95348958969116 version: stable1.1
    else:
        gc.parallel_collect_selfplay(n_cores = n_cores, shared_model = None, policy = mcts_player, batch_size = batch_size, filepath = filepath)
        # repeat 3 time (8c20b), avg time: 357.5275936126709 version: stable1.1
    end_time = time.time()
    print("Paralleled " + str(batch_size) + " selfplay with " + str(n_cores) + " core:", end_time-start_time, "s")
    return end_time-start_time

def test_alphazero_selfplay(n_cores = 8, batch_size = 20, filename = "alphazero_selfplay"):
    dir_file = "./savedata/"
    now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filepath = dir_file + filename + "_" + now_time +".pkl"

    gc = GameCollector()
    env_args = get_env_args()
    model = Model(env_args, use_gpu=False)
    mcts_player = MCTS_alphazero(model.policy_value_fn, c_puct=5, n_playout=1000, selfplay=True)

    start_time = time.time()
    if n_cores == 1:
        gc.collect_selfplay(mcts_player, batch_size, filepath=filepath)
        # repeat 10 time, avg time: 241.05693390369416 version: stable1.1
    else:
        gc.parallel_collect_selfplay(n_cores = n_cores, shared_model = model.policy_value_net, policy = mcts_player, batch_size = batch_size, filepath = filepath)
        # repeat 3 time (8c20b), avg time: 1725.8509844144185 version: stable1.1

    end_time = time.time()
    print("Paralleled " + str(batch_size) + " selfplay with " + str(n_cores) + " core:", end_time-start_time, "s")
    return end_time-start_time


def test_load_selfplay(filepath):
    gc = GameCollector()
    datas = gc.load_selfplay(filepath)
    
    # datas = [datas[2]]
    for winner, game, states, mcts_probs, policy_grad in datas:
        print(winner)
        # print(states)
        print(mcts_probs)
        print(policy_grad)

        gui = GUI()
        gui.replay(game)

def test_eval():
    dir_file = "./savedata/"

    gc = GameCollector()
    env_args = get_env_args()
    model = Model(env_args, use_gpu=False)
    current_policy = MCTS_alphazero(model.policy_value_fn, c_puct=5, n_playout=1000, selfplay=False)
    eval_policy = MCTS_pure(c_puct=5, n_playout=1600)
    win_ratio = gc.parallel_eval(current_policy, model.policy_value_net, eval_policy, 8, 10)
    print(win_ratio)

if __name__ == "__main__": 
    dir_file = "./savedata/"
    # torch.multiprocessing.set_start_method("spawn")

    # total_time = 0
    # for i in range(3):
    #     # total_time += test_pure_mcts_selfplay(8, 20)
    #     total_time += test_alphazero_selfplay(8, 20)
    # print(total_time, total_time/3)

    # test_pure_mcts_selfplay(1, 1)
    test_alphazero_selfplay(8, 20)
    # test_load_selfplay(dir_file+"alphazero_selfplay_20211012_1705.pkl")
    # test_eval()