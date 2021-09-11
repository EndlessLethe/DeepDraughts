'''
Author: Zeng Siwei
Date: 2021-09-11 16:20:41
LastEditors: Zeng Siwei
LastEditTime: 2021-09-12 00:16:44
Description: 
'''
from board import Board

class Game():
    def __init__(self, player1_name = "player1", player2_name = "player2") -> None:
        self.state_path = []
        self.current_board = Board()
        self.player1_name = player1_name
        self.player2_name = player2_name

    def move(self, pos_from, pos_to, take_piece = False):
        last_move = self.current_board.move(pos_from, pos_to, take_piece)
        self.state_path.append(last_move)
