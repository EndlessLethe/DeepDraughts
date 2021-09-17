'''
Author: Zeng Siwei
Date: 2021-09-15 23:02:07
LastEditors: Zeng Siwei
LastEditTime: 2021-09-17 13:43:06
Description: 
'''

from deepdraughts.gui import GUI
from deepdraughts.game_collector import GameCollector
from deepdraughts.mcts_pure import MCTSPlayer as MCTS_Pure
import time
    

def test_selfplay():
    dir_file = "deepdraughts/savedata/"

    gc = GameCollector()
    mcts_player = MCTS_Pure(c_puct=5, n_playout=1000)
    
    # start_time = time.time()
    # gc.collect_selfplay(mcts_player, batch_size, filepath= dir_file + "selfplay1.pkl")
    # end_time = time.time()
    # print("Non parallel " + str(batch_size) + " selfplay:", end_time-start_time, "s")
    # # Non parallel 2 selfplay: 388.1669747829437 s

    start_time = time.time()
    gc.parallel_collect_selfplay(n_core = 8, policy = mcts_player, batch_size = 20, filepath = dir_file + "selfplay1.pkl")
    end_time = time.time()
    print("Paralleled " + str(10) + " selfplay with " + str(8) + " core:", end_time-start_time, "s")
    # Paralleled 10 selfplay with 5 core: 1021.0484848022461 s
    # Paralleled 10 selfplay with 8 core: 822.6482546329498 s
    # Paralleled 10 selfplay with 8 core: 1561.856823682785 s

def test_reading():
    dir_file = "deepdraughts/savedata/"
    gc = GameCollector()
    datas = gc.load_selfplay(dir_file + "selfplay1.pkl")
    
    
    # datas = [datas[2]]
    for winner, game, states, mcts_probs, policy_grad in datas:
        gui = GUI()
        print(winner)
        print(game)
        # print(states)
        print(mcts_probs)
        print(policy_grad)
        gui.replay(game)



if __name__ == "__main__":
    # test_selfplay()
    test_reading()
    
    