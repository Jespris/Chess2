"""
Responsible for finding a good move for the AI
"""

import random as r


piece_values = {6: 0, 5: 9, 4: 3, 3: 3, 2: 5, 1: 1}
# black wants a negative score, white positive
CHECKMATE = 1000
STALEMATE = 0
CPU_PERFORMANCE = 10
ENDGAME = False
BOARD_HASH = {}

knight_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]]  # TODO: tweak knight scores

opening_king_scores =   [[2, 3, 3, 1, 1, 1, 3, 2],
                         [2, 1, 1, 1, 1, 1, 1, 2],
                         [1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1],
                         [2, 1, 1, 1, 1, 1, 1, 2],
                         [2, 3, 3, 1, 1, 1, 3, 2]]  # prefers castles?!?

endgame_king_scores =   [[1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 2, 2, 1, 1, 1],
                         [1, 1, 2, 2, 2, 2, 1, 1],
                         [1, 1, 2, 2, 2, 2, 1, 1],
                         [1, 1, 1, 2, 2, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1]]  # active king


queen_scores = [[2, 1, 1, 1, 1, 1, 1, 2],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [2, 1, 1, 1, 1, 1, 1, 2]]

bishop_scores = [[4, 3, 2, 1, 1, 2, 3, 4],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [4, 3, 2, 1, 1, 2, 3, 4]]  # allows for fiancheetos

rook_scores =   [[2, 1, 1, 3, 3, 2, 1, 2],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [2, 1, 1, 3, 3, 2, 1, 2]]  # rooks in the center but not really

white_pawn_scores = [[9, 9, 9, 9, 9, 9, 9, 9],
                     [4, 5, 6, 7, 7, 6, 5, 4],
                     [3, 4, 5, 6, 6, 5, 4, 3],
                     [2, 3, 4, 5, 5, 4, 3, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 2, 2, 3, 3, 2, 2, 2],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [1, 1, 1, 1, 1, 1, 1, 1]]

black_pawn_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [2, 2, 2, 3, 3, 2, 2, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 3, 4, 5, 5, 4, 3, 2],
                     [3, 4, 5, 6, 6, 5, 4, 3],
                     [4, 5, 6, 7, 7, 6, 5, 4],
                     [9, 9, 9, 9, 9, 9, 9, 9]]

white_square_control = [[4, 4, 4, 4, 4, 4, 4, 4],
                     [3, 4, 4, 4, 4, 4, 4, 3],
                     [3, 3, 4, 4, 4, 4, 3, 3],
                     [2, 3, 3, 4, 4, 3, 3, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 2, 2, 3, 3, 2, 2, 2],
                     [1, 1, 1, 2, 2, 1, 1, 1],
                     [1, 1, 1, 1, 1, 1, 1, 1]]

black_square_control = [[1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 2, 2, 1, 1, 1],
                        [2, 2, 2, 3, 3, 2, 2, 2],
                        [2, 2, 3, 4, 4, 3, 2, 2],
                        [2, 3, 3, 4, 4, 3, 3, 2],
                        [3, 3, 4, 4, 4, 4, 3, 3],
                        [3, 4, 4, 4, 4, 4, 4, 3],
                        [4, 4, 4, 4, 4, 4, 4, 4]]

piece_position_scores = {3: knight_scores, 6: opening_king_scores if not ENDGAME else endgame_king_scores,
                         5: queen_scores, 2: rook_scores, 4: bishop_scores, 1: white_pawn_scores,
                         -1: black_pawn_scores}

rook_directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
bishop_directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
queen_directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]]
knight_directions = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
king_directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]]

piece_directions = {2: rook_directions, 4: bishop_directions, 5: queen_directions, 3: knight_directions, 6: king_directions}


def find_random_move(legal_moves):
    return legal_moves[r.randint(0, len(legal_moves) - 1)]


def find_best_move(gamestate, legal_moves, return_queue):
    global next_move, counter, ENDGAME, BOARD_HASH, board_state_copies
    next_move = None
    actual_depth = 1
    counter = 0
    if len(legal_moves) == 1:
        next_move = legal_moves[0]

    if not next_move:
        board_state_copies = 0
        actual_depth = get_good_depth()
        if len(gamestate.move_log) < 6:  # opening
            next_move_in_opening = gamestate.get_opening()
            if next_move_in_opening:
                for move in legal_moves:
                    if move.get_notation() == next_move_in_opening:  # check if this move results in the same notation the opening line move is
                        next_move = move
                        break
        if not next_move:
            find_move_nega_max_alpha_beta(gamestate, legal_moves, actual_depth, -CHECKMATE, CHECKMATE, 1 if gamestate.white_to_move else -1, actual_depth)
        print("Looked at", counter, "boardstates,", board_state_copies, "skipped copies, depth", actual_depth)
    return_queue.put((next_move, (counter, actual_depth)))


