'''
Author: Zeng Siwei
Date: 2021-09-11 14:36:26
LastEditors: Zeng Siwei
LastEditTime: 2021-09-12 20:41:28
Description: 
'''

from .env_utils import *
from .piece import Piece

class Board():
    def __init__(self, ngrid = N_GRID_64, rule = RUSSIAN_RULE) -> None:
        self.pieces = dict() # key - value: pos - piece
        self.ngrid = ngrid
        self.rule = rule
        self.available_moves = dict()
        self.jump_moves = []
        self.normal_moves = []
        self.set_board(*self.get_default_pos())

        import math
        n = int(math.sqrt(ngrid))
        if n * n != ngrid:
            raise Exception("N_grid is not squre number.")
        self.nsize = n
        

    '''
    Load gloval vars
    '''    

    def get_king_promotion_pos(self):
        return globals()["KING_POS_WHITE_" + str(self.ngrid)], globals()["KING_POS_WHITE_" + str(self.ngrid)]


    def get_default_pos(self):
        return globals()["DEFAULT_POS_WHITE_" + str(self.ngrid)], globals()["DEFAULT_POS_BLACK_" + str(self.ngrid)]

    def get_edge_pos(self):
        return globals()["EDGE_POS_" + str(self.ngrid)]

    def get_valid_pos(self):
        return globals()["VALID_POS_" + str(self.ngrid)]

    '''
    Update board
    '''    
    def reset_available_moves(self):
        self.available_moves.clear()
        self.jump_moves.clear()
        self.normal_moves.clear()

    def set_board(self, whites_pos, blacks_pos, whites_isking = None, blacks_isking = None):
        whites_pos = norm_pos_list(whites_pos)
        blacks_pos = norm_pos_list(blacks_pos)
        if (self.check_pos_list(whites_pos) and self.check_pos_list(blacks_pos)) == False:
            raise Exception("Invaid pos list")
        if whites_isking is None:
            whites_isking = [False] * len(whites_pos)
        if blacks_isking is None:
            blacks_isking = [False] * len(blacks_pos)

        for pos, isking in zip(whites_pos, whites_isking):
            self.pieces[pos] = Piece(WHITE, pos, isking, *self.get_king_promotion_pos())
        for pos, isking in zip(blacks_pos, blacks_isking):
            self.pieces[pos] = Piece(BLACK, pos, isking, *self.get_king_promotion_pos())
        self.reset_available_moves()

    def check_pos_list(self, pos_list):
        is_ok = True
        for pos in pos_list:
            if pos not in globals()["VALID_POS_" + str(self.ngrid)]:
                x, y = pos2coord(pos, self.ngrid)
                print("Invalid pos:", pos, "row:", x, "col:", y)
                is_ok = False
        return is_ok

    def move(self, pos_from, pos_to, take_piece = False, force = False):
        '''
        Move the piece in pos_from to pos_to.
        '''
        if pos_from not in self.pieces or pos_to in self.pieces:
            return None # action is not available
        piece = self.pieces.pop(pos_from)
        piece.move_to(pos_to)
        self.pieces[pos_to] = piece
        if take_piece:
            self.pieces.pop((pos_from + pos_to) / 2)
        self.reset_available_moves()
        return Move(pos_from, pos_to, force)


    '''
    Querying states
    '''    
    def get_pieces(self):
        return [x for x in self.pieces.values()]

    def get_khop_pos(self, pos, k):
        '''
        It's sure that all pos in dict_pos is valid.

        Args: 
		
        Returns: 
		
        '''        
        dict_pos = dict()
        EDGE_POS = self.get_edge_pos()
        VALID_POS = self.get_valid_pos()
        
        for key, args in HOP_POS_ARGS.items():
            dict_pos[key] = dict()
            is_invalid = False
            for i in range(k):
                if is_invalid:
                    dict_pos[key][i] = None
                    continue

                # make sure in boundary
                next_pos = pos + (i+1)*args[0]*self.nsize + (i+1)*args[1]
                if not self.in_boundary(next_pos) or next_pos not in VALID_POS:
                    is_invalid = True
                    next_pos = None
                dict_pos[key][i] = next_pos

                # edge pos (col 1 or 8)
                if next_pos in EDGE_POS:
                    is_invalid = True
                # print("for pos", pos, key, i, "next", next_pos, is_invalid)
        return dict_pos


    def in_boundary(self, pos):
        return pos >= 1 and pos <= self.ngrid

    def get_available_moves(self, pos):
        # TODO Brazilian rule 有多吃多

        if pos in self.available_moves:
            return self.available_moves[pos]
        
        jump_moves = []
        normal_moves = []

        piece = self.pieces[pos]
        _, col = pos2coord(pos, self.nsize)
        
        # normal piece
        if piece.isking == False:
            dict_pos = self.get_khop_pos(pos, 2)

            # jump moves
            for key in HOP_POS_ARGS:
                next_pos = dict_pos[key][0]
                jump_pos = dict_pos[key][1]

                # make sure move is valid
                if next_pos is None or jump_pos is None:
                    continue
                
                # 如果周围有子，其后方没有子，且异色
                if next_pos in self.pieces and jump_pos not in self.pieces and self.pieces[next_pos].player != piece.player:
                    jump_moves.append(jump_pos)
            
            # normal moves
            if len(jump_moves) == 0:
                for key in HOP_POS_ARGS:
                    next_pos = dict_pos[key][0]
                    if next_pos is None:
                        continue
                    if piece.player == WHITE and next_pos > pos: # 不能往回走
                        continue
                    if piece.player == BLACK and next_pos < pos:
                        continue
                    
                    if next_pos not in self.pieces:
                        normal_moves.append(next_pos)

        # king moves
        else:
            dict_pos = self.get_khop_pos(pos, self.nsize)
            
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
                            tmp_jump.append(next_pos)
                        else:
                            tmp_normal.append(next_pos)
                
                # deal each direction
                if len(tmp_jump) >= 1:
                    jump_moves.extend(tmp_jump)
                else:
                    normal_moves.extend(tmp_normal)


        self.available_moves[pos] = (jump_moves, normal_moves)
        return jump_moves, normal_moves


    def get_all_available_moves(self, current_player):
        '''
        Args: 
		
        Returns: 
            take_piece: Bool
            next_moves: List
        '''
        if len(self.jump_moves) + len(self.normal_moves):
            return self.jump_moves, self.normal_moves

        all_jump = []
        all_normal = []
        for pos in self.pieces:
            if self.pieces[pos].player != current_player:
                continue
            jump_moves, normal_moves = self.get_available_moves(pos)
            all_jump.extend(jump_moves)
            all_normal.extend(normal_moves)

        self.jump_moves = list(set(all_jump))
        self.normal_moves = list(set(all_normal))
        return self.jump_moves, self.normal_moves
        
class Move():
    def __init__(self, pos_from, pos_to, force = False) -> None:
        self.move_list = [pos_from, pos_to]
        self.force = force
    
    def __str__(self) -> str:
        if not self.force:
            return "-".join([str(x) for x in self.move_list])
        else:
            return "->".join([str(x) for x in self.move_list])

    def merge(self, merging_move):
        if len(merging_move.move_list) != 2:
            raise Exception("Length of merging move is not 2")
        if self.move_list[-1] != merging_move.move_list[0]:
            raise Exception("Merging move does not match.")
        self.move_list.append(merging_move[1])
