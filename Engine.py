"""
Contains game logic and AI
"""
import random

from win32api import GetSystemMetrics

WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)
BOARDGAP = HEIGHT // 10
SQ_SIZE = (HEIGHT - 2 * BOARDGAP) // 8
int_to_string = {0: '--', 1: 'wp', 2: 'wr', 3: 'wn', 4: 'wb', 5: 'wq', 6: 'wk',
                 -1: 'bp', -2: 'br', -3: 'bn', -4: 'bb', -5: 'bq', -6: 'bk'}


class GameState:
    def __init__(self, width, height, sq_size):
        self.width = width
        self.height = height
        self.squaresize = sq_size
        # TODO: change all pieces to integers for faster calculation
        # white - positive, black - negative
        # empty = 0, pawn = 1, rook = 2, knight = 3, bishop = 4, queen = 5, king = 6
        self.board = [
            [-2,-3,-4,-5,-6,-4,-3,-2],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [2, 3, 4, 5, 6, 4, 3, 2]
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
        self.draw = False
        self.promote_to = 5 if self.white_to_move else -5
        self.boardstates_log = []
        self.states_depth_log = []
        self.eval_log = []

    """
    MOVE
    """

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = 0
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # update the king location
        if move.piece_moved == 6:
            self.white_king = (move.end_row, move.end_col)
        elif move.piece_moved == -6:
            self.black_king = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.promote_to

        # update en passant possible variable
        if abs(move.piece_moved) == 1 and abs(move.start_row - move.end_row) == 2:  # only on two square pawn advances
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.en_passant_possible = ()
        # en passant
        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = 0

        # castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king moved to kingside
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]  # copy rook
                self.board[move.end_row][move.end_col + 1] = 0  # erase rook
            else:  # queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]  # copy rook
                self.board[move.end_row][move.end_col - 2] = 0  # erase rook

        # update whenever rook or king moves
        self.update_castle_rights(move)
        self.castle_rights_log.append((CastleRights(self.castle_rights.wks, self.castle_rights.bks,
                                               self.castle_rights.wqs, self.castle_rights.bqs)))

        # store board state
        self.boardstates_log.append(self.get_boardstate())

    def update_castle_rights(self, move):
        if move.piece_moved == 6:  # king
            self.castle_rights.wqs = False
            self.castle_rights.wks = False
        elif move.piece_moved == -6:
            self.castle_rights.bqs = False
            self.castle_rights.bks = False
        elif move.piece_moved == 2:  # rook
            if move.start_row == 7:  # white start row
                if move.start_col == 0:  # left rook
                    self.castle_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.castle_rights.wks = False
        elif move.piece_moved == -2:
            if move.start_row == 0:  # black start row
                if move.start_col == 0:  # left rook
                    self.castle_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.castle_rights.bks = False
        # if a rook is captured
        if move.piece_captured == 2:
            if move.end_row == 7:
                if move.end_col == 0:
                    self.castle_rights.wqs = False
                elif move.end_col == 7:
                    self.castle_rights.wks = False
        elif move.piece_captured == -2:
            if move.end_row == 0:
                if move.end_col == 0:
                    self.castle_rights.bqs = False
                elif move.end_col == 7:
                    self.castle_rights.bks = False

    def undo_move(self):
        if self.move_log:
            move = self.move_log.pop()
            self.boardstates_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # update the king location
            if move.piece_moved == 6:  # king
                self.white_king = (move.start_row, move.start_col)
            elif move.piece_moved == -6:
                self.black_king = (move.start_row, move.start_col)
            # undo en passant
            if move.is_en_passant:
                self.board[move.end_row][move.end_col] = 0  # landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible = (move.end_row, move.end_col)
            # undo a 2 square pawn advance
            if abs(move.piece_moved) == 1 and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()

            # castle
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]  # copy rook
                    self.board[move.end_row][move.end_col - 1] = 0  # erase rook
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]  # copy rook
                    self.board[move.end_row][move.end_col + 1] = 0  # erase rook
            # undo castle_rights
            self.castle_rights_log.pop()
            self.castle_rights = self.castle_rights_log[-1]

        self.checkmate = False
        self.draw = False

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
                if abs(piece_checking) == 3:  # knight
                    valid_squares = [[check_row, check_col]]
                else:
                    for i in range(1, 8):
                        valid_square = [king_row + check[2] * i, king_col + check[3] * i]  # check[2, 3] are the directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:  # reached the piece checking
                            break
                # get rid of moves that don't block checks or moves king
                for i in range(len(moves) - 1, - 1, - 1):  # go backwards through list to not skip any moves
                    if abs(moves[i].piece_moved) != 6:  # move doesn't move king so has to block or capture
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
                self.draw = True
        else:
            self.checkmate = False
            self.draw = False
        return moves

    def get_all_possible_moves(self):  # without considering checks
        moves = []
        for r in range(8):
            for c in range(8):
                turn = 1 if self.white_to_move else -1
                if self.board[r][c] * turn > 0:  # if the piece times turn is positive, it is that pieces turn
                    piece = abs(self.board[r][c])
                    if piece == 1:  # pawn
                        self.get_pawn_moves(r, c, moves)
                    elif piece == 2:  # rook
                        self.get_rook_moves(r, c, moves)
                    elif piece == 3:  # knight
                        self.get_knight_moves(r, c, moves)
                    elif piece == 4:  # bishop
                        self.get_bishop_moves(r, c, moves)
                    elif piece == 5:  # queen
                        self.get_queen_moves(r, c, moves)
                    elif piece == 6:  # king
                        self.get_king_moves(r, c, moves)
        return moves

    """
    Legal moves helper functions
    """

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        enemy = -1 if self.white_to_move else 1
        ally = 1 if self.white_to_move else -1
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
                    if end_piece * ally > 0 and abs(end_piece) != 6:  # ally but not king
                        if possible_pin == ():  # 1st allied piece in that direction
                            possible_pin = (new_row, new_col, card_dir[d][0], card_dir[d][1])
                        else:  # 2nd or later allied piece in this direction, so no pin possible
                            break
                    elif end_piece * enemy > 0:
                        piece_type = abs(end_piece)
                        """
                        5 possibilities in this complex conditional:
                        1. Orthogonally away from king and piece is a rook
                        2. Diagonally away from king and piece is a bishop
                        3. 1 square away diagonally and piece is a pawn
                        4. any direction and piece is a queen
                        5. any direction 1 square away and piece is king
                        """
                        if (d < 4 and piece_type == 2) or \
                                (7 >= d >= 4 == piece_type) or \
                                (i == 1 and piece_type == 1 and ((enemy == 1 and 6 <= d <= 7) or (enemy == -1 and 4 <= d <= 5))) or \
                                (piece_type == 5) or (i == 1 and piece_type == 6):
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
                if end_piece * enemy > 0 and abs(end_piece) == 3:  # enemy knight attacking king
                    in_check = True
                    checks.append((new_row, new_col, n[0], n[1]))
        return in_check, pins, checks

    def get_square_under_attack(self, r, c, ally):
        # check if an enemy piece is attacking that square, return True if it is => castling illegal
        # 1. go orthogonally outward from that square and check for rooks and queens
        # 2. Go diagonally outward and check for bishops, queens or pawn one square away
        # 3. Check if a king is one square away
        # 4. check for knights
        enemy = -1 if ally == 1 else 1
        # rooks and queen
        directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        for d in directions:
            for i in range(8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # inside board
                    if self.board[new_r][new_c] * ally > 0:  # piece blocking attack
                        break
                    if self.board[new_r][new_c] * enemy < 0:
                        if abs(self.board[new_r][new_c]) == 2 or abs(self.board[new_r][new_c]) == 5:
                            return True
                else:  # outside board
                    break
        # bishops and queen, pawn
        directions = [[1, 1], [-1, 1], [-1, -1], [1, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # inside board
                    if self.board[new_r][new_c] * ally > 0:  # piece blocking attack
                        break
                    if self.board[new_r][new_c] * enemy > 0:
                        if abs(self.board[new_r][new_c]) == 4 or abs(self.board[new_r][new_c]) == 6:
                            return True
                        if abs(self.board[new_r][new_c]) == 1 and i == 1:
                            return True
                else:  # outside board
                    break
        # king
        directions = [[1, 1], [-1, 1], [-1, -1], [1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if 0 <= new_r < 8 and 0 <= new_c < 8:  # inside board
                if self.board[new_r][new_c] == enemy * 6:
                    return True
        # knights
        directions = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if 0 <= new_r < 8 and 0 <= new_c < 8:  # inside board
                if self.board[new_r][new_c] == enemy * 3:
                    return True
        return False

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
        enemy = -1 if self.white_to_move else 1
        ally = 1 if self.white_to_move else -1
        promotions = [5, 4, 3, 2]
        if self.board[r + direction][c] == 0:  # 1 square pawn advance,
            if not piece_pinned or pin_direction == (direction, 0):
                if r + direction == 0 or r + direction == 7:  # promotion
                    for i in promotions:
                        moves.append(Move((r, c), (r + direction, c), self.board, promote_to=i * ally))  # adding all different promotions for engine to calculate
                else:
                    moves.append(Move((r, c), (r + direction, c), self.board))
                if r == origin_row and self.board[r + 2 * direction][c] == 0:  # 2 square advance
                    moves.append(Move((r, c), (r + 2 * direction, c), self.board))
        capture_directions = [[direction, 1], [direction, -1]]
        for d in capture_directions:
            new_c = c + d[1]
            if 0 <= new_c < 8:  # inside board
                if self.board[r + d[0]][new_c] * enemy > 0:
                    if not piece_pinned or pin_direction == (d[0], d[1]):
                        if r + d[0] == 0 or r + d[0] == 7:  # capture and promotion
                            for i in promotions:
                                moves.append(Move((r, c), (r + d[0], new_c), self.board, promote_to=i * ally))  # adding all different promotions for engine to calculate
                        else:  # normal capture
                            moves.append(Move((r, c), (r + d[0], new_c), self.board))
                elif (r + d[0], new_c) == self.en_passant_possible:
                    # check if the same king is on same rank as pawn initially
                    king_row, king_col = self.white_king if self.white_to_move else self.black_king
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c:  # king is left of pawn
                            inside_range = range(king_col + 1, c - 1) if capture_directions.index(d) == 1 else range(king_col + 1, c)
                            outside_range = range(c + 1, 8) if capture_directions.index(d) == 1 else range(c + 2, 8)
                        else:  # king right of pawn
                            inside_range = range(king_col - 1, c, - 1) if capture_directions.index(d) == 1 else range(king_col - 1, c + 1, -1)
                            outside_range = range(c - 2, -1, -1) if capture_directions.index(d) == 1 else range(c - 1, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != 0:  # some other piece blocks
                                blocking_piece = True
                        for j in outside_range:
                            square = self.board[r][j]
                            if square * enemy < 0 and (abs(square) == 2 or abs(square) == 5):  # attacking piece
                                attacking_piece = True
                            elif square != 0:  # not empty but not enemy rook or queen
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
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

        enemy = -1 if self.white_to_move else 1
        directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                    if self.board[new_r][new_c] == 0:
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c] * enemy > 0:
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

        enemy = -1 if self.white_to_move else 1
        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                    if self.board[new_r][new_c] == 0:
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c] * enemy > 0:
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

        enemy = -1 if self.white_to_move else 1
        directions = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                if not piece_pinned:
                    if self.board[new_r][new_c] == 0:
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c] * enemy > 0:
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

        enemy = -1 if self.white_to_move else 1
        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                    if self.board[new_r][new_c] == 0:
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c] * enemy > 0:
                        if not piece_pinned or pin_direction == d:
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    else:
                        break

    def get_king_moves(self, r, c, moves):
        row_moves = [-1, -1, -1, 0, 0, 1, 1, 1]
        col_moves = [-1, 0, 1, -1, 1, -1, 0, 1]
        ally = 1 if self.white_to_move else -1
        for i in range(8):
            new_r = r + row_moves[i]
            new_c = c + col_moves[i]
            if 0 <= new_r < 8 and 0 <= new_c < 8:  # new square is inside board
                end_piece = self.board[new_r][new_c]
                if end_piece * ally <= 0:  # not an ally piece, empty or enemy
                    if ally == 1:
                        self.white_king = (new_r, new_c)
                    else:
                        self.black_king = (new_r, new_c)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                    # place king back
                    if ally == 1:
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
        if self.board[r][c + 1] == 0 and self.board[r][c + 2] == 0:  # empty squares between rook and king
            if not self.get_square_under_attack(r, c + 1, ally) and not self.get_square_under_attack(r, c + 2, ally):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves, ally):
        if self.board[r][c - 1] == 0 and self.board[r][c - 2] == 0 and self.board[r][c - 3] == 0:  # empty squares between rook and king
            # TODO: check if square under attack
            if not self.get_square_under_attack(r, c - 1, ally) and not self.get_square_under_attack(r, c - 2, ally):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))

    # draw logic
    def get_draw(self):
        # TODO: make get draw function more accurate
        piece_found = False
        for row in range(8):
            if not piece_found:
                for col in range(8):
                    # check if only kings are on board
                    if 0 < abs(self.board[row][col]) < 6:
                        piece_found = True
                        break
        if not piece_found:
            self.draw = True
            return
        # threefold repetition
        # check if the same boardstate occurs three times
        repetitions = 0
        if len(self.boardstates_log) >= 9:
            checking_state = self.boardstates_log[-1]
            for i in range(-5, -10, -4):
                if self.boardstates_log[i] == checking_state:
                    repetitions += 1
            if repetitions == 2:
                self.draw = True
                return
        # 50 move rule, go backwards in movelog, if no captures in 50 moves or pawn pushes => draw
        if len(self.move_log) >= 100:
            for i in range(-1, -100, -1):
                move = self.move_log[i]
                if move.piece_captured != 0 or abs(move.piece_moved) == 1:
                    return
            self.draw = True
            return

    def get_opening(self):
        move = None
        # hashmap of tuples of moves to reply to the move, choose a random one of those
        moves_so_far = ''
        for move in self.move_log:
            moves_so_far += move.get_notation()

        reti = {'Nf3': (Move((0, 6), (2, 5), self.board), Move((1, 2), (3, 2), self.board), Move((1, 3), (3, 3), self.board)),
                'Nf3Nf6': (Move((6, 2), (4, 2), self.board), Move((6, 3), (4, 3), self.board), Move((6, 6), (5, 6), self.board)),
                'Nf3Nf6c4': (Move((1, 2), (2, 2), self.board), Move((1, 2), (3, 2), self.board), Move((1, 4), (2, 4), self.board)),
                'Nf3Nf6d4': (Move((1, 2), (2, 2), self.board), Move((1, 3), (3, 3), self.board), Move((1, 4), (2, 4), self.board)),
                'Nf3Nf6g3': (Move((1, 2), (2, 2), self.board), Move((1, 2), (3, 2), self.board), Move((1, 6), (2, 6), self.board)),
                'Nf3c5': (Move((6, 1), (5, 1), self.board), Move((6, 2), (4, 2), self.board), Move((6, 4), (4, 4), self.board)),
                'Nf3c5b3': (Move((0, 1), (2, 2), self.board), Move((0, 6), (2, 5), self.board), Move((1, 6), (2, 6), self.board)),
                'Nf3c5c4': (Move((0, 1), (2, 2), self.board), Move((0, 6), (2, 5), self.board), Move((1, 1), (2, 1), self.board)),
                'Nf3c5e4': (Move((0, 1), (2, 2), self.board), Move((1, 3), (2, 3), self.board), Move((1, 4), (2, 4), self.board)),
                'Nf6d5': (Move((6, 3), (4, 3), self.board), Move((6, 4), (5, 4), self.board), Move((6, 6), (5, 6), self.board)),
                'Nf6d5d4': (Move((0, 1), (1, 3), self.board), Move((1, 4), (2, 4), self.board), Move((0, 6), (2, 5), self.board)),
                'Nf6d5e3': (Move((1, 2), (3, 2), self.board), Move((1, 4), (2, 4), self.board), Move((0, 6), (2, 5), self.board)),
                'Nf6d5g3': (Move((1, 2), (3, 2), self.board), Move((1, 6), (2, 6), self.board), Move((0, 6), (2, 5), self.board))}
        kingspawn = {'e4': (Move((1, 4), (3, 4), self.board), Move((1, 2), (3, 2), self.board))}
        queenspawn = {'d4': (Move((1, 3), (3, 3), self.board))}
        english = {'c4': (Move((1, 4), (3, 4), self.board))}
        openings = [reti, kingspawn, queenspawn, english]
        for opening in openings:
            if moves_so_far in opening:
                replies = opening[moves_so_far]
                move = replies[random.randint(0, len(replies) - 1)]
                break
        return move

    def get_boardstate(self):
        board_string = ''
        for row in range(8):
            for col in range(8):
                board_string += str(self.board[row][col])
        board_state = (board_string, self.castle_rights_log[-1].castles_ID, self.en_passant_possible, self.white_to_move)
        return board_state


