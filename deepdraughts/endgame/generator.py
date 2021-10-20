'''
Author: Zeng Siwei
Date: 2021-10-13 10:49:16
LastEditors: Zeng Siwei
LastEditTime: 2021-10-20 12:54:56
Description: 
'''

from ..env.py_env import *
from ..env.py_env.env_utils import _VALID_POS_64, WHITE, BLACK, KING_POS_WHITE_64, KING_POS_BLACK_64
from ..env.py_env.env_utils import CONST_TOKEN_WIN, CONST_TOKEN_LOSE, CONST_TOKEN_DRAW, CONST_TOKEN_UNKNOWN, DICT_CONST_RESULT, INF
import queue
import pickle

'''
    Endgame database: dict (key-value): FEN-(IS_WHITE_WIN, N_WIN_MOVES)
		
'''

# using computer id format


'''

    Generation aux functions

'''

def binary_search(arr, l, r, x): 
    if r >= l: 
        mid = int(l + (r - l)/2)
        if arr[mid] == x: 
            return mid 
        elif arr[mid] > x: 
            return binary_search(arr, l, mid-1, x) 
        else: 
            return binary_search(arr, mid+1, r, x) 
  
    else: 
        return -1

def is_valid_waiting_endgame(game, fen, endgame_dict):
    if fen in endgame_dict:
        return False

    # make sure the opponent has piece
    if not game.opponent_has_piece():
        return False

    # make sure no taken-piece moves for both player
    for pos, piece in game.current_board.pieces.items():
        king_jumps_tmp, jumps_tmp, normals_tmp = game.current_board.get_available_moves(pos)
        if len(king_jumps_tmp) + len(jumps_tmp) >= 1:
            return False
    return True

def update_dict_by_game_status(game_status, fen, endgame_dict):
    is_over = game_is_over(game_status)
    is_drawn = game_is_drawn(game_status)
    winner = game_winner(game_status)
    if not is_over:
        endgame_dict[fen] = (CONST_TOKEN_UNKNOWN, INF)
    else:
        if is_drawn:
            endgame_dict[fen] = (CONST_TOKEN_DRAW, 0)
        else:
            if winner == WHITE:
                endgame_dict[fen] = (CONST_TOKEN_WIN, 0)
            else:
                endgame_dict[fen] = (CONST_TOKEN_LOSE, 0)

def tokenize_drawn_endgames(waiting_endgames, endgame_dict, n_moves):
    while not waiting_endgames.empty():
        fen = waiting_endgames.get()
        status = endgame_dict[fen][0]
        if status == CONST_TOKEN_UNKNOWN:
            endgame_dict[fen] = (CONST_TOKEN_DRAW, n_moves)

'''

    Generation functions

'''

