import copy
import numpy as np
cimport numpy as np

from .env_utils import *

cdef extern from "math.h":
    double sqrt(double theta)

cdef class Piece():
    cdef public int player
    cdef public int pos
    cdef public int isking
    cdef public int captured
    cdef public set KING_POS_WHITE
    cdef public set KING_POS_BLACK
        
    def __init__(self, int player, int pos, int isking, set KING_POS_WHITE, set KING_POS_BLACK):
        self.player = player # white 1 black -1
        self.pos = pos
        self.isking = isking
        self.captured = False
        self.KING_POS_WHITE = KING_POS_WHITE
        self.KING_POS_BLACK = KING_POS_BLACK

    cpdef void move_to(self, int pos):
        '''
        Args: 
            pos: pos to move. Make sure it's available.
        '''        
        self.pos = pos
        if not self.isking:
            if self.player == WHITE and pos in self.KING_POS_WHITE:
                self.king_promote()
            if self.player == BLACK and pos in self.KING_POS_BLACK:
                self.king_promote()


    cpdef void king_promote(self):
        self.isking = True
    
cdef class Move():
    cdef public tuple pos
    cdef public str direction
    cdef public int force
    cdef public int take_piece
    cdef public int taken_pos
    cdef public int move_type
    
    
    def __init__(self, int pos_from, int pos_to, str direction, int move_type = MEN_MOVE, 
                int take_piece = False, int taken_pos = -1, int force = False) -> None:
        self.pos = (pos_from, pos_to)
        self.direction = direction
        self.force = force
        self.take_piece = take_piece
        self.taken_pos = taken_pos
        self.move_type = move_type
    
    def __str__(self):
        if self.force:
            return "->".join([str(x) for x in self.pos])
        if self.take_piece:
            return "x".join([str(x) for x in self.pos])
        return "-".join([str(x) for x in self.pos])