class CastleRights:  # for storing the info about castling rights
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

        four = '1' if self.wks else '0'
        three = '1' if self.bks else '0'
        two = '1' if self.wqs else '0'
        one = '1' if self.bqs else '0'
        self.castles_ID = int(four + three + two + one)

    def __eq__(self, other):
        if isinstance(other, CastleRights):
            return self.castles_ID == other.castles_ID
        return False


ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
cols_to_files = {v: k for k, v in files_to_cols.items()}


class Move:
    def __init__(self, start_sq, end_sq, board, en_passant_possible=False, is_castle_move=False, promote_to=0):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.promote_to = promote_to
        self.is_pawn_promotion = False if not self.promote_to else True

        self.is_en_passant = en_passant_possible
        if self.is_en_passant:
            self.piece_captured = 1 if self.piece_moved == -1 else 1

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
        if self.is_castle_move:
            if self.end_col == 6:  # kingside
                return '0-0'
            else:  # queenside
                return '0-0-0'
        piece = '' if abs(self.piece_moved) == 1 else int_to_string[abs(self.piece_moved)][1].upper()
        captures = 'x' if self.piece_captured != 0 else ''
        if piece == '' and captures:  # pawn captures
            piece = cols_to_files[self.start_col]
        promotion = '' if not self.is_pawn_promotion else '=' + int_to_string[self.promote_to].upper()
        return piece + captures + get_rank_file(self.end_row, self.end_col) + promotion


def get_rank_file(r, c):
    return cols_to_files[c] + rows_to_ranks[r]







