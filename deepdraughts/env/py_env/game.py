'''
Author: Zeng Siwei
Date: 2021-09-11 16:20:41
LastEditors: Zeng Siwei
LastEditTime: 2021-10-25 18:50:49
Description: 
'''

from .board import Board, Move
from .env_utils import *
from .io_utils import parse_fen, game_to_fen
import pickle

class Game():
    def __init__(self, player1_name = "player1", player2_name = "player2", ngrid = CONST_N_GRID_64, rule = RUSSIAN_RULE, init_board = True) -> None:
        # necessary part to describe a game
        self.current_player = WHITE
        self.current_board = Board(ngrid, rule)
        if init_board:
            self.current_board.init_default_board()
        self.is_chain_taking = False
        self.chain_taking_piece_pos = None
        self.chain_taking_pos = []
        self.n_king_move = 0

        # non-necessary part
        self.move_path = []
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.chain_taking_moves = []
        self.game_status = self.query_game_status()
        self.available_moves = None

    def reset_available_moves(self):
        self.available_moves = None

    def reset_chain_taking_states(self):
        self.is_chain_taking = False
        self.chain_taking_moves = []
        self.chain_taking_pos = []
        self.chain_taking_piece_pos = None
        
    def do_move(self, move):
        self.current_board.do_move(move)
        self.move_path.append(move)
        self.reset_available_moves()
        
        if move.move_type == MEN_MOVE:
            self.n_king_move = 0
        else:
            self.n_king_move += 1

        # check whether in chain-taking
        # only when chain-taking, keep current player playing
        if move.take_piece:
            # check whether the player can take another piece after this move.
            self.chain_taking_moves.append(move)
            self.chain_taking_pos.append(move.taken_pos)
            self.chain_taking_piece_pos = move.pos[-1]

            can_take_piece = False
            king_jumps, jumps, _ = self.current_board.get_available_moves(move.pos[-1])

            if len(jumps) >= 1:
                can_take_piece = True
            else:
                # check whether king go over the same piece
                king_jumps = self.remove_jump_over_twice_moves(king_jumps)
                can_take_piece = len(king_jumps) >= 1

            if can_take_piece:
                # 连吃 chain-taking
                self.is_chain_taking = True
                return GAME_CONTINUE

        self.change_player()
        self.reset_chain_taking_states()
        self.game_status = self.query_game_status()
        return self.game_status
        
    def query_game_status(self):
        '''
        Return current game status. 

        Note: 
            This function doesn't return True or False.
            Returns may be different from is_over or is_drawn, 
                due to the applied endgame database.

        Usage:
            game_status = game.query_game_status()
            is_over = game_is_over(game_status)
            is_drawn = game_is_drawn(game_status)
            winner = game_winner(game_status)

        '''
        if is_using_endgame_database() and (not self.is_chain_taking) and self.current_board.number_of_pieces() <= K_ENDGAME_PIECE:
            endgame_database = get_endgame_database()
            fen = self.to_fen()
            if fen in endgame_database:
                status, n_moves = endgame_database[fen]
                if status == CONST_TOKEN_DRAW:
                    return GAME_DRAW
                elif status == CONST_TOKEN_WIN:
                    return GAME_WHITE_WIN
                elif status == CONST_TOKEN_LOSE:
                    return GAME_BLACK_WIN
            else:
                # pass
                print(fen, "not in endgame database.")
                import time
                time.sleep(1)

        if not self.has_available_moves():
            return GAME_WHITE_WIN if self.current_player == BLACK else GAME_BLACK_WIN
        elif not self.opponent_has_piece():
            return GAME_WHITE_WIN if self.current_player == WHITE else GAME_BLACK_WIN
        elif self.is_drawn():
            return GAME_DRAW
        else:
            return GAME_CONTINUE

    def opponent_has_piece(self):
        cnt = 0
        for pos, piece in self.current_board.pieces.items():
            if piece.player != self.current_player:
                cnt += 1
        return cnt >= 1

    def is_over(self):
        return (not self.has_available_moves()) or self.is_drawn()

    def has_available_moves(self):
        has_available_moves = False
        for pos, piece in self.current_board.pieces.items():
            if piece.player != self.current_player:
                continue
            king_jumps_tmp, jumps_tmp, normals_tmp = self.current_board.get_available_moves(pos)
            if len(king_jumps_tmp) + len(jumps_tmp) + len(normals_tmp) >= 1:
                has_available_moves = True
                break
        return has_available_moves

    def is_drawn(self):
        '''
        Here I just implement the only one basic rules about drawn:
        - If both players play 15 kingmoves (any king) without captures or moving men, the game is drawn.
        '''        
        if self.n_king_move >= 30:
            return True
        return False

    def remove_jump_over_twice_moves(self, king_jumps):
        chain_taking_pos = set(self.chain_taking_pos)
        # check whether go over the same piece
        list_jumps = []
        for king_jump in king_jumps:
            if not is_jump_over_twice(king_jump, chain_taking_pos):
                list_jumps.append(king_jump)
        return list_jumps

    def get_all_available_moves(self):
        # TODO Brazilian rule 有多吃多
        if self.available_moves is not None:
            return self.available_moves

        if self.is_chain_taking:
            # last move's pos_to
            king_jumps, jump_moves, normal_moves = self.current_board.get_available_moves(self.chain_taking_piece_pos)
            king_jumps = self.remove_jump_over_twice_moves(king_jumps)

        else:
            king_jumps, jump_moves, normal_moves = [], [], []
            for pos, piece in self.current_board.pieces.items():
                if piece.player != self.current_player:
                    continue
                king_jumps_tmp, jumps_tmp, normals_tmp = self.current_board.get_available_moves(pos)
                king_jumps.extend(king_jumps_tmp)
                jump_moves.extend(jumps_tmp)
                normal_moves.extend(normals_tmp)

        if len(king_jumps)  == 0:
            self.available_moves = jump_moves if len(jump_moves) >= 1 else normal_moves
            return self.available_moves

        # king jump must be carefully dealt when chain-taking:
        # if king can take a piece, and after this move another piece can be taken,
        # only continueing chain-taking is available.
        king_chain_takings = []
        king_normal_jumps = []
        for king_jump in king_jumps:
            board_tmp = pickle.loads(pickle.dumps(self.current_board, -1))
            board_tmp.do_move(king_jump)
            tmp_king_jumps, tmp_jump_moves, _ = board_tmp.get_available_moves(king_jump.pos[-1])
            tmp_king_jumps = self.remove_jump_over_twice_moves(tmp_king_jumps)
            can_take_piece = (len(tmp_king_jumps) + len(tmp_jump_moves)) >= 1
            if can_take_piece:
                king_chain_takings.append(king_jump)
            else:
                king_normal_jumps.append(king_jump)

        self.available_moves = king_chain_takings if len(king_chain_takings) >= 1 else king_normal_jumps
        self.available_moves.extend(jump_moves)
        return self.available_moves

    def change_player(self):
        self.current_player = WHITE if self.current_player == BLACK else BLACK

    def to_vector(self):
        return state2vec(self)

    '''

    IO functions.
            
    '''    

    def load_game(self, filepath):
        # TODO add guess_taken_piece() for read human files.
        with open(filepath, "r") as fp:
            str_moves = fp.readline().split(",")
            for str_move in str_moves:
                move = Move.init_by_str(str_move)
                print(str(move))

    def to_fen(self):
        current_player = "W" if self.current_player == WHITE else "B"
        is_chain_taking = self.is_chain_taking
        chain_taking_piece_pos = to_readable_pos(self.chain_taking_piece_pos) \
                                    if self.chain_taking_piece_pos is not None else None
        chain_taking_pos = to_readable_pos_list(self.chain_taking_pos)
        whites_pos, blacks_pos, whites_isking, blacks_isking = [], [], [], []
        sorted_items = sorted(self.current_board.pieces.items(), key=lambda item:item[0])
        for pos, piece in sorted_items:
            if piece.player == WHITE:
                whites_pos.append(pos)
                whites_isking.append(piece.isking)
            elif piece.player == BLACK:
                blacks_pos.append(pos)
                blacks_isking.append(piece.isking)
        whites_pos = to_readable_pos_list(whites_pos)
        blacks_pos = to_readable_pos_list(blacks_pos)
        return game_to_fen(current_player, whites_pos, blacks_pos, whites_isking, 
            blacks_isking, is_chain_taking, chain_taking_piece_pos, chain_taking_pos)

    @classmethod
    def load_fen(cls, fen):
        current_player, whites_pos, blacks_pos, whites_isking, \
                blacks_isking, is_chain_taking, chain_taking_piece_pos, chain_taking_pos = parse_fen(fen)
        game = Game(init_board = False)
        game.current_player = WHITE if current_player.lower() == "w" else BLACK
        game.is_chain_taking = is_chain_taking
        game.chain_taking_piece_pos = read_input_pos(chain_taking_piece_pos)
        game.chain_taking_pos = norm_pos_list(chain_taking_pos)
        whites_pos = norm_pos_list(whites_pos)
        blacks_pos = norm_pos_list(blacks_pos)
        game.current_board.set_board(whites_pos, blacks_pos, whites_isking, blacks_isking)
        return game

    @classmethod
    def load_pickled_game(cls, filepath):
        with open(filepath, "rb") as fp:
            game = pickle.load(fp)
            return game
    
    @classmethod
    def save_pickled_game(cls, game, filepath):
        with open(filepath, "wb") as wfp:
            pickle.dump(game, wfp)

    # def  __repr__(self):
    #     # TODO
    #     pass

    def __str__(self):
        return ", ".join(str(x) for x in self.move_path).strip(", ")