cdef class Board():
    cdef public dict pieces
    cdef public int ngrid
    cdef public int rule
    cdef public dict piece_moves
    cdef public list all_king_jumps
    cdef public list all_jump_moves
    cdef public list all_normal_moves
    cdef public int nsize
    
    
    def __init__(self, int ngrid = N_GRID_64, int rule = RUSSIAN_RULE) -> None:
        self.pieces = dict() # key - value: pos - piece
        self.ngrid = ngrid
        self.rule = rule
        self.piece_moves = dict()
        self.all_king_jumps = []
        self.all_jump_moves = []
        self.all_normal_moves = []

        cdef int n
        
        n = int(sqrt(ngrid))
        if n * n != ngrid:
            raise Exception("N_grid is not squre number.")
        self.nsize = n
        

    '''
    Load gloval vars
    '''    

    def get_king_promotion_pos(self):
        return globals()["KING_POS_WHITE_" + str(self.ngrid)], globals()["KING_POS_BLACK_" + str(self.ngrid)]


    def get_default_pos(self):
        return globals()["DEFAULT_POS_WHITE_" + str(self.ngrid)], globals()["DEFAULT_POS_BLACK_" + str(self.ngrid)]

    def get_edge_pos(self):
        return globals()["EDGE_POS_" + str(self.ngrid)]

    def get_valid_pos(self):
        return globals()["VALID_POS_" + str(self.ngrid)]

    '''
    Update board
    '''    
    cpdef void reset_available_moves(self):
        self.piece_moves.clear()
        self.all_king_jumps.clear()
        self.all_jump_moves.clear()
        self.all_normal_moves.clear()

    def set_board(self, list whites_pos, list blacks_pos, whites_isking = None, blacks_isking = None):
        whites_pos = norm_pos_list(whites_pos)
        blacks_pos = norm_pos_list(blacks_pos)
        if (self.check_pos_list(whites_pos) and self.check_pos_list(blacks_pos)) == False:
            raise Exception("Invaid pos list")
        if whites_isking is None:
            whites_isking = [False] * len(whites_pos)
        if blacks_isking is None:
            blacks_isking = [False] * len(blacks_pos)

        for pos, isking in zip(whites_pos, whites_isking):
            self.pieces[pos] = Piece(WHITE, pos, isking, *self.get_king_promotion_pos())
        for pos, isking in zip(blacks_pos, blacks_isking):
            self.pieces[pos] = Piece(BLACK, pos, isking, *self.get_king_promotion_pos())
        self.reset_available_moves()

    cpdef void init_empty_board(self):
        self.pieces.clear()
        self.reset_available_moves()

    cpdef void init_default_board(self):
        self.set_board(*self.get_default_pos())

    cpdef check_pos_list(self, list pos_list):
        cdef int is_ok, pos, x, y
        is_ok = True
        for pos in pos_list:
            if pos not in globals()["VALID_POS_" + str(self.ngrid)]:
                x, y = pos2coord(pos, self.ngrid)
                print("Invalid pos:", pos, "row:", x, "col:", y)
                is_ok = False
        return is_ok

    
    cpdef do_move(self, Move move):
        self.move(move.pos[-2], move.pos[-1], move.taken_pos)

    cpdef move(self, int pos_from, int pos_to, int taken_pos = -1):
        '''
        Move the piece in pos_from to pos_to.
        '''
        cdef Piece piece
        
        if pos_from not in self.pieces or pos_to in self.pieces:
            raise Exception("Invalid move operation. From", pos_from, "to", pos_to)
        piece = self.pieces.pop(pos_from)
        piece.move_to(pos_to)
        self.pieces[pos_to] = piece
        if taken_pos != -1:
            self.pieces.pop(taken_pos)
        self.reset_available_moves()


    '''
    Querying states
    '''    
    def number_of_pieces(self):
        return len(self.pieces)

    cpdef list get_pieces(self):
        return [x for x in self.pieces.values()]

    def get_available_moves(self, int pos):
        if pos in self.piece_moves:
            return self.piece_moves[pos]
        
        cdef list king_jump_moves, jump_moves, normal_moves, tmp_normal,tmp_jump
        cdef Piece piece
        cdef dict dict_pos
        cdef str key
        
        king_jump_moves = []
        jump_moves = []
        normal_moves = []
        
        piece = self.pieces[pos]
        
        # normal piece
        if piece.isking == False:
            dict_pos = KHOP_POS_64[pos]

            # jump moves
            for key in HOP_POS_ARGS:
                next_pos = dict_pos[key][0]
                jump_pos = dict_pos[key][1]

                # make sure move is valid
                if next_pos is None or jump_pos is None:
                    continue
                
                # 如果周围有子，其后方没有子，且异色
                if next_pos in self.pieces and jump_pos not in self.pieces and self.pieces[next_pos].player != piece.player:
                    jump_moves.append(Move(pos, jump_pos, key, MEN_MOVE, True, next_pos))
            
            # normal moves
            for key in HOP_POS_ARGS:
                next_pos = dict_pos[key][0]
                if next_pos is None:
                    continue
                if piece.player == WHITE and next_pos > pos: # 不能往回走
                    continue
                if piece.player == BLACK and next_pos < pos:
                    continue
                
                if next_pos not in self.pieces:
                    normal_moves.append(Move(pos, next_pos, key, MEN_MOVE))

        # king moves
        else:
            dict_pos = KHOP_POS_64[pos]
            
            for key in HOP_POS_ARGS:
                # for each direction, check:
                # 1. same color, if true, break
                # 2. diff color, if true, go step 3
                # 3. any space behind this diff piece, go futher util meet any piece.
                tmp_normal = []
                tmp_jump = []
                meet_diff_color = None # meet pos id
                for i in range(self.nsize):
                    next_pos = dict_pos[key][i]
                    if next_pos is None:
                        break
                    # meet piece and check color
                    if next_pos in self.pieces:
                        # same color
                        if self.pieces[next_pos].player == piece.player:
                            break
                        # diff color
                        else:
                            if meet_diff_color is not None:
                                break
                            else:
                                meet_diff_color = next_pos
                    # find a place where can jump to
                    else:
                        if meet_diff_color is not None:
                            tmp_jump.append(Move(pos, next_pos, key, KING_MOVE, True, meet_diff_color))
                        else:
                            tmp_normal.append(Move(pos, next_pos, key, KING_MOVE))
                
                # deal each direction
                king_jump_moves.extend(tmp_jump)
                normal_moves.extend(tmp_normal)


        self.piece_moves[pos] = (king_jump_moves, jump_moves, normal_moves)
        return king_jump_moves, jump_moves, normal_moves


    def get_all_available_moves_board(self, int current_player):
        '''
        Args: 
		
        Returns: 
            take_piece: Bool
            next_moves: List
        '''
        if len(self.all_king_jumps) + len(self.all_jump_moves) + len(self.all_normal_moves) >= 1:
            return self.all_king_jumps, self.all_jump_moves, self.all_normal_moves
        
        cdef list all_king_jumps, all_jump_moves, all_normal_moves, king_jump_moves, jump_moves, normal_moves
        cdef int pos
        
        all_king_jumps = []
        all_jump_moves = []
        all_normal_moves = []
        for pos in self.pieces:
            if self.pieces[pos].player != current_player:
                continue
            king_jump_moves, jump_moves, normal_moves = self.get_available_moves(pos)
            all_king_jumps.extend(king_jump_moves)
            all_jump_moves.extend(jump_moves)
            all_normal_moves.extend(normal_moves)

        self.all_king_jumps = all_king_jumps
        self.all_jump_moves = all_jump_moves
        self.all_normal_moves = all_normal_moves
        return all_king_jumps, all_jump_moves, all_normal_moves
        

