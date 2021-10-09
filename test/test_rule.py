'''
Author: Zeng Siwei
Date: 2021-09-15 23:01:04
LastEditors: Zeng Siwei
LastEditTime: 2021-10-09 19:49:42
Description: 
'''

from deepdraughts.gui import GUI

def test_rule_cannot_jump_over_twice():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([13, 18, 45], [6], blacks_isking=[True])
    gui.run()

if __name__ == "__main__":
    test_rule_cannot_jump_over_twice()