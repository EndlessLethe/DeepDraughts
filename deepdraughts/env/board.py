'''
Author: Zeng Siwei
Date: 2021-09-11 14:36:26
LastEditors: Zeng Siwei
LastEditTime: 2021-09-12 00:15:46
Description: 
'''

from utils import *
from piece import Piece

class Board():
    def __init__(self, ngrid = N_GRID_64) -> None:
        self.pieces = dict() # key - value: pos - piece
        self.ngrid = ngrid
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

    '''
    Update board
    '''    
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

    def check_pos_list(self, pos_list):
        is_ok = True
        for pos in pos_list:
            if pos not in globals()["VALID_POS_" + str(self.ngrid)]:
                x, y = pos2coord(pos, self.ngrid)
                print("Invalid pos:", pos, "row:", x, "col:", y)
                is_ok = False
        return is_ok

    def move(self, pos_from, pos_to, take_piece = False):
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
        return Move(pos_from, pos_to)


    '''
    Querying states
    '''    
    def get_pieces(self):
        return [x for x in self.pieces.values()]

    def get_khop_pos(self, pos, k):
        dict_pos = dict()
        for i in range(k):
            dict_pos[i] = dict()
            for key, args in HOP_POS_ARGS.items():
                dict_pos[i][key] = pos + (i+1)*args[0]*self.nsize + (i+1)*args[1]
        return dict_pos


    def in_boundary(self, pos):
        return pos >= 1 and pos <= self.ngrid

    def get_available_moves(self, pos):
        jump_moves = []
        normal_moves = []

        piece = self.pieces[pos]
        _, col = pos2coord(pos, self.nsize)
        
        dict_pos = self.get_khop_pos(pos, 2)
        print(dict_pos)

        # normal piece
        # jump moves
        for key in HOP_POS_ARGS:
            next_pos = dict_pos[0][key]
            jump_pos = dict_pos[1][key]
            if (self.in_boundary(next_pos) and self.in_boundary(jump_pos)) == False:
                continue
            
            # 如果周围有子，其后方没有子，且异色
            if next_pos in self.pieces and jump_pos not in self.pieces and self.pieces[next_pos].player != piece.player:
                    # 不能跳出棋盘范围外
                    if key.startswith("left") and col >= 3:
                        jump_moves.append(jump_pos)
                    if key.startswith("right") and col <= 6:
                        jump_moves.append(jump_pos)
        
        # normal moves
        if len(jump_moves) == 0:
            for key in HOP_POS_ARGS:
                next_pos = dict_pos[0][key]
                print(next_pos)
                if self.in_boundary == False:
                    continue
                if piece.player == WHITE and next_pos > pos: # 不能往回走
                    continue
                if piece.player == BLACK and next_pos < pos:
                    continue
                
                if next_pos not in self.pieces:
                    if key.startswith("left") and col >= 2:
                        normal_moves.append(next_pos)
                    if key.startswith("right") and col <= 7:
                        normal_moves.append(next_pos)

        # king moves
        # if piece.isking == True:
        #     dict_pos = self.get_khop_pos(pos, 8)
        return jump_moves, normal_moves


    def get_all_available_moves(self):
        pass
        
class Move():
    def __init__(self, pos_from, pos_to) -> None:
        self.pos_from = pos_from
        self.pos_to = pos_to
    
    def __str__(self) -> str:
        return str(self.pos_from) + "-" + str(self.pos_to)