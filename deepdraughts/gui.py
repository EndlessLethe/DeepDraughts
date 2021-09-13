'''
Author: Zeng Siwei
Date: 2021-09-11 15:56:20
LastEditors: Zeng Siwei
LastEditTime: 2021-09-13 11:44:54
Description: 
'''

import pygame as pg
from env.game import Game
from env.env_utils import *

class GUI():
    COLOR_WHITE = pg.Color('white')
    COLOR_BLACK = pg.Color('black')
    COLOR_YELLOW = pg.Color('yellow')
    COLOR_RED = pg.Color('red')

    SQUARE_COLORS = [pg.Color('gray'), pg.Color('brown')]
    BACKGROUND_COLOR = pg.Color('#8EA2F3')
    
    def __init__(self, screen_size = 800, text_size = 0):
        self.screen_size = screen_size
        self.text_size = text_size
        self.square_size = int(screen_size / 8)
        self.piece_radius = int(self.square_size / 2)
        self.king_radius1 = int(self.square_size / 3)
        self.king_radius2 = int(self.square_size / 4)
        self.move_radius = int(self.piece_radius / 6)

        # pygame states
        self.screen = None
        self.surface = None

        # interaction states
        self.selected_pos = None
        self.take_piece = False
        self.next_moves = []

    def draw_background(self):
        color_idx = 0
        for i in range(0, self.screen_size, self.square_size):
            for j in range(0, self.screen_size, self.square_size):
                square = (i, j, self.square_size, self.square_size)
                pg.draw.rect(self.surface, self.SQUARE_COLORS[color_idx], square)
                color_idx ^= 1 
            color_idx ^= 1

        pg.draw.rect(self.surface, self.BACKGROUND_COLOR, (self.screen_size, 0, self.text_size, self.screen_size))

    def draw_pieces(self, pos_list, player_list, isking_list, nsize):
        for pos, player, isking in zip(pos_list, player_list, isking_list):
            row, col = pos2coord(pos, nsize, origin = "left_upper")
            x = (col-1) * self.square_size + self.piece_radius
            y = (row-1) * self.square_size + self.piece_radius
            pg.draw.circle(self.surface, self.COLOR_WHITE if player == WHITE else self.COLOR_BLACK, 
                            (x, y), self.piece_radius)
            if isking:
                pg.draw.circle(self.surface, self.COLOR_BLACK if player == WHITE else self.COLOR_BLACK, 
                                (x, y), self.king_radius1)
                pg.draw.circle(self.surface, self.COLOR_WHITE if player == WHITE else self.COLOR_BLACK, 
                                (x, y), self.king_radius2)


    def draw_select(self, pos, nsize):
        row, col = pos2coord(pos, nsize, origin = "left_upper")
        x = (col-1) * self.square_size + self.piece_radius
        y = (row-1) * self.square_size + self.piece_radius
        pg.draw.circle(self.surface, self.COLOR_RED, (x, y), self.move_radius)

    def draw_move(self, moves):
        pass

    def reset_drawing(self):
        self.selected_pos = None
        self.take_piece = False
        self.next_moves = []

    def listen_human_action(self, event):
        if event.type == pg.QUIT:
            return GUI_EXIT, ()
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1: # left click of mouse
                # compute click info
                mouse_y, mouse_x = event.pos
                return GUI_LEFTCLICK, (mouse_y, mouse_x)
            elif event.button == 3: # right click of mouse
                return GUI_RIGHTCLICK, ()
        return GUI_WAIT, ()

    def update_by_human_action(self, action, info, game, pos_list, available_moves):
        if action == GUI_RIGHTCLICK:
            self.reset_drawing()
            return

        if action == GUI_LEFTCLICK:
            mouse_y, mouse_x = info
            row = int(mouse_x / self.square_size) + 1
            col = int(mouse_y / self.square_size) + 1
            
            pos = coord2pos(row, col, game.current_board.nsize, "left_upper")
            print(mouse_y, mouse_x, row, col, pos)

            # if move piece
            for move in self.next_moves:
                if pos == move.moves[-1]:
                    game.move(move)
                    print(str(game))
                    # reset last action
                    self.reset_drawing()
                    return

            # reset last action
            self.reset_drawing()

            # select piece
            if pos in pos_list:
                if game.current_board.pieces[pos].player != game.current_player:
                    return

                # show available moves.
                for move in available_moves:
                    if pos == move.moves[-2]:
                        self.next_moves.append(move)
                if len(self.next_moves) >= 1:
                    self.selected_pos = pos

    def is_human_playing(self, game, player_white, player_black):
        return (game.current_player == WHITE and player_white == HUMAN_PLAYER) or \
                (game.current_player == BLACK and player_black == HUMAN_PLAYER)

    def run(self, player_white = HUMAN_PLAYER, player_black = HUMAN_PLAYER, 
            policy_white = None, policy_black = None):
        pg.init()
        self.screen = pg.display.set_mode((self.screen_size + self.text_size, self.screen_size))
        self.surface = pg.Surface((self.screen_size + self.text_size, self.screen_size))
        pg.display.set_caption('DeepDraughts')
        clock = pg.time.Clock()

        pg.font.init()
        font = pg.font.Font(None, 36)

        game = Game()
        
        running = True
        while running:
            # quering current states for each frame
            pieces = game.current_board.get_pieces()
            pos_list = [x.pos for x in pieces]
            player_list = [x.player for x in pieces]
            isking_list = [x.isking for x in pieces]
            available_moves = game.get_all_available_moves()

            if self.is_human_playing(game, player_white, player_black):
                for event in pg.event.get():
                    human_action, info = self.listen_human_action(event)
                    if human_action == GUI_EXIT:
                        running = False
                    elif human_action == GUI_WAIT:
                        continue
                    self.update_by_human_action(human_action, info, game, pos_list, available_moves)
            else:
                policy = policy_white if game.current_player == WHITE else policy_black
                # TODO

            self.draw_background()
            self.draw_pieces(pos_list, player_list, isking_list, game.current_board.nsize)
            
            if self.selected_pos is not None and self.next_moves:
                for move in self.next_moves:
                    pos = move.moves[-1]
                    self.draw_select(pos, game.current_board.nsize)
            else:
                for move in available_moves:
                    pos = move.moves[-1]
                    self.draw_select(pos, game.current_board.nsize)
            
            self.screen.blit(self.surface, (0, 0))
            pg.display.flip()
            clock.tick(500)

        pg.quit()

if __name__ == "__main__":
    gui = GUI()
    gui.run()