def find_move_nega_max_alpha_beta(gamestate, legal_moves, depth, alpha, beta, turn_mult, actual_depth):
    global next_move, counter, ENDGAME, BOARD_HASH, board_state_copies
    if depth == 0:
        return turn_mult * score_board(gamestate)

    sorted_moves = sort_legal_moves(legal_moves, gamestate)

    # check if endgame
    if not ENDGAME and len(gamestate.move_log) > 50:
        ENDGAME = evaluate_endgame(gamestate.board)

    max_score = -CHECKMATE
    for move in sorted_moves:
        counter += 1
        gamestate.make_move(move)
        next_moves = gamestate.get_legal_moves()
        board_state = gamestate.boardstates_log[-1]
        if board_state not in BOARD_HASH:
            # print("New board state")
            score = -find_move_nega_max_alpha_beta(gamestate, next_moves, depth - 1, -beta, -alpha, -turn_mult, actual_depth)
            BOARD_HASH[board_state] = score
        else:
            # print("Board state already found!")
            board_state_copies += 1
            score = BOARD_HASH[board_state]
            # print("copied board state evaluated as", score)
        if score > max_score:
            max_score = score
            if depth == actual_depth:
                print("new best move", move.get_notation(), "evaluation:", score)
                next_move = move
        gamestate.undo_move()
        if max_score > alpha:  # pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def sort_legal_moves(legal_moves, gamestate):
    # move ordering (check more forcing moves first)
    # only relevant if captures are available aka after first moves
    if len(gamestate.move_log) >= 2:
        sorted_moves = []
        # check each legal move and sort them, captures and checks first
        for i in range(len(legal_moves) - 1, -1, -1):
            move = legal_moves[i]
            gamestate.make_move(move)
            gamestate.get_legal_moves()  # to update the in check variable
            if move.piece_captured != 0 or gamestate.in_check:  # move is capture or check
                sorted_moves.append(move)
                legal_moves.pop(i)
            gamestate.undo_move()
        # then pieces before pawns
        for i in range(len(legal_moves) - 1, -1, -1):
            move = legal_moves[i]
            gamestate.make_move(move)
            if abs(move.piece_moved) != 1:
                sorted_moves.append(move)
                legal_moves.pop(i)
            gamestate.undo_move()
        # append the rest to the new list
        r.shuffle(legal_moves)
        for unforcing_move in legal_moves:
            sorted_moves.append(unforcing_move)
    else:
        sorted_moves = legal_moves
    return sorted_moves


def get_good_depth():
    depth = 3 if not ENDGAME else 6
    return depth


"""
Score the board
"""


def score_board(gamestate):
    if gamestate.checkmate:
        if gamestate.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE
    elif gamestate.draw:
        return STALEMATE
    white_pawn_chains = 0
    black_pawn_chains = 0
    pawn_chain_weight = 10  # higher = less positional impact
    available_moves = 0
    available_moves_weight = 20
    material_weight = 1.2
    # TODO: instead of checking squares controlled, just check number of available moves from a position, more = better
    #  - this is maybe less computaionally heavy than checking the squares controlled
    sq_controlled_weight = 12  # higher = less positional impact
    score = 0
    weights_impact = 10  # higher = less positional impact
    for row in range(8):
        for col in range(8):
            square = gamestate.board[row][col]
            if square != 0:  # not blank
                white = False
                if square != 1 and square != -1:
                    piece_score = piece_position_scores[abs(square)][row][col] / weights_impact
                else:
                    piece_score = piece_position_scores[square][row][col] / weights_impact
                if square > 0:
                    white = True
                score += piece_score if white else -piece_score
                # checking available moves
                available_move_adder = 1 if square > 0 else -1
                if abs(square) == 1:  # pawns
                    move_direction = -1 if square == 1 else 1
                    if gamestate.board[row + move_direction][col] == 0:
                        available_moves += available_move_adder
                elif 2 <= abs(square) <= 5 and abs(square) != 3:  # all pieces excluding nights
                    for direction in piece_directions[abs(square)]:
                        for i in range(1, 8):
                            new_row = row + direction[0] * i
                            new_col = col + direction[1] * i
                            if 0 <= new_row < 8 and 0 <= new_col < 8:
                                check_square = gamestate.board[new_row][new_col]
                                if check_square == 0:
                                    available_moves += available_move_adder
                                elif square * check_square < 0:  # enemy piece
                                    available_moves += available_move_adder
                                    break
                                else:  # piece occupy so can't move there
                                    break
                            else:  # outside board so point in checking further
                                break
                elif abs(square) == 3 or abs(square) == 6:
                    for direction in piece_directions[abs(square)]:
                        new_row = row + direction[0]
                        new_col = col + direction[1]
                        if 0 <= new_row < 8 and 0 <= new_col < 8:
                            check_square = gamestate.board[new_row][new_col]
                            if check_square == 0:
                                available_moves += available_move_adder
    # better position the more options you have generally
    score += available_moves / available_moves_weight

    # material score
    score += gamestate.material_balance / material_weight

    # TODO: add points for connected pawn chains
    score += (white_pawn_chains - black_pawn_chains) / pawn_chain_weight
    return score


def evaluate_endgame(board):
    pieces = 0
    for row in range(8):
        for col in range(8):
            if board[row][col] != 0 and abs(board[row][col]) != 1:  # don't count pawns
                pieces += 1
    if pieces > 5:
        return False
    return True


def is_inside_board(row, col):
    if 0 <= row < 8 and 0 <= col < 8:
        return True
    return False


def score_material(board):
    score = 0
    for row in range(8):
        for col in range(8):
            if board[row][col] > 0:
                score += piece_values[abs(board[row][col])]
            elif board[row][col] < 0:
                score -= piece_values[abs(board[row][col])]
    return score

