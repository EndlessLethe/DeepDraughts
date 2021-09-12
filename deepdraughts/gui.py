'''
Author: Zeng Siwei
Date: 2021-09-11 15:56:20
LastEditors: Zeng Siwei
LastEditTime: 2021-09-13 00:01:03
Description: 
'''

import pygame as pg
from env.game import Game
from env.env_utils import *

def draw_background():
    color_idx = 0
    for i in range(0, screen_size, square_size):
        for j in range(0, screen_size, square_size):
            square = (i, j, square_size, square_size)
            pg.draw.rect(surface, square_colors[color_idx], square)
            color_idx ^= 1 
        color_idx ^= 1

    pg.draw.rect(surface, background_color, (screen_size, 0, text_size, screen_size))

def draw_pieces(pos_list, player_list, isking_list, nsize):
    for pos, player, isking in zip(pos_list, player_list, isking_list):
        row, col = pos2coord(pos, nsize, origin = "left_upper")
        x = (col-1) * square_size + piece_radius
        y = (row-1) * square_size + piece_radius
        pg.draw.circle(surface, COLOR_WHITE if player == WHITE else COLOR_BLACK, (x, y), piece_radius)
        if isking:
            pg.draw.circle(surface, COLOR_BLACK if player == WHITE else COLOR_BLACK, (x, y), king_radius1)
            pg.draw.circle(surface, COLOR_WHITE if player == WHITE else COLOR_BLACK, (x, y), king_radius2)


def draw_select(pos, nsize):
    row, col = pos2coord(pos, nsize, origin = "left_upper")
    x = (col-1) * square_size + piece_radius
    y = (row-1) * square_size + piece_radius
    pg.draw.circle(surface, COLOR_RED, (x, y), move_radius)

def draw_move(moves):
    pass
    # for move in moves:
    #     offset = coor_matrix[move[0]]
    #     offset_y, offset_x = (coord + offset) * square_size + piece_radius
    #     pg.draw.circle(surface, piece_colors[3], (offset_x, offset_y), move_radius)




screen_size, text_size = 800, 0
square_size = int(screen_size / 8)
piece_radius = int(square_size / 2)
king_radius1 = int(square_size / 3)
king_radius2 = int(square_size / 4)
move_radius = int(piece_radius / 6)

COLOR_WHITE = pg.Color('white')
COLOR_BLACK = pg.Color('black')
COLOR_YELLOW = pg.Color('yellow')
COLOR_RED = pg.Color('red')

square_colors = [pg.Color('gray'), pg.Color('brown')]

# piece_colors = [pg.Color('white'), pg.Color('black'), pg.Color('red'), pg.Color('yellow'), pg.Color('black'), pg.Color('white')]
background_color = pg.Color('#8EA2F3')


pg.init()
screen = pg.display.set_mode((screen_size + text_size, screen_size))
surface = pg.Surface((screen_size + text_size, screen_size))
pg.display.set_caption('DeepDraughts')
clock = pg.time.Clock()

pg.font.init()
font = pg.font.Font(None, 36)

game = Game()



selected_pos = None
take_piece = False
next_moves = []

def reset_drawing():
    global selected_pos
    global take_piece
    global next_moves
    selected_pos = None
    take_piece = False
    next_moves = []

running = True
while running:
    pieces = game.current_board.get_pieces()
    pos_list = [x.pos for x in pieces]
    player_list = [x.player for x in pieces]
    isking_list = [x.isking for x in pieces]
    available_moves = game.get_all_available_moves()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1: # left click of mouse
                # compute click info
                mouse_y, mouse_x = event.pos
                row = int(mouse_x / square_size) + 1
                col = int(mouse_y / square_size) + 1
                
                pos = coord2pos(row, col, game.current_board.nsize, "left_upper")
                print(mouse_y, mouse_x, row, col, pos)

                # if move piece
                for move in next_moves:
                    if pos == move.moves[-1]:
                        game.move(move)
                        print(str(game))
                        # reset last action
                        reset_drawing()
                        continue

                # reset last action
                reset_drawing()

                # select piece
                if pos in pos_list:
                    if game.current_board.pieces[pos].player != game.current_player:
                        continue

                    # show available moves.
                    for move in available_moves:
                        if pos == move.moves[-2]:
                            next_moves.append(move)
                    if len(next_moves) >= 1:
                        selected_pos = pos

            elif event.button == 3: # right click of mouse
                # reset last action
                reset_drawing()
    
    draw_background()
    draw_pieces(pos_list, player_list, isking_list, game.current_board.nsize)
    if selected_pos is not None and next_moves:
        for move in next_moves:
            pos = move.moves[-1]
            draw_select(pos, game.current_board.nsize)
    else:
        for move in available_moves:
            pos = move.moves[-1]
            draw_select(pos, game.current_board.nsize)
    screen.blit(surface, (0, 0))
    pg.display.flip()
    clock.tick(500)

pg.quit()