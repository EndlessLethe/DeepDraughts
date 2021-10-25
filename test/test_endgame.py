'''
Author: Zeng Siwei
Date: 2021-10-14 12:35:49
LastEditors: Zeng Siwei
LastEditTime: 2021-10-25 18:14:25
Description: 
'''

from pygame.event import wait
from deepdraughts.gui import GUI
from deepdraughts.env import *
from deepdraughts.endgame.generator import *
import queue
import time

def test_generate_next_piece1():
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    endgame_queue = queue.Queue()
    endgame_dict = dict()
    generate_next_piece(None, 1, 0, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
    generate_next_piece(None, 0, 1, 0, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
    generate_next_piece(None, 0, 0, 1, 0,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)
    generate_next_piece(None, 0, 0, 0, 1,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)

    while not endgame_queue.empty():
        fen = endgame_queue.get()
        game = Game.load_fen(fen)
        # check whether is valid
        if is_valid_waiting_endgame(game, fen, endgame_dict):
            # check whether is over and put status into dict
            update_dict_by_game_status(game, endgame_dict)

    print(len(endgame_dict))
    assert len(endgame_dict) == 120

    for key, item in endgame_dict.items():
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()


def test_generate_next_piece2():
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    endgame_queue = queue.Queue()
    endgame_dict = dict()
    generate_next_piece(None, 0, 0, 1, 1,
        whites_pos, blacks_pos, whites_isking, blacks_isking, endgame_queue)

    while not endgame_queue.empty():
        fen = endgame_queue.get()
        game = Game.load_fen(fen)
        # check whether is valid
        if is_valid_waiting_endgame(game, fen, endgame_dict):
            # check whether is over and put status into dict
            update_dict_by_game_status(game, endgame_dict)

    print(len(endgame_dict))
    # assert len(endgame_dict) == 120

    for key, item in endgame_dict.items():
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()

def test_k_sum_combines(k):
    combines = k_sum_combines(k)
    for x in combines:
        print(x)

def test_generate_next_piece3():
    fen = "W:WKG7:BH6,KD2."
    generated_endgames = queue.Queue()
    whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
    combines = k_sum_combines(3)
    
    for a, b, c, d in combines:
        generate_next_piece(None, a, b, c, d,
            whites_pos, blacks_pos, whites_isking, blacks_isking, generated_endgames)
    while not generated_endgames.empty():
        generated_fen = generated_endgames.get()
        if generated_fen == fen:
            endgame_dict = dict()
            game = Game.load_fen(fen)
            print("generated", is_valid_waiting_endgame(game, fen, endgame_dict))

def test_update1():
    endgame_dict = generate_basic_endgames()
    new_dict = pickle.loads(pickle.dumps(endgame_dict, -1))
    
    fen = "W:WKA5:BKB8,KB6."
    
    gui = GUI()
    gui.game = Game.load_fen(fen)
    gui.run()
    
    waiting_endgames = queue.Queue()
    waiting_endgames.put(fen)
    update(waiting_endgames, new_dict)
    for key, item in new_dict.items():
        if key in endgame_dict:
            continue
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()

def test_update2():
    endgame_dict = generate_basic_endgames()
    new_dict = pickle.loads(pickle.dumps(endgame_dict, -1))
    
    fen = "B:WKA5:BKB8,KD8."
    # fen = "B:WKB8,KD8:BKA5."
    
    # gui = GUI()
    # gui.game = Game.load_fen(fen)
    # gui.run()
    
    waiting_endgames = queue.Queue()
    waiting_endgames.put(fen)
    update(waiting_endgames, new_dict)
    for key, item in new_dict.items():
        if key in endgame_dict:
            continue
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()

def test_generate_one_piece():
    with open("1p.pkl", "rb") as fp:
        basic_dict = pickle.load(fp)
    endgame_dict = generate_k_piece(1)
    print(len(endgame_dict))
    assert len(endgame_dict) == 120

    for key, item in endgame_dict.items():
        if key in basic_dict:
            continue
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()
    

def test_generate_two_piece():
    start_time = time.time()
    with open("1p.pkl", "rb") as fp:
        basic_dict = pickle.load(fp)

    endgame_dict = generate_k_piece(2)
    end_time = time.time()
    print("Comsuming", end_time-start_time, "s")
    

    print(len(basic_dict))
    print(len(endgame_dict))
    assert len(endgame_dict) == 10580

    # for key, item in endgame_dict.items():
    #     if key in basic_dict:
    #         continue
        
    #     if item[0] != CONST_TOKEN_DRAW:
    #         continue
    #     print(key, item)
    #     gui = GUI()
    #     gui.game = Game.load_fen(key)
    #     gui.run()

def test_generate_three_piece():
    start_time = time.time()
    with open("2p.pkl", "rb") as fp:
        basic_dict = pickle.load(fp)

    endgame_dict = generate_k_piece(3)
    end_time = time.time()
    print("Comsuming", end_time-start_time, "s")
    # Comsuming 256.7149775028229 s

    print(len(basic_dict))
    print(len(endgame_dict))
    assert len(endgame_dict) == 470180

    # for key, item in endgame_dict.items():
    #     if key in basic_dict:
    #         continue
        
    #     if item[0] != CONST_TOKEN_DRAW:
    #         continue
    #     print(key, item)
    #     gui = GUI()
    #     gui.game = Game.load_fen(key)
    #     gui.run()

def test_generate_four_piece():
    start_time = time.time()
    # with open("3p.pkl", "rb") as fp:
    #     basic_dict = pickle.load(fp)

    endgame_dict = generate_k_piece(4)
    end_time = time.time()
    print("Comsuming", end_time-start_time, "s")
    # Comsuming 10119.538697481155 s

    # print(len(basic_dict))
    print(len(endgame_dict))
    # assert len(endgame_dict) == 13998502

    # for key, item in endgame_dict.items():
    #     if key in basic_dict:
    #         continue
        
    #     if item[0] != CONST_TOKEN_DRAW:
    #         continue
    #     print(key, item)
    #     gui = GUI()
    #     gui.game = Game.load_fen(key)
    #     gui.run()

def test_parallel_generate_three_piece(manager):
    start_time = time.time()
    endgame_dict = parallel_generate_k_piece(3, manager, 4)
    end_time = time.time()
    print("Comsuming", end_time-start_time, "s")
    print(len(endgame_dict))
    assert len(endgame_dict) == 470180

    # with open("./deepdraughts/endgame/3p.pkl", "rb") as fp:
    #     basic_dict = pickle.load(fp)
    
    # for key, value in endgame_dict.items():
    #     if key in 


# def test_generate_two_kings_versus_one_king():
#     basic_dict = generate_basic_endgames()
#     endgame_dict = generate_two_kings_versus_one_king()

#     print(len(endgame_dict))
#     # assert len(endgame_dict) == 59672

#     for key, item in endgame_dict.items():
#         if key in basic_dict:
#             continue
#         print(key, item)
#         gui = GUI()
#         gui.game = Game.load_fen(key)
#         gui.run()

# def test_generate_three_kings_versus_one_king():
#     with open("two_kings_versus_one_king.pkl", "rb") as fp:
#         basic_dict = pickle.load(fp)

#     endgame_dict = generate_three_kings_versus_one_king()

#     print(len(endgame_dict))
#     assert len(endgame_dict) == 603628

#     for key, item in endgame_dict.items():
#         if key in basic_dict:
#             continue
#         print(key, item)
#         gui = GUI()
#         gui.game = Game.load_fen(key)
#         gui.run()

# def test_generate_one_versus_two():
#     with open("one_versus_one.pkl", "rb") as fp:
#         basic_dict = pickle.load(fp)

#     endgame_dict = generate_one_versus_two()

#     print(len(endgame_dict))
#     assert len(endgame_dict) == 870336

#     fen = "B:WD6:BB8,F8."
#     print(fen, endgame_dict[fen])
#     gui = GUI()
#     gui.game = Game.load_fen(fen)
#     gui.run()
    

#     for key, item in endgame_dict.items():
#         if key in basic_dict:
#             continue
#         print(key, item)
#         gui = GUI()
#         gui.game = Game.load_fen(key)
#         gui.run()

# def test_generate_two_versus_two():
#     with open("one_versus_two.pkl", "rb") as fp:
#         basic_dict = pickle.load(fp)

#     endgame_dict = generate_two_versus_two()

#     print(len(endgame_dict))

#     for key, item in endgame_dict.items():
#         if key in basic_dict:
#             continue
#         print(key, item)
#         gui = GUI()
#         gui.game = Game.load_fen(key)
#         gui.run()


if __name__ == "__main__":
    # test_generate_one_piece()
    # test_generate_two_piece()   
    # test_generate_three_piece()
    test_generate_four_piece()

    ## test parallel
    # import multiprocessing
    # from rwlock import RWLock
    # manager = multiprocessing.Manager()
    # endgame_lock_mananger, game_lock_mananger = RWLock(manager), RWLock(manager)
    # test_parallel_generate_three_piece((manager, endgame_lock_mananger, game_lock_mananger))
    

    ## Dont use them any more.
    # test_k_sum_combines(3)
    # test_generate_next_piece1()
    # test_generate_next_piece2()
    # test_generate_next_piece3()        
    
    # test_update1()
    # test_update2()
    # test_generate_two_kings_versus_one_king()
    # test_generate_three_kings_versus_one_king()
    
    # test_generate_one_versus_two()
    # test_generate_two_versus_two()
