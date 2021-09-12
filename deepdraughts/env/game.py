'''
Author: Zeng Siwei
Date: 2021-09-11 16:20:41
LastEditors: Zeng Siwei
LastEditTime: 2021-09-13 00:43:31
Description: 
'''

from .board import Board, Move
from .env_utils import *
import copy

class Game():
    def __init__(self, player1_name = "player1", player2_name = "player2", ngrid = N_GRID_64, rule = RUSSIAN_RULE) -> None:
        self.move_path = []
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.current_board = Board(ngrid, rule)
        self.current_player = WHITE

        self.current_board.init_default_board()
        self.available_moves = None
        self.n_king_move = 0

    def reset_available_moves(self):
        self.available_moves = None

    def move(self, move):
        self.current_board.move(move)
        self.move_path.append((self.current_player, move))
        self.reset_available_moves()
        
        if move.move_type == MEN_MOVE:
            self.n_king_move = 0
        else:
            self.n_king_move += 1

        # check whether the player can take another piece after this move.
        king_jumps, jumps, _ = self.current_board.get_available_moves(move.moves[-1])
        can_take_piece = (len(king_jumps) + len(jumps)) >= 1
        if move.take_piece and can_take_piece:
            # 连吃 chain-taking
            pass
        else:
            self.change_player()

        if self.is_over():
            print("Game Over!")
            return GAME_OVER
        if self.is_drawn():
            print("Game Draw!")
            return GAME_DRAW
        return GAME_CONTINUE

    def is_over(self):
        available_moves = self.get_all_available_moves()
        if len(available_moves) == 0:
            return True
        else:
            return False

    def is_drawn(self):
        '''
        Here I just implement the only one basic rules about drawn:
        - If both players play 15 kingmoves (any king) without captures or moving men, the game is drawn.
        '''        
        if self.n_king_move >= 30:
            return True
        return False

    def get_all_available_moves(self):
        # TODO Brazilian rule 有多吃多
        if self.available_moves is not None:
            return self.available_moves

        king_jumps, jump_moves, normal_moves = self.current_board.get_all_available_moves(self.current_player)

        if len(king_jumps)  == 0:
            self.available_moves = jump_moves if len(jump_moves) >= 1 else normal_moves
            return self.available_moves

        # king jump must be carefully dealt when chain-taking
        chain_taking_jumps = []
        normal_jumps = []
        for king_jump in king_jumps:
            board_tmp = copy.deepcopy(self.current_board)
            board_tmp.move(king_jump)
            king_jumps, jump_moves, _ = board_tmp.get_available_moves(king_jump.moves[-1])
            can_take_piece = (len(king_jumps) + len(jump_moves)) >= 1
            if can_take_piece:
                chain_taking_jumps.append(king_jump)
            else:
                normal_jumps.append(king_jump)

        self.available_moves = chain_taking_jumps if len(chain_taking_jumps) >= 1 else normal_jumps
        return self.available_moves

    def change_player(self):
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        self.current_board.reset_available_moves()
        self.reset_available_moves()
        self.is_chain_taking = False

    '''

    IO functions.
            
    '''    

    def load_game(self, filepath):
        # TODO add guess_taken_piece() for read human files.
        with open(filepath, "r") as fp:
            str_moves = fp.readline().split(",")
            for str_move in str_moves:
                move = Move.init_by_str(str_move)
                print(str(move))

    def load_structured_game(self):
        # TODO
        pass
    
    # def  __repr__(self):
    #     # TODO
    #     pass

    def __str__(self):
        return ", ".join(str(x[1]) for x in self.move_path).strip(", ")
