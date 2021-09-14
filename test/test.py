'''
Author: Zeng Siwei
Date: 2021-09-12 23:33:09
LastEditors: Zeng Siwei
LastEditTime: 2021-09-15 00:42:57
Description: 
'''

from deepdraughts.env.game import Game
from deepdraughts.gui import GUI

def test_load_game():
    game = Game()
    filepath = "F:/Projects/dramaster/deepdraughts/savedata/1.txt"
    game.load_game(filepath)

def test_rule_cannot_jump_over_twice():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([13, 18, 45], [6], blacks_isking=[True])
    gui.run()