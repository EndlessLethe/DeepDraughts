'''
Author: Zeng Siwei
Date: 2021-10-13 11:03:14
LastEditors: Zeng Siwei
LastEditTime: 2021-10-17 16:17:06
Description: 
'''

import re

def parse_fen(fen):
    '''
    Based on FMJD FEN format, game states is added at the end of FEN string.
    [CHAINTAKING][SQUARE_NUM][[SQUARE_NUM][,]...]: is_chain_taking, last_pos and chain_taking_pos
    
    [TURN]:[COLOUR1][[K][SQUARE_NUM][,]...]:[COLOUR2][[K][SQUARE_NUM][,]...].[CHAINTAKING][SQUARE_NUM],[[SQUARE_NUM][,]...]

    More details about FEN: http://pdn.fmjd.org/fen.html
    
    '''
    tokens = fen.split(".")
    is_chain_taking = False
    last_piece_pos = None
    chain_taking_pos = []
    if len(tokens) == 2:
        is_chain_taking, last_piece_pos, chain_taking_pos = _parse_fen_chain_taking(tokens[1])
    current_player, whites_pos, blacks_pos, whites_isking, blacks_isking = _parse_fen_pos(tokens[0])
    return current_player, whites_pos, blacks_pos, whites_isking, blacks_isking, is_chain_taking, last_piece_pos, chain_taking_pos


def _parse_fen_pos(fen):
    '''
        # The code is mainly contributed by akalverboer.
        # The github link is: https://github.com/akalverboer/python_draughts_10x10/blob/master/mad100_play.py
        #
        # Code is modified by EndlessLethe for further use.
    '''
    """ Parses a string in Forsyth-Edwards Notation into a Position """                # working copy
    fen = fen.replace(" ", "")  # remove all spaces
    fen = re.sub(r'\..*$', '', fen)   # cut off info (.xxx) at the end
    if fen == '': fen = 'W:B:W'       # empty FEN Position
    if fen == 'W::': fen = 'W:B:W'
    if fen == 'B::': fen = 'B:B:W'
    fen = re.sub(r'.::$', 'W:W:B', fen)
    parts = fen.split(':')
    
    current_player = 'B' if parts[0][0] == 'B' else 'W'
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []

    for i in range(1, 3):   # process the two sides
        side = parts[i]
        color = side[0]
        side = side[1:]     # strip color char
        if len(side) == 0: continue    # nothing to do: next side
        numSquares = side.split(',')   # list of numbers or range of numbers with/without king flag
        for num in numSquares:
            isking = True if num[0] == 'K' else False
            num = num[1:] if isking else num       # strip 'K'
            isRange = True if len(num.split('-')) == 2 else False
            if isRange:
                r = num.split('-')
                for j in range( int(r[0]), int(r[1]) + 1 ):
                    if color.lower() == "w":
                        whites_pos.append(j)
                        whites_isking.append(isking)
                    else:
                        blacks_pos.append(j)
                        blacks_isking.append(isking)
                    
            else:
                if ord(num[0]) < 65: # ord("A") 65, ord("0") 48, ord("a") 97
                    num = int(num)  
                if color.lower() == "w":
                    whites_pos.append(num)
                    whites_isking.append(isking)
                else:
                    blacks_pos.append(num)
                    blacks_isking.append(isking)
    return current_player, whites_pos, blacks_pos, whites_isking, blacks_isking

def _parse_fen_chain_taking(fen):
    if len(fen) <= 1:
        return False, None, []
    is_change_taking = int(fen[0])
    if ord(fen[1]) >= 65: # ord("A") 65, ord("0") 48, ord("a") 97
        pos = [x for x in fen[1:].split(",")]
    else:
        pos = [int(x) for x in fen[1:].split(",")]
    return is_change_taking, pos[0], pos[1:]

def game_to_fen(current_player, whites_pos, blacks_pos, whites_isking, 
            blacks_isking, is_chain_taking, last_piece_pos, chain_taking_pos):
    fen = current_player
    white_pieces, black_pieces = [], []
    for i, pos in enumerate(whites_pos):
        white_pieces.append("K"+str(pos) if whites_isking[i] else str(pos))
    for i, pos in enumerate(blacks_pos):
        black_pieces.append("K"+str(pos) if blacks_isking[i] else str(pos))
    fen += ":W"
    fen += ",".join(white_pieces)
    fen += ":B"
    fen += ",".join(black_pieces)
    fen += "."
    if is_chain_taking:
        fen += str(int(is_chain_taking))
        fen += last_piece_pos + ","
        fen += ",".join(chain_taking_pos)
    return fen
