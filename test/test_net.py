'''
Author: Zeng Siwei
Date: 2021-09-17 23:52:20
LastEditors: Zeng Siwei
LastEditTime: 2021-09-24 13:13:50
Description: 
'''

from deepdraughts.gui import GUI
from deepdraughts.game_collector import GameCollector
from deepdraughts.mcts_pure import MCTSPlayer as MCTS_pure
from deepdraughts.mcts_alphazero import MCTSPlayer_alphazero as MCTS_AlphaZero
from deepdraughts.net_pytorch import Model
from deepdraughts.env import *
import time
    
def test_state2vec():
    dir_file = "./savedata/"
    gc = GameCollector()
    datas = gc.load_selfplay(dir_file + "selfplay1.pkl")
    
    # datas = [datas[2]]
    for winner, states, mcts_probs, policy_grad in datas:
        for game in states:
            vec_board, vec_state = state2vec(game)
            print(vec_board)
            print(vec_state)
        break


def test_init_model():
    gui = GUI()
    env_args = get_env_args()
    model = Model(env_args, use_gpu=False)
    mcts_player = MCTS_AlphaZero(model.policy_value_fn, c_puct=5, n_playout=1000, inference=True)
    gui.run(player_black=AI_PLAYER, policy_black=mcts_player)

def test_save_model():
    checkpoint_dir = "./savedata/"
    env_args = get_env_args()
    model = Model(env_args, name="test", use_gpu=False)
    model.save(checkpoint_dir, 0)

def test_load_model():
    checkpoint_dir = "./savedata/"
    model = Model.load_checkpoint(model_file=checkpoint_dir+"test_0.pth.tar")
    print(model.checkpoint_n_epoch)
    gui = GUI()
    mcts_player = MCTS_AlphaZero(model.policy_value_fn, c_puct=5, n_playout=1000, inference=True)
    gui.run(player_black=AI_PLAYER, policy_black=mcts_player)

if __name__ == "__main__":
    # test_state2vec()
    test_save_model()
    # test_load_model()
    