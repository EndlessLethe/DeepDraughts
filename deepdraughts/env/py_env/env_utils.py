'''
Author: Zeng Siwei
Date: 2021-09-11 14:31:25
LastEditors: Zeng Siwei
LastEditTime: 2021-10-11 10:44:40
Description: 
'''

from pickle import FALSE
import pickle
import numpy as np

# Const value
CONST_N_GRID_64 = 64
CONST_N_GRID_100 = 100
CONST_N_GRID_144 = 144
CONST_N_SIZE_8 = 8
CONST_N_SIZE_10 = 10
CONST_STR_RUSSIAN = "russian"
CONST_ASCII_LOWER_A = 48

# Basic code
# For training AI, use 1 and -1
WHITE = 1
NO_WINNER = 0
BLACK = -1

RUSSIAN_RULE = 2
BRAZILIAN_RULE = 3
MEN_MOVE = 4
KING_MOVE = 5

# Current states
CURRENT_RULE = None
CURRENT_BORAD = None

def set_rule(rule = CONST_STR_RUSSIAN):
    global CURRENT_RULE
    if rule.lower() == CONST_STR_RUSSIAN:
        CURRENT_RULE = RUSSIAN_RULE
    else:
        CURRENT_RULE = BRAZILIAN_RULE

def set_board(boardsize = CONST_N_GRID_64):
    if boardsize not in (CONST_N_GRID_64, CONST_N_GRID_100, CONST_N_GRID_144):
        raise Exception("Board size must be 8x8, 10x10 or 12x12.")
    global CURRENT_BORAD
    CURRENT_BORAD = boardsize

set_rule()
set_board()

print("rule", CURRENT_RULE)
print("board", CURRENT_BORAD)

def get_env_args():
    '''
    Returns: 
        nsize: board is nsize x nsize.
        ngrids: #grids of board
        n_actions: #number of actions
        
    '''    
    if CURRENT_BORAD == CONST_N_GRID_64:
        return CONST_N_SIZE_8, CONST_N_GRID_64, N_STATE_64, N_ACTION_64
    elif CURRENT_BORAD == CONST_N_GRID_100:
        return CONST_N_SIZE_10, CONST_N_GRID_100, N_STATE_100, N_ACTION_100
    else:
        raise Exception("Board size error!")

# Game State code
GAME_CONTINUE = 10
GAME_WHITE_WIN = 11
GAME_BLACK_WIN = 12
GAME_DRAW = 13
GAME_OVER_SET = set([GAME_WHITE_WIN, GAME_BLACK_WIN, GAME_DRAW])

def game_is_over(game_status):
    if game_status in GAME_OVER_SET:
        return True
    return False

def game_is_drawn(game_status):
    if game_status == GAME_DRAW:
        return True
    return False

def game_winner(game_status):
    if game_status == GAME_WHITE_WIN:
        return WHITE
    elif game_status == GAME_BLACK_WIN:
        return BLACK
    else:
        return NO_WINNER

def game_status_to_str(game_status):
    if game_status == GAME_DRAW:
        return "Game Draw"
    elif game_status == GAME_WHITE_WIN:
        return "Game over. White wins."
    elif game_status == GAME_BLACK_WIN:
        return "Game over. Black wins."
    return ""

# GUI State code
GUI_EXIT = 20
GUI_WAIT = 21
GUI_LEFTCLICK = 22
GUI_RIGHTCLICK = 23

# Player State code
HUMAN_PLAYER = 30
AI_PLAYER = 31
PURE_MCTS_PLAYER = 32
ALPHAZERO_PLAYER = 33
DRL_PLAYER = 34


# Var Tables
KING_POS_WHITE_64 = set([2, 4, 6, 8])
KING_POS_BLACK_64 = set([57, 59, 61, 63])

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

def KING_PROMOTION_POS():
    if CURRENT_BORAD == CONST_N_GRID_64:
        return KING_POS_WHITE_64, KING_POS_BLACK_64
    elif CURRENT_BORAD == CONST_N_GRID_100:
        return KING_POS_WHITE_100, KING_POS_BLACK_100
    else:
        raise Exception("Board size error!")

def VALID_POS():
    if CURRENT_BORAD == CONST_N_GRID_64:
        return VALID_POS_64
    elif CURRENT_BORAD == CONST_N_GRID_100:
        return VALID_POS_100
    else:
        raise Exception("Board size error!")

def DEFAULT_POS():
    if CURRENT_BORAD == CONST_N_GRID_64:
        return DEFAULT_POS_WHITE_64, DEFAULT_POS_BLACK_64
    elif CURRENT_BORAD == CONST_N_GRID_100:
        return DEFAULT_POS_WHITE_100, DEFAULT_POS_BLACK_100
    else:
        raise Exception("Board size error!")

def EDGE_POS():
    if CURRENT_BORAD == CONST_N_GRID_64:
        return EDGE_POS_64
    elif CURRENT_BORAD == CONST_N_GRID_100:
        return EDGE_POS_100
    else:
        raise Exception("Board size error!")

'''
    Position function.

'''

HOP_POS_ARGS = {
    "left_upper" : (-1, -1), 
    "right_upper" : (-1, 1),
    "left_lower" : (1, -1), 
    "right_lower" : (1, 1)
}


def in_boundary_64(pos, N_GRID):
    return pos >= 1 and pos <= N_GRID

