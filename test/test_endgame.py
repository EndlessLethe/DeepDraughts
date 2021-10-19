'''
Author: Zeng Siwei
Date: 2021-10-14 12:35:49
LastEditors: Zeng Siwei
LastEditTime: 2021-10-19 19:23:49
Description: 
'''

from pygame.event import wait
from deepdraughts.gui import GUI
from deepdraughts.env import *
from deepdraughts.endgame.generator import *
import queue
import time

def test_generate_one_piece():
    endgame_one_piece = generate_one_piece()
    print(len(endgame_one_piece))
    assert len(endgame_one_piece) == 120

    for key, item in endgame_one_piece.items():
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()
    
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
        is_valid_waiting_endgame(game, fen, endgame_dict)

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
        is_valid_waiting_endgame(game, fen, endgame_dict)

        # check whether is over and put status into dict
        update_dict_by_game_status(game, endgame_dict)

    print(len(endgame_dict))
    # assert len(endgame_dict) == 120

    for key, item in endgame_dict.items():
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()

def test_generate_basic_endgames():
    endgame_dict = generate_basic_endgames()
    for key, item in endgame_dict.items():
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()

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


def test_generate_two_kings_versus_one_king():
    basic_dict = generate_basic_endgames()
    endgame_dict = generate_two_kings_versus_one_king()

    print(len(endgame_dict))
    # assert len(endgame_dict) == 59672

    for key, item in endgame_dict.items():
        if key in basic_dict:
            continue
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()

def test_generate_three_kings_versus_one_king():
    with open("two_kings_versus_one_king.pkl", "rb") as fp:
        basic_dict = pickle.load(fp)

    endgame_dict = generate_three_kings_versus_one_king()

    print(len(endgame_dict))
    assert len(endgame_dict) == 603628

    for key, item in endgame_dict.items():
        if key in basic_dict:
            continue
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()


def test_generate_one_versus_one():
    start_time = time.time()
    with open("three_kings_versus_one_king.pkl", "rb") as fp:
        basic_dict = pickle.load(fp)

    endgame_dict = generate_one_versus_one()
    end_time = time.time()
    print("Comsuming", end_time-start_time, "s")

    print(len(basic_dict))
    print(len(endgame_dict))
    assert len(endgame_dict) == 607656

    for key, item in endgame_dict.items():
        if key in basic_dict:
            continue
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()
    


def test_generate_one_versus_two():
    with open("one_versus_one.pkl", "rb") as fp:
        basic_dict = pickle.load(fp)

    endgame_dict = generate_one_versus_two()

    print(len(endgame_dict))
    assert len(endgame_dict) == 870336

    fen = "B:WD6:BB8,F8."
    print(fen, endgame_dict[fen])
    gui = GUI()
    gui.game = Game.load_fen(fen)
    gui.run()
    

    for key, item in endgame_dict.items():
        if key in basic_dict:
            continue
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()

def test_generate_two_versus_two():
    with open("one_versus_two.pkl", "rb") as fp:
        basic_dict = pickle.load(fp)

    endgame_dict = generate_two_versus_two()

    print(len(endgame_dict))

    for key, item in endgame_dict.items():
        if key in basic_dict:
            continue
        print(key, item)
        gui = GUI()
        gui.game = Game.load_fen(key)
        gui.run()

if __name__ == "__main__":
    # test_generate_one_piece()
    # test_generate_next_piece1()
    # test_generate_next_piece2()                
    # test_generate_basic_endgames()
    # test_update1()
    # test_update2()
    # test_generate_two_kings_versus_one_king()
    # test_generate_three_kings_versus_one_king()
    # test_generate_one_versus_one()
    # test_generate_one_versus_two()
    test_generate_two_versus_two()