def generate_next_piece(last_pos, n_white_pawns, n_black_pawns, n_white_kings, n_black_kings,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue):
    '''
    Based generated positons, next pos is enumarated.
    '''    
    if n_white_pawns + n_black_pawns + n_white_kings + n_black_kings == 0:
        game = Game()
        game.current_player = WHITE
        game.current_board.set_board(whites_pos, blacks_pos, whites_isking, blacks_isking)
        endgame_queue.put(game.to_fen())
        game.current_player = BLACK
        endgame_queue.put(game.to_fen())
        return
    
    if last_pos is None:
        pos_list = _VALID_POS_64
    else:
        last_idx = binary_search(_VALID_POS_64, 0, len(_VALID_POS_64)-1, last_pos)
        pos_list = _VALID_POS_64[last_idx+1:]
    for pos in pos_list:
        if n_white_pawns > 0 and pos not in KING_POS_WHITE_64:
            whites_pos.append(pos)
            whites_isking.append(False)
            generate_next_piece(pos, n_white_pawns-1, n_black_pawns, n_white_kings, n_black_kings,
                    whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
            whites_pos.pop()
            whites_isking.pop()
        if n_white_kings > 0:
            whites_pos.append(pos)
            whites_isking.append(True)
            generate_next_piece(pos, n_white_pawns, n_black_pawns, n_white_kings-1, n_black_kings,
                    whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
            whites_pos.pop()
            whites_isking.pop()

        if n_black_pawns > 0 and pos not in KING_POS_BLACK_64:
            blacks_pos.append(pos)
            blacks_isking.append(False)
            generate_next_piece(pos, n_white_pawns, n_black_pawns-1, n_white_kings, n_black_kings,
                    whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
            blacks_pos.pop()
            blacks_isking.pop()
        if n_black_kings > 0:
            blacks_pos.append(pos)
            blacks_isking.append(True)
            generate_next_piece(pos, n_white_pawns, n_black_pawns, n_white_kings, n_black_kings-1,
                    whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
            blacks_pos.pop()
            blacks_isking.pop()

def generate_one_piece():
    '''
    This function is equal to generate_next_piece() when sum of all pieces == 1.
    '''    
    endgame_one_piece = dict()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    game = Game()

    for pos in _VALID_POS_64:
        game.current_player = BLACK

        if pos not in KING_POS_WHITE_64:
            whites_pos.append(pos)
            whites_isking.append(False)
            game.current_board.set_board(whites_pos, blacks_pos, whites_isking, blacks_isking)
            endgame_one_piece[game.to_fen()] = (CONST_TOKEN_WIN, 0)
            whites_pos.pop()
            whites_isking.pop()

        whites_pos.append(pos)
        whites_isking.append(True)
        game.current_board.set_board(whites_pos, blacks_pos, whites_isking, blacks_isking)
        endgame_one_piece[game.to_fen()] = (CONST_TOKEN_WIN, 0)
        whites_pos.pop()
        whites_isking.pop()

        game.current_player = WHITE
        if pos not in KING_POS_BLACK_64:
            blacks_pos.append(pos)
            blacks_isking.append(False)
            game.current_board.set_board(whites_pos, blacks_pos, whites_isking, blacks_isking)
            endgame_one_piece[game.to_fen()] = (CONST_TOKEN_LOSE, 0)
            blacks_pos.pop()
            blacks_isking.pop()

        blacks_pos.append(pos)
        blacks_isking.append(True)
        game.current_board.set_board(whites_pos, blacks_pos, whites_isking, blacks_isking)
        endgame_one_piece[game.to_fen()] = (CONST_TOKEN_LOSE, 0)
        blacks_pos.pop()
        blacks_isking.pop()
    return endgame_one_piece

def generate_basic_endgames():
    
    endgame_queue = queue.Queue()
    endgame_dict = dict()

    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    # one piece
    generate_next_piece(None, 1, 0, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
    generate_next_piece(None, 0, 1, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
    generate_next_piece(None, 0, 0, 1, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
    generate_next_piece(None, 0, 0, 0, 1,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)

    # two kings
    generate_next_piece(None, 0, 0, 1, 1,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)

    # process FEN in queue
    while not endgame_queue.empty():
        fen = endgame_queue.get()
        game = Game.load_fen(fen)
        # check whether is valid
        if is_valid_waiting_endgame(game, fen, endgame_dict):
            # check whether is over and put status into dict
            game_status = game.query_game_status()
            update_dict_by_game_status(game_status, fen, endgame_dict)

    # set two king situations 
    # all drawn
    for key, item in endgame_dict.items():
        is_white_win, n_moves_to_win = item
        if is_white_win == CONST_TOKEN_UNKNOWN:
            endgame_dict[key] =  (CONST_TOKEN_DRAW, 0)

    return endgame_dict

def generate_two_kings_versus_one_king():
    endgame_dict = generate_basic_endgames() # call when no generated file
    # with open("two_kings_versus_one_king.pkl", "rb") as fp:
    #     endgame_dict = pickle.load(fp)

    waiting_endgames = queue.Queue()
    
    waiting_endgames.put("B:WKA5:BKB8,KD8.")
    waiting_endgames.put("B:WKB8,KD8:BKA5.")
    update(waiting_endgames, endgame_dict)
    for fen, item in endgame_dict.items():
        status, n_moves = item
        if status == CONST_TOKEN_UNKNOWN:
            endgame_dict[fen] = (CONST_TOKEN_DRAW, 1)
    with open("two_kings_versus_one_king.pkl", "wb") as wfp:
        pickle.dump(endgame_dict, wfp, -1)
    return endgame_dict

def generate_three_kings_versus_one_king():
    # with open("two_kings_versus_one_king.pkl", "rb") as fp: # call when no generated file
    with open("three_kings_versus_one_king.pkl", "rb") as fp:
        endgame_dict = pickle.load(fp)
    
    waiting_endgames = queue.Queue()
    waiting_endgames.put("B:WKA5:BKB8,KD8,KF8.")
    waiting_endgames.put("B:WKB8,KD8,KF8:BKA5.")
    update(waiting_endgames, endgame_dict)

    for fen, item in endgame_dict.items():
        status, n_moves = item
        if status == CONST_TOKEN_UNKNOWN:
            endgame_dict[fen] = (CONST_TOKEN_DRAW, 2)

    with open("three_kings_versus_one_king.pkl", "wb") as wfp:
        pickle.dump(endgame_dict, wfp, -1)
    return endgame_dict

def generate_one_versus_one():
    with open("three_kings_versus_one_king.pkl", "rb") as fp:
    # with open("one_versus_one.pkl", "rb") as fp:
        endgame_dict = pickle.load(fp)
    
    generated_endgames = queue.Queue()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    generate_next_piece(None, 1, 1, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)

    waiting_endgames = queue.Queue()
    while not generated_endgames.empty():
        fen = generated_endgames.get()
        game = Game.load_fen(fen)
        # check whether is valid
        if is_valid_waiting_endgame(game, fen, endgame_dict):
            waiting_endgames.put(fen)
        
            update(waiting_endgames, endgame_dict)
            tokenize_drawn_endgames(waiting_endgames, endgame_dict, 4)

    with open("one_versus_one.pkl", "wb") as wfp:
        pickle.dump(endgame_dict, wfp, -1)
    return endgame_dict

def generate_one_versus_two():
    with open("one_versus_one.pkl", "rb") as fp:
    # with open("one_versus_two.pkl", "rb") as fp:
        endgame_dict = pickle.load(fp)
    
    generated_endgames = queue.Queue()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    generate_next_piece(None, 1, 2, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    generate_next_piece(None, 2, 1, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)

    waiting_endgames = queue.Queue()
    while not generated_endgames.empty():
        fen = generated_endgames.get()
        game = Game.load_fen(fen)
        # check whether is valid
        if is_valid_waiting_endgame(game, fen, endgame_dict):
            waiting_endgames.put(fen)
        
            update(waiting_endgames, endgame_dict)
            tokenize_drawn_endgames(waiting_endgames, endgame_dict, 4)

    with open("one_versus_two.pkl", "wb") as wfp:
        pickle.dump(endgame_dict, wfp, -1)
    return endgame_dict


def generate_two_versus_two():
    # with open("one_versus_two.pkl", "rb") as fp:
    with open("two_versus_two.pkl", "rb") as fp:
        endgame_dict = pickle.load(fp)
    
    generated_endgames = queue.Queue()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    generate_next_piece(None, 2, 2, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    
    waiting_endgames = queue.Queue()
    while not generated_endgames.empty():
        fen = generated_endgames.get()
        game = Game.load_fen(fen)
        # check whether is valid
        if is_valid_waiting_endgame(game, fen, endgame_dict):
            waiting_endgames.put(fen)
            update(waiting_endgames, endgame_dict)

            tokenize_drawn_endgames(waiting_endgames, endgame_dict, 5)

    with open("two_versus_two.pkl", "wb") as wfp:
        pickle.dump(endgame_dict, wfp, -1)
    return endgame_dict

def generate_four_piece():
    with open("two_versus_two.pkl", "rb") as fp:
    # with open("four_piece.pkl", "rb") as fp:
        endgame_dict = pickle.load(fp)
    
    generated_endgames = queue.Queue()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    generate_next_piece(None, 1, 3, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    generate_next_piece(None, 3, 1, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    
    waiting_endgames = queue.Queue()
    while not generated_endgames.empty():
        fen = generated_endgames.get()
        game = Game.load_fen(fen)
        # check whether is valid
        if is_valid_waiting_endgame(game, fen, endgame_dict):
            waiting_endgames.put(fen)
            update(waiting_endgames, endgame_dict)

            tokenize_drawn_endgames(waiting_endgames, endgame_dict, 6)

    with open("four_piece.pkl", "wb") as wfp:
        pickle.dump(endgame_dict, wfp, -1)
    return endgame_dict

def generate_five_piece():
    with open("four_piece.pkl", "rb") as fp:
    # with open("four_piece.pkl", "rb") as fp:
        endgame_dict = pickle.load(fp)
    
    generated_endgames = queue.Queue()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    generate_next_piece(None, 2, 3, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    generate_next_piece(None, 3, 2, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    generate_next_piece(None, 1, 4, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    generate_next_piece(None, 4, 1, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    
    waiting_endgames = queue.Queue()
    while not generated_endgames.empty():
        fen = generated_endgames.get()
        game = Game.load_fen(fen)
        # check whether is valid
        if is_valid_waiting_endgame(game, fen, endgame_dict):
            waiting_endgames.put(fen)
            update(waiting_endgames, endgame_dict)

            tokenize_drawn_endgames(waiting_endgames, endgame_dict, 7)

    with open("four_piece.pkl", "wb") as wfp:
        pickle.dump(endgame_dict, wfp, -1)
    return endgame_dict



'''

    Update

'''

def update(waiting_endgames, endgame_dict):
    '''
    Args: 
        waiting_endgames: queue <str>. Endgames which are token as "UNKNOWN"
        
    '''
    game_dict = dict()
    cnt_iter = 0
    while waiting_endgames.qsize() >= 1:
        cnt_iter += 1
        any_updated = False
        n_endgames_per_epoch = waiting_endgames.qsize()
        print("Iter", cnt_iter, "with", n_endgames_per_epoch, "endgames")

        for i in range(n_endgames_per_epoch):
            fen = waiting_endgames.get()
            game = Game.load_fen(fen)
            if fen not in endgame_dict:
                game_status = game.query_game_status()
                update_dict_by_game_status(game_status, fen, endgame_dict)
                any_updated = True

            if endgame_dict[fen][0] != CONST_TOKEN_UNKNOWN:
                continue

            if fen not in game_dict:
                tmp_list = []
                available_moves = game.get_all_available_moves()
                for move in available_moves:
                    game_copy = pickle.loads(pickle.dumps(game, -1))
                    game_status = game_copy.do_move(move)
                    fen_copy = game_copy.to_fen()
                    tmp_list.append((fen_copy, game_status))
                game_dict[fen] = tmp_list
                    
            available_endgames = game_dict[fen]
            n_moves = len(available_endgames)
            cnt = [0] * 4
            min_moves = [INF] * 4
            for fen_copy, game_status in available_endgames:
                # print(fen_copy)
                if fen_copy not in endgame_dict:
                    update_dict_by_game_status(game_status, fen_copy,endgame_dict)
                    waiting_endgames.put(fen_copy)
                    any_updated = True

                status, n_moves_to_win = endgame_dict[fen_copy]
                cnt[DICT_CONST_RESULT[status]] += 1
                min_moves[DICT_CONST_RESULT[status]] = min(min_moves[DICT_CONST_RESULT[status]], n_moves_to_win+1)
            
            if game.current_player == WHITE:
                if cnt[0] >= 1:
                    endgame_dict[fen] = (CONST_TOKEN_WIN, min_moves[0])
                    any_updated = True
                elif cnt[1] == n_moves:
                    endgame_dict[fen] = (CONST_TOKEN_LOSE, min_moves[1])
                    any_updated = True
                elif cnt[2] == n_moves:
                    endgame_dict[fen] = (CONST_TOKEN_DRAW, min_moves[2])
                    any_updated = True
                elif cnt[1] + cnt[2] == n_moves:
                    endgame_dict[fen] = (CONST_TOKEN_DRAW, min_moves[2])
                else:
                    waiting_endgames.put(fen)
            else:
                if cnt[0] == n_moves:
                    endgame_dict[fen] = (CONST_TOKEN_WIN, min_moves[0])
                    any_updated = True
                elif cnt[1] >= 1:
                    endgame_dict[fen] = (CONST_TOKEN_LOSE, min_moves[1])
                    any_updated = True
                elif cnt[2] == n_moves:
                    endgame_dict[fen] = (CONST_TOKEN_DRAW, min_moves[2])
                    any_updated = True
                elif cnt[0] + cnt[2] == n_moves:
                    endgame_dict[fen] = (CONST_TOKEN_DRAW, min_moves[2])
                else:
                    waiting_endgames.put(fen)

        if not any_updated:
            print("break")
            break
            
        

class EndgameGenerator():
    def __init__(self) -> None:
        pass