'''
Author: Zeng Siwei
Date: 2021-09-11 14:17:31
LastEditors: Zeng Siwei
LastEditTime: 2021-09-11 19:24:31
Description: 
'''

from utils import *

class Piece():
    def __init__(self, player, pos, isking, KING_POS_WHITE, KING_POS_BLACK) -> None:
        self.player = player # white 1 black -1
        self.pos = pos
        self.isking = isking
        self.captured = False
        self.KING_POS_WHITE = KING_POS_WHITE
        self.KING_POS_BLACK = KING_POS_BLACK

    def move_to(self, pos) -> None:
        '''
        Args: 
            pos: pos to move. Make sure it's available.
        '''        
        self.pos = pos
        if not self.isking:
            if self.player == WHITE and pos in self.KING_POS_WHITE:
                self.king_promote()
            elif self.player == BLACK and pos in self.KING_POS_BLACK:
                self.king_promote()


    def king_promote(self) -> None:
        self.isking = True