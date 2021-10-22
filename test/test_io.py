'''
Author: Zeng Siwei
Date: 2021-10-19 23:40:13
LastEditors: Zeng Siwei
LastEditTime: 2021-10-21 16:00:05
Description: 
'''


from deepdraughts.env.py_env.io_utils import *
from deepdraughts.env import *
from deepdraughts.gui import GUI

def test_parse_fen():
    FEN_INITIAL = "W:B1-20:W31-50"
    FEN_1 = "W:W15,19,24,29,32,41,49,50:B5,8,30,35,37,40,42,45."  # P.Lauwen, DP, 4/1977
    FEN_2 = "W:W17,28,32,33,38,41,43:B10,18-20,23,24,37."
    FEN_3 = "W:WK3,25,34,45:B38,K47."
    FEN_4 = "W:W18,23,31,33,34,39,47:B8,11,20,24,25,26,32."       # M.Dalman
    FEN_5 = "B:B7,11,13,17,20,22,24,30,41:W26,28,29,31,32,33,38,40,48."  # after 30-35 white wins
    FEN_5 = "B:B7,11,13,17,20,22,24,30,41:W26,28,29,31,32,33,38,40,48."  # after 30-35 white wins
    FEN_6 = "W:WA1,C3:BD4"
    FEN_7 = "W:WKA1,C3:BD4"
    print(parse_fen(FEN_INITIAL))
    print(parse_fen(FEN_1))
    print(parse_fen(FEN_2))
    print(parse_fen(FEN_3))
    print(parse_fen(FEN_4))
    print(parse_fen(FEN_5))
    print(parse_fen(FEN_6))
    print(parse_fen(FEN_7))

def test_load_fen():
    # fen = "B:WD6:BB8,F8."
    fen = "W:WKG7:BH6,KD2."
    print(fen)
    gui = GUI()
    gui.game = Game.load_fen(fen)
    gui.run()

if __name__ == "__main__":
    # test_parse_fen()
    test_load_fen()