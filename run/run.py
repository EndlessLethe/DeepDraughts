'''
Author: Zeng Siwei
Date: 2021-09-17 13:36:24
LastEditors: Zeng Siwei
LastEditTime: 2021-09-22 16:44:40
Description: 
'''

if __name__ == "__main__":
    from deepdraughts.env import *
    from deepdraughts.mcts_pure import MCTSPlayer as MCTS_Pure
    from deepdraughts.gui import GUI
    from deepdraughts.mcts_alphaZero import MCTSPlayer_AlphaZero as MCTS_AlphaZero
    from deepdraughts.net_pytorch import Model

    gui = GUI()
    # gui.run()

    # mcts_player = MCTS_Pure(c_puct=5, n_playout=1000)
    # gui.run(player_black=AI_PLAYER, policy_black=mcts_player)
    
    model = Model(N_SIZE_8, N_STATE_64, N_ACTION_64, MOVE_MAP_64)
    mcts_player = MCTS_AlphaZero(model.policy_value_fn, c_puct=5, n_playout=1000, selfplay=False)
    gui.run(player_black=AI_PLAYER, policy_black=mcts_player)
    