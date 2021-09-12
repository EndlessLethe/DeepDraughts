'''
Author: Zeng Siwei
Date: 2021-09-11 16:20:41
LastEditors: Zeng Siwei
LastEditTime: 2021-09-12 19:28:56
Description: 
'''

from .board import Board
from .env_utils import *

class Game():
    def __init__(self, player1_name = "player1", player2_name = "player2", ngrid = N_GRID_64, rule = RUSSIAN_RULE) -> None:
        self.state_path = []
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.current_board = Board(ngrid, rule)
        self.current_player = WHITE

    def move(self, pos_from, pos_to, take_piece = False):
        last_move = self.current_board.move(pos_from, pos_to, take_piece)
        self.state_path.append((self.current_player, last_move))
        
        jump_moves, _ = self.current_board.get_available_moves(pos_to)
        can_take_piece = len(jump_moves) >= 1
        if take_piece and can_take_piece:
            # 连吃 chain-take
            pass
        else:
            self.change_player()

    def change_player(self):
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        self.current_board.reset_available_moves()
