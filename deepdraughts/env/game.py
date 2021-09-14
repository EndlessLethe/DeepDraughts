'''
Author: Zeng Siwei
Date: 2021-09-11 16:20:41
LastEditors: Zeng Siwei
LastEditTime: 2021-09-14 23:51:12
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

        self.is_chain_taking = False
        self.chain_taking_pos = []

    def reset_available_moves(self):
        self.available_moves = None

    def reset_chain_taking_states(self):
        self.is_chain_taking = False
        self.chain_taking_pos = []

    def do_move(self, move):
        self.current_board.do_move(move)
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
            self.is_chain_taking = True
            self.chain_taking_pos = [move.moves[-2], move.moves[-1]]
        else:
            self.change_player()
            self.reset_chain_taking_states()

        is_over, winner = self.is_over()
        if is_over:
            return GAME_WHITE_WIN if winner == WHITE else GAME_BLACK_WIN
        if self.is_drawn():
            return GAME_DRAW
        return GAME_CONTINUE

    def is_over(self):
        available_moves = self.get_all_available_moves()
        if len(available_moves) == 0:
            return True, WHITE if self.current_player == BLACK else BLACK
        else:
            return False, None

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
        # TODO 不能跳过同一个棋子两次
        if self.available_moves is not None:
            return self.available_moves

        if self.is_chain_taking:
            king_jumps, jump_moves, _ = self.current_board.get_available_moves(self.chain_taking_pos[-1])
            
            # check whether go over the same piece
            # 1. whether the opposite direction. if false, it's ok
            # 2. if true, whether the pos is mono. if true, it's ok
            # 3. if false, remove this move

        else:
            king_jumps, jump_moves, normal_moves = self.current_board.get_all_available_moves(self.current_player)

        if len(king_jumps)  == 0:
            self.available_moves = jump_moves if len(jump_moves) >= 1 else normal_moves
            return self.available_moves

        # king jump must be carefully dealt when chain-taking:
        # if king can take a piece, and after this move another piece can be taken,
        # only continueing chain-taking is available.
        king_chain_takings = []
        king_normal_jumps = []
        for king_jump in king_jumps:
            board_tmp = copy.deepcopy(self.current_board)
            board_tmp.do_move(king_jump)
            tmp_king_jumps, tmp_jump_moves, _ = board_tmp.get_available_moves(king_jump.moves[-1])
            can_take_piece = (len(tmp_king_jumps) + len(tmp_jump_moves)) >= 1
            if can_take_piece:
                king_chain_takings.append(king_jump)
            else:
                king_normal_jumps.append(king_jump)

        self.available_moves = king_chain_takings if len(king_chain_takings) >= 1 else king_normal_jumps
        self.available_moves.extend(jump_moves)
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
