"""
Contains game logic and AI
"""

import pygame as p
from win32api import GetSystemMetrics

WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)
BOARDGAP = HEIGHT // 10
SQ_SIZE = (HEIGHT - 2 * BOARDGAP) // 8



class GameState:
    def __init__(self, width, height, sq_size):
        self.width = width
        self.height = height
        self.squaresize = sq_size
        self.board = [
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', '--', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', '--', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr'],
        ]
        self.legal_moves = []
        self.move_log = []
        self.white_to_move = True
        self.white_castling_rights = [True, True]  # Queenside, Kingside
        self.black_castling_rights = [True, True]
        self.flip_board = False

    """
    MOVE
    """

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move



    def get_legal_moves(self, from_square):
        piece_type = self.board[from_square[1]][from_square[0]][1]
        if piece_type == 'p':
            self.get_pawn_moves(from_square)
        elif piece_type == 'r':
            self.get_rook_moves(from_square)
        elif piece_type == 'n':
            self.get_knight_moves(from_square)
        elif piece_type == 'b':
            self.get_bishop_moves(from_square)
        elif piece_type == 'q':
            self.get_queen_moves(from_square)
        elif piece_type == 'k':
            self.get_king_moves(from_square)

    def get_king_moves(self, square):
        legal = []
        directions = [[1, 0], [1, 1], [1, -1], [0, 1], [0, -1], [-1, 1], [-1, 0], [-1, -1]]
        for d in directions:
            new_row = square[1] + d[0]
            new_col = square[0] + d[1]
            if 0 <= new_col < 8 and 0 <= new_row < 8:
                enemy = 'b' if self.white_to_move else 'w'
                if self.board[new_row][new_col] == '--' or self.board[new_row][new_col][0] == enemy:
                    legal.append([new_col, new_row])

    def get_pawn_moves(self, square):
        legal = []
        pawn_direction = -1 if self.white_to_move else 1
        original_row = 6 if self.white_to_move else 1
        enemy = 'b' if self.white_to_move else 'w'
        new_row = square[1] + pawn_direction
        if 0 <= new_row < 8:
            if self.board[new_row][square[0]] == '--':
                legal.append([square[0], new_row])
            if square[1] == original_row:
                legal.append([square[0], square[1] + 2 * pawn_direction])
            sides = [-1, 1]
            for side in sides:
                new_col = square[0] + side
                if 0 <= new_col < 8:
                    if self.board[new_row][new_col][0] == enemy:
                        legal.append([new_col, new_row])

    def get_rook_moves(self, square):
        pass

    def get_bishop_moves(self, square):
        pass

    def get_knight_moves(self, square):
        pass

    def get_queen_moves(self, square):
        pass


class Move:

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

    def get_notation(self):
        piece = '' if self.piece_moved[1] == 'p' else self.piece_moved[1].upper()
        return piece + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]







