'''
Author: Zeng Siwei
Date: 2021-09-15 23:01:04
LastEditors: Zeng Siwei
LastEditTime: 2021-10-11 11:06:55
Description: 
'''

from deepdraughts.gui import GUI

def test_rule_cannot_jump_over_twice1():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([13, 18, 45], [6], blacks_isking=[True])
    gui.game.change_player()
    gui.run()

def test_rule_cannot_jump_over_twice2():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([27, 47, 43, 29], [40], blacks_isking=[True])
    gui.game.change_player()
    gui.run()

def test_rule_cannot_jump_over_twice3():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([27, 47, 43, 38], [40], blacks_isking=[True])
    gui.game.change_player()
    gui.run()

if __name__ == "__main__":
    test_rule_cannot_jump_over_twice3()