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
        self.mouse_clicks = []
        self.legal_moves = []
        self.white_to_move = True

    def mouseclicks(self, pos):
        if BOARDGAP < pos[0] < BOARDGAP + 8 * SQ_SIZE and BOARDGAP < pos[1] < BOARDGAP + 8 * SQ_SIZE:
            square_clicked = [(pos[0] - BOARDGAP) // SQ_SIZE, (pos[1] - BOARDGAP) // SQ_SIZE]  # col, row
            print(square_clicked)
            ally_piece = 'w' if self.white_to_move else 'b'
            if self.board[square_clicked[1]][square_clicked[0]][0] == ally_piece:  # white clicked a white piece
                self.mouse_clicks = [square_clicked]
                self.get_legal_moves(self.mouse_clicks[0])
            else:
                if self.mouse_clicks:
                    if square_clicked in self.legal_moves:
                        # white has a piece selected and moves to an empty square or captures
                        self.mouse_clicks.append(square_clicked)
                        self.make_move()

    def make_move(self):
        new_square = self.mouse_clicks[1]
        old_square = self.mouse_clicks[0]
        piece_moved = self.board[old_square[1]][old_square[0]]
        self.board[new_square[1]][new_square[0]] = piece_moved
        self.board[old_square[1]][old_square[0]] = '--'
        self.white_to_move = not self.white_to_move
        self.mouse_clicks = []
        self.legal_moves = []

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
        self.legal_moves = legal

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
        self.legal_moves = legal

    def get_rook_moves(self, square):
        pass






