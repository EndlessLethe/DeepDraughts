'''
Author: Zeng Siwei
Date: 2021-09-12 23:33:09
LastEditors: Zeng Siwei
LastEditTime: 2021-09-15 23:02:14
Description: 
'''

from deepdraughts.env.game import Game
from deepdraughts.gui import GUI

def test_load_game():
    game = Game()
    filepath = "F:/Projects/dramaster/deepdraughts/savedata/1.txt"
    game.load_game(filepath)
