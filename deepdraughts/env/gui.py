'''
Author: Zeng Siwei
Date: 2021-09-11 15:56:20
LastEditors: Zeng Siwei
LastEditTime: 2021-09-12 00:17:54
Description: 
'''

import pygame as pg
from game import Game
from utils import *

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

running = True
while running:
    pieces = game.current_board.get_pieces()
    pos_list = [x.pos for x in pieces]
    player_list = [x.player for x in pieces]
    isking_list = [x.isking for x in pieces]
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
                if pos in next_moves:
                    game.move(selected_pos, pos, take_piece = take_piece)
                    continue

                # reset last action
                selected_pos = None
                take_piece = False
                next_moves = []

                # select piece
                if pos in pos_list:
                    selected_pos = pos

                    # show available moves.
                    jump_moves, normal_moves = game.current_board.get_available_moves(pos)
                    if len(jump_moves) >= 1:
                        take_piece = True
                        for nextpos in jump_moves:
                            next_moves.append(nextpos)
                    else:
                        for nextpos in normal_moves:
                            next_moves.append(nextpos)
                    print(jump_moves)
                    print(normal_moves)

            elif event.button == 3: # right click of mouse
                # reset last action
                selected_pos = None
                take_piece = False
                next_moves = []
    
    draw_background()
    draw_pieces(pos_list, player_list, isking_list, game.current_board.nsize)
    if next_moves:
        for pos in next_moves:
            draw_select(pos, game.current_board.nsize)
    # draw_move(possible_moves)
    screen.blit(surface, (0, 0))
    pg.display.flip()
    clock.tick(50)

pg.quit()