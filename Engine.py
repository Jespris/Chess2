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
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
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

    def undo_move(self):
        if self.move_log:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

    """
    Listing legal moves
    """

    def get_legal_moves(self):  # considering checks (pins)
        return self.get_all_possible_moves()  # TEMPORARY

    def get_all_possible_moves(self):  # without considering checks
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.get_pawn_moves(r, c, moves)
                    elif piece == 'r':
                        self.get_rook_moves(r, c, moves)
                    elif piece == 'n':
                        self.get_knight_moves(r, c, moves)
                    elif piece == 'b':
                        self.get_bishop_moves(r, c, moves)
                    elif piece == 'q':
                        self.get_queen_moves(r, c, moves)
                    elif piece == 'k':
                        self.get_king_moves(r, c, moves)
        return moves

    """
    Different piece moves
    """

    def get_pawn_moves(self, r, c, moves):
        direction = -1 if self.white_to_move else 1  # sets pawn direction
        origin_row = 1 if not self.white_to_move else 6
        enemy = 'b' if self.white_to_move else 'w'
        if self.board[r + direction][c] == '--':  # 1 square pawn advance, add promotion later
            moves.append(Move((r, c), (r + direction, c), self.board))
            if r == origin_row and self.board[r + 2 * direction][c] == '--':  # 2 square advance
                moves.append(Move((r, c), (r + 2 * direction, c), self.board))
        capture_directions = [[direction, 1], [direction, -1]]
        for d in capture_directions:
            new_c = c + d[1]
            if 0 <= new_c < 8:  # inside board
                if self.board[r + d[0]][new_c][0] == enemy:
                    moves.append(Move((r, c), (r + d[0], new_c), self.board))
        return moves

    def get_rook_moves(self, r, c, moves):
        enemy = 'b' if self.white_to_move else 'w'
        i = 1
        north_stop = False
        south_stop = False
        west_stop = False
        east_stop = False
        while (not north_stop or not south_stop or not west_stop or not east_stop) and i < 8:
            # check "north" direction
            if not north_stop and r - i >= 0:
                if self.board[r - i][c] == '--':
                    moves.append(Move((r, c), (r - i, c), self.board))
                elif self.board[r - i][c][0] == enemy:
                    moves.append(Move((r, c), (r - i, c), self.board))
                    north_stop = True
                else:
                    north_stop = True

            if not south_stop and r + i < 8:
                if self.board[r + i][c] == '--':
                    moves.append(Move((r, c), (r + i, c), self.board))
                elif self.board[r + i][c][0] == enemy:
                    moves.append(Move((r, c), (r + i, c), self.board))
                    south_stop = True
                else:
                    south_stop = True

            if not west_stop and c - i >= 0:
                if self.board[r][c - i] == '--':
                    moves.append(Move((r, c), (r, c - i), self.board))
                elif self.board[r][c - i][0] == enemy:
                    moves.append(Move((r, c), (r, c - i), self.board))
                    west_stop = True
                else:
                    west_stop = True

            if not east_stop and c + i < 8:
                if self.board[r][c + i] == '--':
                    moves.append(Move((r, c), (r, c + i), self.board))
                elif self.board[r - i][c][0] == enemy:
                    moves.append(Move((r, c), (r, c + i), self.board))
                    east_stop = True
                else:
                    east_stop = True
            i += 1
        return moves

    def get_bishop_moves(self, r, c, moves):
        enemy = 'b' if self.white_to_move else 'w'
        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                    if self.board[new_r][new_c] == '--':
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c][0] == enemy:
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    else:
                        break
        return moves

    def get_knight_moves(self, r, c, moves):
        enemy = 'b' if self.white_to_move else 'w'
        directions = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                if self.board[new_r][new_c] == '--':
                    moves.append(Move((r, c), (new_r, new_c), self.board))
                elif self.board[new_r][new_c][0] == enemy:
                    moves.append(Move((r, c), (new_r, new_c), self.board))
        return moves

    def get_queen_moves(self, r, c, moves):
        enemy = 'b' if self.white_to_move else 'w'
        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                    if self.board[new_r][new_c] == '--':
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c][0] == enemy:
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    else:
                        break
        return moves

    def get_king_moves(self, r, c, moves):
        enemy = 'b' if self.white_to_move else 'w'
        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                if self.board[new_r][new_c] == '--':
                    moves.append(Move((r, c), (new_r, new_c), self.board))
                elif self.board[new_r][new_c][0] == enemy:
                    moves.append(Move((r, c), (new_r, new_c), self.board))
        return moves


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
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    """
    Overriding the equals method, to allow python to recognize the tuples as equal and not two different objects
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    # TODO: better notation

    def get_notation(self):
        piece = '' if self.piece_moved[1] == 'p' else self.piece_moved[1].upper()
        return piece + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]







