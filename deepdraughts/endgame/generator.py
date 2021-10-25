'''
Author: Zeng Siwei
Date: 2021-10-13 10:49:16
LastEditors: Zeng Siwei
LastEditTime: 2021-10-25 15:09:16
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

def err_call_back(err):
    print(f'error：{str(err)}')

def call_back(res):
        print(f'Hello,World!')

def k_sum_combines(k):
    combines = []
    for i in range(k+1):
        for j in range(k+1):
            for t in range(k+1):
                for m in range(k+1):
                    if i + j + t + m == k:
                        combines.append((i, j, t, m))
    return combines


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

def is_valid_waiting_endgame(fen, endgame_dict):
    game = Game.load_fen(fen)

    if fen in endgame_dict:
        return False

    # make sure the opponent has piece (game has not been over)
    if not game.opponent_has_piece():
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

def generate_k_piece(k):
    if k == 1:
        endgame_dict = dict()
    else:
        with open(str(k-1)+"p.pkl", "rb") as fp:
            endgame_dict = pickle.load(fp)
    
    generated_endgames = queue.Queue()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []

    combines = k_sum_combines(k)
    for a, b, c, d in combines:
        generate_next_piece(None, a, b, c, d,
            whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)

    waiting_endgames = queue.Queue()
    while not generated_endgames.empty():
        fen = generated_endgames.get()

        # check whether is valid
        if is_valid_waiting_endgame(fen, endgame_dict):
            waiting_endgames.put(fen)
        
            update(waiting_endgames, endgame_dict)
            tokenize_drawn_endgames(waiting_endgames, endgame_dict, k-1)

    with open(str(k)+"p.pkl", "wb") as wfp:
        pickle.dump(endgame_dict, wfp, -1)
    return endgame_dict

def parallel_generate_k_piece(k, managers, n_cores = 4, n_fens = 1000):
    # from prwlock import RWLock
    from multiprocessing import Pool
    
    def split_chunks(n, lst):
        return [lst[i:i+n] for i in range(0, len(lst), n)]

    if k == 1:
        saved_dict = dict()
    else:
        with open(str(k-1)+"p.pkl", "rb") as fp:
            saved_dict = pickle.load(fp)

    generated_endgames = queue.Queue()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    combines = k_sum_combines(k)
    for a, b, c, d in combines:
        generate_next_piece(None, a, b, c, d,
            whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    print("Finish generation with", generated_endgames.qsize())

    manager, endgame_lock_manager, game_lock_manager = managers
    endgame_dict, game_dict = manager.dict(), manager.dict()
    # endgame_rlock, endgame_wlock = endgame_lock_mananger.reader_lock, endgame_lock_mananger.writer_lock
    # game_rlock, game_wlock = game_lock_mananger.reader_lock, game_lock_mananger.writer_lock
    # endgame_rlock, endgame_wlock = manager.Lock(), manager.Lock()
    # game_rlock, game_wlock = manager.Lock(), manager.Lock()
    endgame_dict.update(saved_dict)

    list_fen = []
    while not generated_endgames.empty():
        fen = generated_endgames.get()
        
        # check whether is valid
        if is_valid_waiting_endgame(fen, endgame_dict):
            list_fen.append(fen)
    list_batch = split_chunks(n_fens, list_fen)
    print(len(list_fen), len(list_batch))

    with Pool(n_cores) as pool:
        for list_fen in list_batch:
            pool.apply_async(parallel_update, 
                        (list_fen, endgame_dict, game_dict, endgame_lock_manager, 
                        game_lock_manager, k-1))
                        # callback=call_back, error_callback=err_call_back)
            # pool.apply_async(parallel_update, 
            #             (list_fen, endgame_dict, game_dict, endgame_rlock, endgame_wlock,
            #             game_rlock, game_wlock, k-1))
        pool.close() 
        pool.join()


    print(len(endgame_dict))
    with open(str(k)+"p.pkl", "wb") as wfp:
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


def update_string(val, l):
    l.append(val)

# def parallel_update(list_fen, endgame_dict, game_dict, endgame_read_lock, endgame_write_lock,
#                         game_read_lock, game_write_lock, draw_token):
def parallel_update(list_fen, endgame_dict, game_dict, endgame_lock_manager, 
                    game_lock_manager, draw_token):
    '''
    All data in game_dict will only be written once.

    '''    
    print("start parallel_update", len(list_fen))
    cnt_iter = 0
    waiting_endgames = queue.Queue()
    for fen in list_fen:
        waiting_endgames.put(fen)
    endgame_read_lock = endgame_lock_manager.reader_lock
    endgame_write_lock = endgame_lock_manager.writer_lock
    game_read_lock = game_lock_manager.reader_lock
    game_write_lock = game_lock_manager.writer_lock
    

    while waiting_endgames.qsize() >= 1:
        cnt_iter += 1
        any_updated = False
        n_endgames_per_epoch = waiting_endgames.qsize()
        print("Iter", cnt_iter, "with", n_endgames_per_epoch, "endgames")

        for i in range(n_endgames_per_epoch):
            fen = waiting_endgames.get()
            game = Game.load_fen(fen)

            if fen not in endgame_dict:
                with endgame_write_lock:
                    if fen not in endgame_dict:
                        game_status = game.query_game_status()
                        update_dict_by_game_status(game_status, fen, endgame_dict)
                        any_updated = True
    
            with endgame_read_lock:
                if endgame_dict[fen][0] != CONST_TOKEN_UNKNOWN:
                    continue
            
            if fen not in game_dict:
                with game_write_lock:
                    if fen not in game_dict:
                        tmp_list = []
                        available_moves = game.get_all_available_moves()
                        for move in available_moves:
                            game_copy = pickle.loads(pickle.dumps(game, -1))
                            game_status = game_copy.do_move(move)
                            fen_copy = game_copy.to_fen()
                            tmp_list.append((fen_copy, game_status))
                        game_dict[fen] = tmp_list
            
            with game_read_lock:
                available_endgames = game_dict[fen]
            n_moves = len(available_endgames)
            cnt = [0] * 4
            min_moves = [INF] * 4
            for fen_copy, game_status in available_endgames:
                # print(fen_copy)
                if fen_copy not in endgame_dict:
                    with endgame_write_lock:
                        if fen_copy not in endgame_dict:
                            update_dict_by_game_status(game_status, fen_copy,endgame_dict)
                            waiting_endgames.put(fen_copy)
                            any_updated = True

                with endgame_read_lock:
                    status, n_moves_to_win = endgame_dict[fen_copy]
                cnt[DICT_CONST_RESULT[status]] += 1
                min_moves[DICT_CONST_RESULT[status]] = min(min_moves[DICT_CONST_RESULT[status]], n_moves_to_win+1)
            
            if game.current_player == WHITE:
                if cnt[0] >= 1:
                    with endgame_write_lock:
                        endgame_dict[fen] = (CONST_TOKEN_WIN, min_moves[0])
                        any_updated = True
                elif cnt[1] == n_moves:
                    with endgame_write_lock:
                        endgame_dict[fen] = (CONST_TOKEN_LOSE, min_moves[1])
                        any_updated = True
                elif cnt[2] == n_moves:
                    with endgame_write_lock:
                        endgame_dict[fen] = (CONST_TOKEN_DRAW, min_moves[2])
                        any_updated = True
                elif cnt[1] + cnt[2] == n_moves:
                    with endgame_write_lock:
                        endgame_dict[fen] = (CONST_TOKEN_DRAW, min_moves[2])
                        any_updated = True
                else:
                    waiting_endgames.put(fen)
            else:
                if cnt[0] == n_moves:
                    with endgame_write_lock:
                        endgame_dict[fen] = (CONST_TOKEN_WIN, min_moves[0])
                        any_updated = True
                elif cnt[1] >= 1:
                    with endgame_write_lock:
                        endgame_dict[fen] = (CONST_TOKEN_LOSE, min_moves[1])
                        any_updated = True
                elif cnt[2] == n_moves:
                    with endgame_write_lock:
                        endgame_dict[fen] = (CONST_TOKEN_DRAW, min_moves[2])
                        any_updated = True
                elif cnt[0] + cnt[2] == n_moves:
                    with endgame_write_lock:
                        endgame_dict[fen] = (CONST_TOKEN_DRAW, min_moves[2])
                        any_updated = True
                else:
                    waiting_endgames.put(fen)

        if not any_updated:
            print("break")
            break
    
    with endgame_write_lock:
        tokenize_drawn_endgames(waiting_endgames, endgame_dict, draw_token)
    
    with game_write_lock:
        with endgame_read_lock:
            list_remove = []
            for fen in game_dict.keys():
                if fen in endgame_dict:
                    if endgame_dict[fen][0] != CONST_TOKEN_UNKNOWN:
                        list_remove.append(fen)
            for fen in list_remove:
                game_dict.pop(fen)
    

