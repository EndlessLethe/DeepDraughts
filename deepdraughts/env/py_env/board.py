'''
Author: Zeng Siwei
Date: 2021-09-11 14:36:26
LastEditors: Zeng Siwei
LastEditTime: 2021-10-13 19:13:00
Description: 
'''

from .env_utils import *
from .piece import Piece

class Board():
    def __init__(self, ngrid = CONST_N_GRID_64, rule = RUSSIAN_RULE) -> None:
        self.pieces = dict() # key - value: pos - piece
        self.ngrid = ngrid
        self.rule = rule

        # no need caching moves
        self.piece_moves = dict()

        import math
        n = int(math.sqrt(ngrid))
        if n * n != ngrid:
            raise Exception("N_grid is not squre number.")
        self.nsize = n

    '''
    Update board
    '''    
    def reset_available_moves(self):
        self.piece_moves.clear()

    def set_board(self, whites_pos, blacks_pos, whites_isking = None, blacks_isking = None):
        '''
        Input must be computer index. See more details in env_utils.py

        Usage:
            whites_pos = norm_pos_list(whites_pos)
            blacks_pos = norm_pos_list(blacks_pos)
            set_board(whites_pos, blacks_pos)
        '''        
        if (self.check_pos_list(whites_pos) and self.check_pos_list(blacks_pos)) == False:
            raise Exception("Invaid pos list.")
        self.init_empty_board()
        if whites_isking is None:
            whites_isking = [False] * len(whites_pos)
        if blacks_isking is None:
            blacks_isking = [False] * len(blacks_pos)

        for pos, isking in zip(whites_pos, whites_isking):
            self.pieces[pos] = Piece(WHITE, pos, isking, *KING_PROMOTION_POS())
        for pos, isking in zip(blacks_pos, blacks_isking):
            self.pieces[pos] = Piece(BLACK, pos, isking, *KING_PROMOTION_POS())
        self.reset_available_moves()

    def init_empty_board(self):
        self.pieces.clear()
        self.reset_available_moves()

    def init_default_board(self):
        self.set_board(*DEFAULT_POS())

    def check_pos_list(self, pos_list):
        is_ok = True
        for pos in pos_list:
            if pos not in VALID_POS():
                x, y = pos2coord(pos, self.ngrid)
                print("Invalid pos:", pos, "row:", x, "col:", y)
                is_ok = False
        return is_ok

    
    def do_move(self, move):
        self.move(move.pos[-2], move.pos[-1], move.taken_pos)

    def move(self, pos_from, pos_to, taken_pos = None):
        '''
        Move the piece in pos_from to pos_to.
        '''
        if pos_from not in self.pieces or pos_to in self.pieces:
            raise Exception("Invalid move operation. From", pos_from, "to", pos_to)
        piece = self.pieces.pop(pos_from)
        piece.move_to(pos_to)
        self.pieces[pos_to] = piece
        if taken_pos is not None:
            self.pieces.pop(taken_pos)
        self.reset_available_moves()


    '''
    Querying states
    '''    
    def number_of_pieces(self):
        return len(self.pieces)

    def get_pieces(self):
        return [x for x in self.pieces.values()]

    def get_available_moves(self, pos):
        if pos in self.piece_moves:
            return self.piece_moves[pos]
        
        king_jump_moves = []
        jump_moves = []
        normal_moves = []

        piece = self.pieces[pos]
        
        # normal piece
        if piece.isking == False:
            dict_pos = KHOP_POS_64[pos]

            # jump moves
            for key in HOP_POS_ARGS:
                next_pos = dict_pos[key][0]
                jump_pos = dict_pos[key][1]

                # make sure move is valid
                if next_pos is None or jump_pos is None:
                    continue
                
                # 如果周围有子，其后方没有子，且异色
                if next_pos in self.pieces and jump_pos not in self.pieces and self.pieces[next_pos].player != piece.player:
                    jump_moves.append(Move(pos, jump_pos, key, MEN_MOVE, True, next_pos))
            
            # normal moves
            for key in HOP_POS_ARGS:
                next_pos = dict_pos[key][0]
                if next_pos is None:
                    continue
                if piece.player == WHITE and next_pos > pos: # 不能往回走
                    continue
                if piece.player == BLACK and next_pos < pos:
                    continue
                
                if next_pos not in self.pieces:
                    normal_moves.append(Move(pos, next_pos, key, MEN_MOVE))

        # king moves
        else:
            dict_pos = KHOP_POS_64[pos]
            
            for key in HOP_POS_ARGS:
                # for each direction, check:
                # 1. same color, if true, break
                # 2. diff color, if true, go step 3
                # 3. any space behind this diff piece, go futher util meet any piece.
                tmp_normal = []
                tmp_jump = []
                meet_diff_color = None # meet pos id
                for i in range(self.nsize):
                    next_pos = dict_pos[key][i]
                    if next_pos is None:
                        break
                    # meet piece and check color
                    if next_pos in self.pieces:
                        # same color
                        if self.pieces[next_pos].player == piece.player:
                            break
                        # diff color
                        else:
                            if meet_diff_color is not None:
                                break
                            else:
                                meet_diff_color = next_pos
                    # find a place where can jump to
                    else:
                        if meet_diff_color is not None:
                            tmp_jump.append(Move(pos, next_pos, key, KING_MOVE, True, meet_diff_color))
                        else:
                            tmp_normal.append(Move(pos, next_pos, key, KING_MOVE))
                
                # deal each direction
                king_jump_moves.extend(tmp_jump)
                normal_moves.extend(tmp_normal)


        # self.piece_moves[pos] = (king_jump_moves, jump_moves, normal_moves)
        return king_jump_moves, jump_moves, normal_moves
        
class Move():
    @classmethod
    def init_by_str(cls, str_move, game):
        take_piece = False
        taken_pos = None
        force = False
        sep = None
        if "->" in str_move:
            sep = "->"
            force = True
        elif "-" in str_move:
            sep = "-"
        elif "x" in str_move:
            sep = "x"
            take_piece = True
        else:
            raise Exception("Invalid file format.")
        pos_from, pos_to = (int(x) for x in str_move.split(sep))
        direction = get_direction(pos_from, pos_to)
        move_type = MEN_MOVE if not game.current_borad.pieces[pos_from].isking else KING_MOVE
        
        return Move(pos_from, pos_to, direction, move_type, take_piece, taken_pos, force)

    def __init__(self, pos_from, pos_to, direction, move_type = MEN_MOVE, 
                take_piece = False, taken_pos = None, force = False) -> None:
        self.pos = (pos_from, pos_to)
        self.direction = direction
        self.force = force
        self.take_piece = take_piece
        self.taken_pos = taken_pos
        self.move_type = move_type
    
    def __str__(self) -> str:
        if self.force:
            return "->".join([str(x) for x in self.pos])
        if self.take_piece:
            return "x".join([str(x) for x in self.pos])
        return "-".join([str(x) for x in self.pos])

    def id(self):
        return action2id(self)
    # def __hash__(self):
        