def get_khop_pos(pos, N_SIZE, N_GRID, VALID_POS, EDGE_POS):
    '''
    It's sure that all pos in dict_pos is valid.

    Args: 
    
    Returns: 
    
    '''        
    dict_pos = dict()
    
    for key, args in HOP_POS_ARGS.items():
        dict_pos[key] = dict()
        is_invalid = False
        for i in range(N_SIZE):
            if is_invalid:
                dict_pos[key][i] = None
                continue

            # make sure in boundary
            next_pos = pos + (i+1)*args[0]*N_SIZE + (i+1)*args[1]
            if not in_boundary_64(next_pos, N_GRID) or next_pos not in VALID_POS:
                is_invalid = True
                next_pos = None
            dict_pos[key][i] = next_pos

            # edge pos (col 1 or 8)
            if next_pos in EDGE_POS:
                is_invalid = True
    return dict_pos

KHOP_POS_64 = dict()
for x in VALID_POS_64:
    KHOP_POS_64[x] = get_khop_pos(x, CONST_N_SIZE_8, CONST_N_GRID_100, VALID_POS_64, EDGE_POS_64)

KHOP_POS_100 = dict()
for x in VALID_POS_100:
    KHOP_POS_100[x] = get_khop_pos(x, CONST_N_SIZE_10, CONST_N_GRID_100, VALID_POS_100, EDGE_POS_100)

def get_valid_moves(VALID_POS, HOP_POS_ARGS, KHOP_POS):
    '''
	Compute all legal moves and assign an id.
    '''    
    moves = []
    for x in VALID_POS:
        for key in HOP_POS_ARGS:
            for k, next_pos in KHOP_POS[x][key].items():
                if next_pos is None:
                    break
                moves.append((x, next_pos))
    return moves

MOVE_MAP_64 = dict([(x, i) for i, x in enumerate(get_valid_moves(VALID_POS_64, HOP_POS_ARGS, KHOP_POS_64))])
MOVE_MAP_100 = dict([(x, i) for i, x in enumerate(get_valid_moves(VALID_POS_100, HOP_POS_ARGS, KHOP_POS_100))])

N_ACTION_64 = len(MOVE_MAP_64)
assert N_ACTION_64 == 280

JUMP_OVER_POS = dict()
def init_jump_over_pos(VALID_POS, HOP_POS_ARGS, KHOP_POS):
    for x in VALID_POS:
        for key in HOP_POS_ARGS:
            list_jump_over = []
            for k, next_pos in KHOP_POS[x][key].items():
                if next_pos is None:
                    break
                JUMP_OVER_POS[(x, next_pos)] = pickle.loads(pickle.dumps(list_jump_over, -1))
                list_jump_over.append(next_pos)

init_jump_over_pos(VALID_POS_64, HOP_POS_ARGS, KHOP_POS_64)
def is_jump_over_twice(move, chain_taking_pos):
    for pos in chain_taking_pos:
        if move.pos[-1] == pos:
            return True

    jump_over_pos = JUMP_OVER_POS[(move.pos[-2], move.pos[-1])]
    for pos in jump_over_pos:
        if pos in chain_taking_pos:
            return True
    return False

def is_opposite_direcion(d1, d2):
    if (d1 == "left_upper" and d2 == "right_lower") or (d2 == "left_upper" and d1 == "right_lower"):
        return True
    if (d1 == "left_lower" and d2 == "right_upper") or (d2 == "left_lower" and d1 == "right_upper"):
        return True
    return False

'''
    Position format function.

    Main format for piece position:
    1. idx. Starting index from left upper corner with number 1.
    2. string. Used in chess, the format is indexed from left lower corner. 
        And each row is described by char 'A' to 'H'.
    3. tuple(x, y). The origin is left lower corner by default, to keep the same with chess format.
		
'''



def norm_pos(pos):
    if isinstance(pos, int): # idx format
        return pos
    if isinstance(pos, str): # 64 format like C3 and D4
        return POS_MAP_64[pos.lower()]
    if isinstance(pos, (list, tuple)): # (x, y) format, started from 1
        # TODO
        # return POS_MAP_64[chr(CONST_ASCII_LOWER_A+pos[0]-1)+str(pos[1])] 
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

def coord2fstr():
    # TODO
    pass


'''
    Vectorization function.          
'''

def action2id(action):
    return MOVE_MAP_64[(action.pos[-2], action.pos[-1])]

def actions2vec(actions, probs):
    action_ids = [action2id(action) for action in actions]
    return _actions2vec(action_ids, probs)
    
def _actions2vec(action_ids, probs):
    vec = np.zeros(N_ACTION_64)
    for action, prob in zip(action_ids, probs):
        vec[action] = prob
    return vec

N_STATE_64 = CONST_N_SIZE_8 * 2 + 3

def state2vec(state):
    '''
    Network input vector:
        - last_four_board
            - white man
            - white king
            - black man
            - black king
        - player -1 / 1
        - is_chain_taking 0/1
        - taken_piece nsize * 2
        - n_king_move 0/1
    ''' 
    nsize = state.current_board.nsize
    ngrid = state.current_board.ngrid
    vec_board = np.zeros((4, ngrid))   
    for pos, piece in state.current_board.pieces.items():
        pos -= 1
        if piece.isking:
            if piece.player == WHITE:
                vec_board[1][pos] = 1
            elif piece.player == BLACK:
                vec_board[3][pos] = 1
        else:
            if piece.player == WHITE:
                vec_board[0][pos] = 1
            elif piece.player == BLACK:
                vec_board[2][pos] = 1
    vec_board = vec_board.reshape((4, nsize, nsize))
    vec_state = np.zeros(3+nsize*2)
    vec_state[0] = 1 if state.current_player == WHITE else BLACK
    vec_state[1] = state.is_chain_taking
    for i, move in enumerate(state.chain_taking_moves):
        vec_state[i+2] = move.taken_pos-1
    vec_state[-1] = state.n_king_move
    return vec_board, vec_state
