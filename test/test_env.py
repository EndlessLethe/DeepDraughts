'''
Author: Zeng Siwei
Date: 2021-09-15 23:01:04
LastEditors: Zeng Siwei
LastEditTime: 2021-10-13 23:48:40
Description: 
'''

from deepdraughts.gui import GUI
from deepdraughts.env import *

def test_rule_cannot_jump_over_twice1():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([12, 17, 44], [6], blacks_isking=[True])
    gui.game.change_player()
    gui.run()

def test_rule_cannot_jump_over_twice2():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([26, 46, 42, 28], [39], blacks_isking=[True])
    gui.game.change_player()
    gui.run()

def test_rule_cannot_jump_over_twice3():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([26, 46, 42, 28], [39], blacks_isking=[True])
    gui.game.change_player()
    gui.run()

def test_load_fen():
    FEN_6 = "W:WA1,C3:BD4"
    game = Game.load_fen(FEN_6)
    print(game.current_player)

    gui = GUI()
    gui.game = Game.load_fen(FEN_6)
    gui.run()

def test_to_fen():
    FEN_6 = "W:WA1,C3:BD4"
    game = Game.load_fen(FEN_6)
    print(game.to_fen())

    FEN_6 = "W:WA1,C3:BD4.0"
    game = Game.load_fen(FEN_6)
    print(game.to_fen())

    FEN_6 = "W:WA1,C3:BD4.1C5"
    game = Game.load_fen(FEN_6)
    print(game.to_fen())


if __name__ == "__main__":
    # test_rule_cannot_jump_over_twice3()
    # test_load_fen()
    test_to_fen()