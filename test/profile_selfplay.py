'''
Author: Zeng Siwei
Date: 2021-10-08 15:45:05
LastEditors: Zeng Siwei
LastEditTime: 2021-10-08 17:11:19
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

def test_pure_mcts_selfplay(n_cores = 8, batch_size = 20, filename = "pure_mcts_selfplay"):
    dir_file = "./savedata/"
    now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filepath = dir_file + filename + "_" + now_time +".pkl"

    gc = GameCollector()
    mcts_player = MCTS_pure(c_puct=5, n_playout=1000)

    start_time = time.time()
    if n_cores == 1:
        gc.collect_selfplay(mcts_player, batch_size, filepath=filepath)
    else:
        gc.parallel_collect_selfplay(n_cores = n_cores, shared_model = None, policy = mcts_player, batch_size = batch_size, filepath = filepath)
    end_time = time.time()
    print("Paralleled " + str(batch_size) + " selfplay with " + str(n_cores) + " core:", end_time-start_time, "s")


def test_alphazero_selfplay(filename = "alphazero_selfplay"):
    dir_file = "./savedata/"
    now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filepath = dir_file + filename + "_" + now_time +".pkl"

    gc = GameCollector()
    env_args = get_env_args()
    model = Model(env_args, use_gpu=False)
    mcts_player = MCTS_alphazero(model.policy_value_fn, c_puct=5, n_playout=1000, selfplay=True)

    batch_size = 20
    n_cores = 8
    start_time = time.time()
    gc.parallel_collect_selfplay(n_cores = n_cores, shared_model = model.policy_value_net, policy = mcts_player, batch_size = batch_size, filepath = filepath)
    end_time = time.time()
    print("Paralleled " + str(batch_size) + " selfplay with " + str(n_cores) + " core:", end_time-start_time, "s")

if __name__ == "__main__":
    import cProfile, pstats, io

    pr = cProfile.Profile()
    pr.enable()

    # profile function
    test_pure_mcts_selfplay(1, 1)

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
