'''
Author: Zeng Siwei
Date: 2021-09-17 13:36:24
LastEditors: Zeng Siwei
LastEditTime: 2021-09-24 01:06:31
Description: 
'''

from deepdraughts.env import *
from deepdraughts.mcts_pure import MCTSPlayer as MCTS_pure
from deepdraughts.gui import GUI
from deepdraughts.mcts_alphaZero import MCTSPlayer_alphazero as MCTS_alphazero
from deepdraughts.net_pytorch import Model
from configobj import ConfigObj

def run_human_play():
    play_with_human()

def run_train_pipline():
    checkpoint_dir = "deepdraughts/savedata/"
    env_args = get_env_args()
    model = Model(env_args, name = "test_run")
    training_pipeline = TrainPipeline(model, checkpoint_dir)
    training_pipeline.run()

def play_with_human():
    gui = GUI()
    gui.run()

def play_with_alphazero(start_with_white = True, name = "default", use_gpu = False, checkpoint = ""):
    gui = GUI()
    if not checkpoint:
        model = Model(env_args, name = name, use_gpu = use_gpu)
    else:
        model = Model.load(checkpoint)
    
    mcts_player = MCTS_alphazero(model.policy_value_fn, c_puct=5, n_playout=1000, selfplay=False)
    if start_with_white:
        gui.run(player_black=AI_PLAYER, policy_black=mcts_player)
    else:
        gui.run(player_white=AI_PLAYER, policy_white=mcts_player)

def play_with_pureMCTS(start_with_white = True):
    gui = GUI()
    mcts_player = MCTS_Pure(c_puct=5, n_playout=1600)
    if start_with_white:
        gui.run(player_black=AI_PLAYER, policy_black=mcts_player)
    else:
        gui.run(player_white=AI_PLAYER, policy_white=mcts_player)



if __name__ == "__main__":
    conf_ini = "./config.ini"
    config = ConfigObj(conf_ini, encoding='UTF8')
    print(config)
    # run_human_play()

    