'''
Author: Zeng Siwei
Date: 2021-09-11 14:31:25
LastEditors: Zeng Siwei
LastEditTime: 2021-09-12 19:54:07
Description: 
'''

N_GRID_64 = 64
N_GRID_100 = 100
N_SIZE_8 = 8

RUSSIAN_RULE = 0
BRAZILIAN_RULE = 1

WHITE = 1
BLACK = -1

KING_POS_WHITE_64 = set([2, 4, 6, 8])
KING_POS_BLACK_64 = set([])

KING_POS_WHITE_100 = set([])
KING_POS_BLACK_100 = set([])

DEFAULT_POS_WHITE_64 = [41, 43, 45, 47, 50, 52, 54, 56, 57, 59, 61, 63]
DEFAULT_POS_BLACK_64 = [2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 22, 24]

DEFAULT_POS_WHITE_100 = []
DEFAULT_POS_BLACK_100 = []

VALID_POS_64 = set([2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 22, 24, 
                    25, 27, 29, 31, 34, 36, 38, 40,
                    41, 43, 45, 47, 50, 52, 54, 56, 57, 59, 61, 63])
VALID_POS_100 = set([])

EDGE_POS_64 = set([9, 25, 41, 57, 8, 24, 40, 56])
EDGE_POS_100 = set([])

POS_MAP_64 = {
    
}

ASCII_LOWER_A = 48

'''
    Position function.

    Main format for piece position:
    1. idx. Starting index from left upper corner with number 1.
    2. string. Used in chess, the format is indexed from left lower corner. 
        And each row is described by char 'A' to 'H'.
    3. tuple(x, y). The origin is left lower corner by default, to keep the same with chess format.
		
'''

HOP_POS_ARGS = {
    "left_upper" : (-1, -1), 
    "right_upper" : (-1, 1),
    "left_lower" : (1, -1), 
    "right_lower" : (1, 1)
}

def norm_pos(pos):
    if isinstance(pos, int): # idx format
        return pos
    if isinstance(pos, str): # 64 format like C3 and D4
        return POS_MAP_64[pos.lower()]
    if isinstance(pos, (list, tuple)): # (x, y) format, started from 1
        # return POS_MAP_64[chr(ASCII_LOWER_A+pos[0]-1)+str(pos[1])] 
        return 
    
def norm_pos_list(iter):
    return [norm_pos(x) for x in iter]

def pos2coord(pos, nsize, origin = "left_lower"):
    '''
	Coord is format as Chess.
    (1, 1) is left lower corner.
    '''    
    pos -= 1
    if origin == "left_upper":
        row = int(pos / nsize) + 1
    else:
        row = nsize - int(pos / nsize)
    col = pos % nsize + 1
    return row, col

def coord2pos(row, col, nsize, origin = "left_lower"):
    row -= 1
    col -= 1

    if origin == "left_upper":
        idx = row * nsize + col
    else:
        idx = (nsize-1-row) * nsize + col 
    return idx + 1


if __name__ == "__main__":
    a = "0"
    a = ord(a)
    print(a)