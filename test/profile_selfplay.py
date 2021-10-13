'''
Author: Zeng Siwei
Date: 2021-10-08 15:45:05
LastEditors: Zeng Siwei
LastEditTime: 2021-10-11 18:07:46
Description: 
'''

# from deepdraughts.env.cython_env import * # recommand, faster when playing with AI.
from deepdraughts.env.py_env import *
from deepdraughts.gui import GUI
from deepdraughts.game_collector import GameCollector
from deepdraughts.mcts_pure import MCTSPlayer as MCTS_pure
from deepdraughts.mcts_alphazero import MCTSPlayer_alphazero as MCTS_alphazero
from deepdraughts.net_pytorch import Model
import time
import datetime
from .test_game_collector import test_alphazero_selfplay, test_alphazero_selfplay


if __name__ == "__main__":
    import cProfile, pstats, io

    pr = cProfile.Profile()
    pr.enable()

    # profile function
    # test_pure_mcts_selfplay(1, 1)
    test_alphazero_selfplay(1, 1)

    pr.disable()

    dir_file = "./savedata/"
    filename = "selfplay_profile_1_1"
    now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filepath = dir_file + filename + "_" + now_time +".prof"
    pr.dump_stats(filepath)
    # to see visualization via pip: "flameprof selfplay.prof > selfplay.svg"
    # or invoke flameprof.py directly: "python flameprof.py selfplay.prof > profile.svg"
    # about: https://github.com/baverman/flameprof

    s = io.StringIO()
    sortby = "cumtime"  # 仅适用于 3.6, 3.7 把这里改成常量了
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    result = s.getvalue()
    print(result)

    filepath = dir_file + filename + "_" + now_time +".txt"
    # save it to disk
    with open(filepath, 'w') as f:
        f.write(result)