cdef class Game():
    
    cdef public list move_path
    cdef public str player1_name
    cdef public str player2_name
    cdef public Board current_board
    cdef public int current_player
    cdef public list available_moves
    cdef public int n_king_move

    cdef public int is_chain_taking
    cdef public list chain_taking_moves
    
    def __init__(self, str player1_name = "player1", str player2_name = "player2", int ngrid = N_GRID_64, int rule = RUSSIAN_RULE) -> None:
        self.move_path = []
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.current_board = Board(ngrid, rule)
        self.current_player = WHITE

        self.current_board.init_default_board()
        self.available_moves = []
        self.n_king_move = 0

        self.is_chain_taking = False
        self.chain_taking_moves = []

    cpdef void reset_available_moves(self):
        self.available_moves = []

    cpdef void reset_chain_taking_states(self):
        self.is_chain_taking = False
        self.chain_taking_moves = []

    cpdef int do_move(self, Move move):
        cdef list king_jumps, jumps, list_remove
        cdef Move king_jump, tmp_move
        cdef int pos_a, pos_b, pos_c, can_take_piece, is_over
        
        self.current_board.do_move(move)
        self.move_path.append(move)
        self.reset_available_moves()
        
        if move.move_type == MEN_MOVE:
            self.n_king_move = 0
        else:
            self.n_king_move += 1

        # check whether the player can take another piece after this move.
        king_jumps, jumps, _ = self.current_board.get_available_moves(move.pos[-1])

        # The folling code block is the same with get_all_available_moves()
        # for checking whether go over the same piece
        if king_jumps:
            list_remove = []
            for king_jump in king_jumps:
                if is_opposite_direcion(king_jump.direction, move.direction):
                    pos_a = move.pos[-2]
                    pos_b = move.pos[-1]
                    pos_c = king_jump.pos[-1]
                    if not ((pos_a > pos_b and pos_b > pos_c) or (pos_a < pos_b and pos_b < pos_c)):
                        list_remove.append(king_jump)
            for tmp_move in list_remove:
                king_jumps.remove(tmp_move)

        can_take_piece = (len(king_jumps) + len(jumps)) >= 1
        if move.take_piece and can_take_piece:
            # 连吃 chain-taking
            self.is_chain_taking = True
            self.chain_taking_moves = [move]
        else:
            self.change_player()
            self.reset_chain_taking_states()

        is_over, winner = self.is_over()
        if is_over:
            if winner == None:
                return GAME_DRAW
            return GAME_WHITE_WIN if winner == WHITE else GAME_BLACK_WIN
        return GAME_CONTINUE

    def is_over(self):
        cdef list available_moves
        
        available_moves = self.get_all_available_moves()
        if len(available_moves) == 0:
            return True, WHITE if self.current_player == BLACK else BLACK
        elif self.is_drawn():
            return True, None
        else:
            return False, None

    cpdef int is_drawn(self):
        '''
        Here I just implement the only one basic rules about drawn:
        - If both players play 15 kingmoves (any king) without captures or moving men, the game is drawn.
        '''        
        if self.n_king_move >= 30:
            return True
        return False

    cpdef list get_all_available_moves(self):
        cdef Move last_move, king_jump
        cdef list king_jumps, jump_moves, normal_moves, list_remove, king_chain_takings, king_normal_jumps, tmp_king_jumps, tmp_jump_moves
        cdef int pos_a, pos_b, pos_c, can_take_piece
        cdef Board board_tmp
        
        # TODO Brazilian rule 有多吃多
        if len(self.available_moves) >= 1:
            return self.available_moves

        if self.is_chain_taking:
            # last move's pos_to
            last_move = self.chain_taking_moves[-1]
            king_jumps, jump_moves, normal_moves = self.current_board.get_available_moves(last_move.pos[-1])
            
            # check whether go over the same piece
            # 1. whether the opposite direction. if false, it's ok
            # 2. if true, whether the pos is mono. if true, it's ok
            # 3. if false, remove this move
            list_remove = []
            for king_jump in king_jumps:
                if is_opposite_direcion(king_jump.direction, last_move.direction):
                    pos_a = last_move.pos[-2]
                    pos_b = last_move.pos[-1]
                    pos_c = king_jump.pos[-1]
                    if not ((pos_a > pos_b and pos_b > pos_c) or (pos_a < pos_b and pos_b < pos_c)):
                        list_remove.append(king_jump)
            for move in list_remove:
                king_jumps.remove(move)

        else:
            king_jumps, jump_moves, normal_moves = self.current_board.get_all_available_moves_board(self.current_player)

        if len(king_jumps)  == 0:
            self.available_moves = jump_moves if len(jump_moves) >= 1 else normal_moves
            return self.available_moves

        # king jump must be carefully dealt when chain-taking:
        # if king can take a piece, and after this move another piece can be taken,
        # only continueing chain-taking is available.
        king_chain_takings = []
        king_normal_jumps = []
        for king_jump in king_jumps:
            board_tmp = copy.deepcopy(self.current_board)
            board_tmp.do_move(king_jump)
            tmp_king_jumps, tmp_jump_moves, _ = board_tmp.get_available_moves(king_jump.pos[-1])
            can_take_piece = (len(tmp_king_jumps) + len(tmp_jump_moves)) >= 1
            if can_take_piece:
                king_chain_takings.append(king_jump)
            else:
                king_normal_jumps.append(king_jump)

        self.available_moves = king_chain_takings if len(king_chain_takings) >= 1 else king_normal_jumps
        self.available_moves.extend(jump_moves)
        return self.available_moves

    cpdef void change_player(self):
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        self.current_board.reset_available_moves()
        self.reset_available_moves()
        self.is_chain_taking = False

    def to_vector(self):
        return state2vec(self)

    def __str__(self):
        return ", ".join(str(x) for x in self.move_path).strip(", ")