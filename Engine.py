"""
Contains game logic and AI
"""

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
        self.white_king = (7, 4)
        self.black_king = (0, 4)
        self.castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [(CastleRights(self.castle_rights.wks, self.castle_rights.bks,
                                               self.castle_rights.wqs, self.castle_rights.bqs))]
        self.flip_board = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.en_passant_possible = ()  # the square where en passant is possible
        self.checkmate = False
        self.stalemate = False
        self.promote_to = 'q'

    """
    MOVE
    """

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # update the king location
        if move.piece_moved == 'wk':
            self.white_king = (move.end_row, move.end_col)
        elif move.piece_moved == 'bk':
            self.black_king = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + self.promote_to

        # update en passant possible variable
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:  # only on two square pawn advances
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.en_passant_possible = ()
        # en passant
        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = '--'

        # castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king moved to kingside
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]  # copy rook
                self.board[move.end_row][move.end_col + 1] = '--'  # erase rook
            else:  # queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]  # copy rook
                self.board[move.end_row][move.end_col - 2] = '--'  # erase rook

        # update whenever rook or king moves
        self.update_castle_rights(move)
        self.castle_rights_log.append((CastleRights(self.castle_rights.wks, self.castle_rights.bks,
                                               self.castle_rights.wqs, self.castle_rights.bqs)))

    def update_castle_rights(self, move):
        if move.piece_moved == 'wk':
            self.castle_rights.wqs = False
            self.castle_rights.wks = False
        elif move.piece_moved == 'bk':
            self.castle_rights.bqs = False
            self.castle_rights.bks = False
        elif move.piece_moved == 'wr':
            if move.start_row == 7:  # white start row
                if move.start_col == 0:  # left rook
                    self.castle_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.castle_rights.wks = False
        elif move.piece_moved == 'wr':
            if move.start_row == 0:  # black start row
                if move.start_col == 0:  # left rook
                    self.castle_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.castle_rights.bks = False
        # if a rook is captured
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.castle_rights.wqs = False
                elif move.end_col == 7:
                    self.castle_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.castle_rights.bqs = False
                elif move.end_col == 7:
                    self.castle_rights.bks = False

    def undo_move(self):
        if self.move_log:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # update the king location
            if move.piece_moved == 'wk':
                self.white_king = (move.start_row, move.start_col)
            elif move.piece_moved == 'bk':
                self.black_king = (move.start_row, move.start_col)
            # undo en passant
            if move.is_en_passant:
                self.board[move.end_row][move.end_col] = '--'  # landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible = (move.end_row, move.end_col)
            # undo a 2 square pawn advance
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()

            # castle
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]  # copy rook
                    self.board[move.end_row][move.end_col - 1] = '--'  # erase rook
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]  # copy rook
                    self.board[move.end_row][move.end_col + 1] = '--'  # erase rook
            # undo castle_rights
            self.castle_rights_log.pop()
            self.castle_rights = self.castle_rights_log[-1]

    """
    Listing legal moves
    """

    def get_legal_moves(self):  # considering checks (pins)
        moves = self.get_all_possible_moves()
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        king_row = self.white_king[0] if self.white_to_move else self.black_king[0]
        king_col = self.white_king[1] if self.white_to_move else self.black_king[1]
        if self.in_check:
            if len(self.checks) == 1:  # only one check, block, capture (practically same as blocking) or move king
                moves = self.get_all_possible_moves()
                # to block check, move piece between checker and king
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if piece_checking[1] == 'n':
                    valid_squares = [[check_row, check_col]]
                else:
                    for i in range(1, 8):
                        valid_square = [king_row + check[2] * i, king_col + check[3] * i]  # check[2, 3] are the directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:  # reached the piece checking
                            break
                # get rid of moves that don't block checks or moves king
                for i in range(len(moves) - 1, - 1, - 1):  # go backwards through list to not skip any moves
                    if moves[i].piece_moved[1] != 'k':  # move doesn't move king so has to block or capture
                        if not [moves[i].end_row, moves[i].end_col] in valid_squares:  # move doesn't block
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in check so all moves are fine
            moves = self.get_all_possible_moves()
        if not moves:  # either checkmate or stalemate
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves

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
    Legal moves helper functions
    """

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        enemy = 'b' if self.white_to_move else 'w'
        ally = 'w' if self.white_to_move else 'b'
        start_row = self.white_king[0] if self.white_to_move else self.black_king[0]
        start_col = self.white_king[1] if self.white_to_move else self.black_king[1]
        card_dir = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for d in range(len(card_dir)):
            possible_pin = ()  # reset pin
            for i in range(1, 8):
                new_row = start_row + card_dir[d][0] * i
                new_col = start_col + card_dir[d][1] * i
                if 0 <= new_row < 8 and 0 <= new_col < 8:  # inside board
                    end_piece = self.board[new_row][new_col]
                    if end_piece[0] == ally and end_piece[1] != 'k':
                        if possible_pin == ():  # 1st allied piece in that direction
                            possible_pin = (new_row, new_col, card_dir[d][0], card_dir[d][1])
                        else:  # 2nd or later allied piece in this direction, so no pin possible
                            break
                    elif end_piece[0] == enemy:
                        piece_type = end_piece[1]
                        """
                        5 possibilities in this complex conditional:
                        1. Orthogonally away from king and piece is a rook
                        2. Diagonally away from king and piece is a bishop
                        3. 1 square away diagonally and piece is a pawn
                        4. any direction and piece is a queen
                        5. any direction 1 square away and piece is king
                        """
                        if (d < 4 and piece_type == 'r') or \
                                (4 <= d <= 7 and piece_type == 'b') or \
                                (i == 1 and piece_type == 'p' and ((enemy == 'w' and 6 <= d <= 7) or (enemy == 'b' and 4 <= d <= 5))) or \
                                (piece_type == 'q') or (i == 1 and piece_type == 'k'):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((new_row, new_col, card_dir[d][0], card_dir[d][1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break
        # knight checks:
        knight_moves = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
        for n in knight_moves:
            new_row = start_row + n[0]
            new_col = start_col + n[1]
            if 0 <= new_row < 8 and 0 <= new_col < 8:  # inside board
                end_piece = self.board[new_row][new_col]
                if end_piece[0] == enemy and end_piece[1] == 'n':  # enemy knight attacking king
                    in_check = True
                    checks.append((new_row, new_col, n[0], n[1]))
        return in_check, pins, checks

    """
    Different piece moves
    """

    def get_pawn_moves(self, r, c, moves):
        # pins and stuff
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        direction = -1 if self.white_to_move else 1  # sets pawn direction
        origin_row = 1 if not self.white_to_move else 6
        enemy = 'b' if self.white_to_move else 'w'
        if self.board[r + direction][c] == '--':  # 1 square pawn advance, add promotion later
            if not piece_pinned or pin_direction == (direction, 0):
                moves.append(Move((r, c), (r + direction, c), self.board))
                if r == origin_row and self.board[r + 2 * direction][c] == '--':  # 2 square advance
                    moves.append(Move((r, c), (r + 2 * direction, c), self.board))
        capture_directions = [[direction, 1], [direction, -1]]
        for d in capture_directions:
            new_c = c + d[1]
            if 0 <= new_c < 8:  # inside board
                if self.board[r + d[0]][new_c][0] == enemy:
                    if not piece_pinned or pin_direction == (d[0], d[1]):
                        moves.append(Move((r, c), (r + d[0], new_c), self.board))
                elif (r + d[0], new_c) == self.en_passant_possible:
                    moves.append(Move((r, c), (r + d[0], new_c), self.board, en_passant_possible=True))

    def get_rook_moves(self, r, c, moves):
        # pins and stuff
        piece_pinned = False
        pin_direction = []
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = [self.pins[i][2], self.pins[i][3]]
                self.pins.remove(self.pins[i])
                break

        enemy = 'b' if self.white_to_move else 'w'
        directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                    if self.board[new_r][new_c] == '--':
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c][0] == enemy:
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    else:
                        break

    def get_bishop_moves(self, r, c, moves):
        # pins and stuff
        piece_pinned = False
        pin_direction = []
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = [self.pins[i][2], self.pins[i][3]]
                self.pins.remove(self.pins[i])
                break

        enemy = 'b' if self.white_to_move else 'w'
        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                    if self.board[new_r][new_c] == '--':
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c][0] == enemy:
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    else:
                        break

    def get_knight_moves(self, r, c, moves):
        # pins and stuff
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        enemy = 'b' if self.white_to_move else 'w'
        directions = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                if not piece_pinned:
                    if self.board[new_r][new_c] == '--':
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c][0] == enemy:
                        moves.append(Move((r, c), (new_r, new_c), self.board))

    def get_queen_moves(self, r, c, moves):
        # pins and stuff
        piece_pinned = False
        pin_direction = []
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = [self.pins[i][2], self.pins[i][3]]
                self.pins.remove(self.pins[i])
                break

        enemy = 'b' if self.white_to_move else 'w'
        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                    if self.board[new_r][new_c] == '--':
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c][0] == enemy:
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    else:
                        break

    def get_king_moves(self, r, c, moves):
        row_moves = [-1, -1, -1, 0, 0, 1, 1, 1]
        col_moves = [-1, 0, 1, -1, 1, -1, 0, 1]
        ally = 'w' if self.white_to_move else 'b'
        for i in range(8):
            new_r = r + row_moves[i]
            new_c = c + col_moves[i]
            if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                end_piece = self.board[new_r][new_c]
                if end_piece[0] != ally:  # not an ally piece, empty or enemy
                    if ally == 'w':
                        self.white_king = (new_r, new_c)
                    else:
                        self.black_king = (new_r, new_c)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                    # place king back
                    if ally == 'w':
                        self.white_king = (r, c)
                    else:
                        self.black_king = (r, c)

        self.get_castle_moves(r, c, moves, ally)

    def get_castle_moves(self, r, c, moves, ally):
        if self.in_check:
            return  # can't castle while in check
        if (self.white_to_move and self.castle_rights.wks) or (not self.white_to_move and self.castle_rights.bks):
            self.get_kingside_castle_moves(r, c, moves, ally)
        if (self.white_to_move and self.castle_rights.wqs) or (not self.white_to_move and self.castle_rights.bqs):
            self.get_queenside_castle_moves(r, c, moves, ally)

    def get_kingside_castle_moves(self, r, c, moves, ally):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':  # empty squares between rook and king
            # TODO: check if square under attack
            moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves, ally):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':  # empty squares between rook and king
            # TODO: check if square under attack
            moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))


class CastleRights:  # for storing the info about castling rights
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, en_passant_possible=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.is_pawn_promotion = ((self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7))

        self.is_en_passant = en_passant_possible
        if self.is_en_passant:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        # castle move
        self.is_castle_move = is_castle_move


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







