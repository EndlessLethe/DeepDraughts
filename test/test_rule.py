'''
Author: Zeng Siwei
Date: 2021-09-15 23:01:04
LastEditors: Zeng Siwei
LastEditTime: 2021-09-15 23:01:05
Description: 
'''

def test_rule_cannot_jump_over_twice():
    gui = GUI()
    gui.game.current_board.init_empty_board()
    gui.game.current_board.set_board([13, 18, 45], [6], blacks_isking=[True])
    gui.run()