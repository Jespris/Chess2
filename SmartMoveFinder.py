"""
Responsible for finding a good move for the AI
"""

import random as r


piece_values = {'k': 0, 'q': 9, 'b': 3, 'n': 3, 'r': 5, 'p': 1}
# black wants a negative score, white positive
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4

knight_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]]  # TODO: tweak knight scores

king_scores =   [[1, 3, 3, 1, 1, 1, 3, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 3, 3, 1, 1, 1, 3, 1]]  # prefers castles?!?

queen_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 3, 2, 3, 3, 2, 3, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 3, 2, 3, 3, 2, 3, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]]  # allows for fiancheetos

rook_scores =   [[2, 1, 1, 3, 3, 2, 1, 2],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [2, 1, 1, 3, 3, 2, 1, 2]]  # rooks in the center but not really

white_pawn_scores = [[5, 5, 5, 5, 5, 5, 5, 5],
                     [4, 4, 4, 5, 5, 4, 4, 4],
                     [3, 3, 4, 4, 4, 4, 3, 3],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 2, 2, 3, 3, 2, 2, 2],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [1, 1, 1, 1, 1, 1, 1, 1]]

black_pawn_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [2, 2, 2, 3, 3, 2, 2, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [3, 3, 4, 4, 4, 4, 3, 3],
                     [4, 4, 4, 5, 5, 4, 4, 4],
                     [5, 5, 5, 5, 5, 5, 5, 5]]

piece_position_scores = {'n': knight_scores, 'k': king_scores, 'q': queen_scores, 'r': rook_scores, 'b': bishop_scores,
                         'wp': white_pawn_scores, 'bp': black_pawn_scores}


def find_random_move(legal_moves):
    return legal_moves[r.randint(0, len(legal_moves) - 1)]


def find_best_move(gamestate, legal_moves, return_queue):
    global next_move, counter
    next_move = None
    r.shuffle(legal_moves)
    counter = 0
    find_move_nega_max_alpha_beta(gamestate, legal_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gamestate.white_to_move else -1)
    print("Looked at", counter, "boardstates")
    return_queue.put(next_move)


def find_move_min_max(gamestate, legal_moves, depth, white_to_move):
    global next_move, counter
    if depth == 0:
        return score_material(gamestate.board)
    if white_to_move:  # maximize
        max_score = -CHECKMATE
        for move in legal_moves:
            gamestate.make_move(move)
            next_moves = gamestate.get_legal_moves()
            score = find_move_min_max(gamestate, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gamestate.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in legal_moves:
            gamestate.make_move(move)
            next_moves = gamestate.get_legal_moves()
            score = find_move_min_max(gamestate, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gamestate.undo_move()
        return min_score


def find_move_nega_max_alpha_beta(gamestate, legal_moves, depth, alpha, beta, turn_mult):
    global next_move, counter
    if depth == 0:
        return turn_mult * score_board(gamestate)

    # move ordering (check more forcing moves first) - implement later
    # only relevant if capures are available aka after first moves
    if len(gamestate.move_log) > 2:
        sorted_moves = []
        # check each legal move and sort them, captures and checks first
        for i in range(len(legal_moves) - 1, -1, -1):
            move = legal_moves[i]
            gamestate.make_move(move)
            if move.piece_captured != '--' or gamestate.in_check:  # move is capture or check
                sorted_moves.append(move)
                legal_moves.pop(i)
            gamestate.undo_move()
        # append the rest to the new list
        for unforcing_move in legal_moves:
            sorted_moves.append(unforcing_move)
    else:
        sorted_moves = legal_moves

    max_score = -CHECKMATE
    for move in sorted_moves:
        counter += 1
        gamestate.make_move(move)
        next_moves = gamestate.get_legal_moves()
        score = -find_move_nega_max_alpha_beta(gamestate, next_moves, depth - 1, -beta, -alpha, -turn_mult)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                print("looking at move", move.get_notation(), "evaluating as:", score)
        gamestate.undo_move()
        if max_score > alpha:  # pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def find_move_nega_max(gamestate, legal_moves, depth, turn_mult):
    global next_move
    if depth == 0:
        return turn_mult * score_board(gamestate)

    max_score = -CHECKMATE
    for move in legal_moves:
        gamestate.make_move(move)
        next_moves = gamestate.get_legal_moves()
        score = -find_move_nega_max(gamestate, next_moves, depth - 1, -turn_mult)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gamestate.undo_move()
    return max_score


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
    score = 0
    weights_impact = 8
    for row in range(8):
        for col in range(8):
            square = gamestate.board[row][col]
            if square != '--':  # not blank
                if square != 'wp' and square != 'bp':
                    piece_score = piece_position_scores[square[1]][row][col] / weights_impact
                else:
                    piece_score = piece_position_scores[square][row][col] / weights_impact
                if square[0] == 'w':
                    score += piece_values[square[1]] + piece_score
                elif gamestate.board[row][col][0] == 'b':
                    score -= piece_values[square[1]] + piece_score
    return score


"""def score_material(board):
    score = 0
    for row in range(8):
        for col in range(8):
            if board[row][col][0] == 'w':
                score += piece_values[board[row][col][1]]
            elif board[row][col][0] == 'b':
                score -= piece_values[board[row][col][1]]
    return score"""

