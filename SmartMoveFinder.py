"""
Responsible for finding a good move for the AI
"""

import random as r


piece_values = {'k': 0, 'q': 9, 'b': 3, 'n': 3, 'r': 5, 'p': 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
# black wants a negative score, white positive


def find_random_move(legal_moves):
    return legal_moves[r.randint(0, len(legal_moves) - 1)]


def find_best_move(gamestate, legal_moves):
    global next_move
    next_move = None
    r.shuffle(legal_moves)
    find_move_nega_max_alpha_beta(gamestate, legal_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gamestate.white_to_move else -1)
    return next_move


def find_move_min_max(gamestate, legal_moves, depth, white_to_move):
    global next_move
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
    global next_move
    if depth == 0:
        return turn_mult * score_board(gamestate)

    # move ordering (check more forcing moves first) - implement later

    max_score = -CHECKMATE
    for move in legal_moves:
        gamestate.make_move(move)
        next_moves = gamestate.get_legal_moves()
        score = -find_move_nega_max_alpha_beta(gamestate, next_moves, depth - 1, -beta, -alpha, -turn_mult)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
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


def score_board(gamestate):
    if gamestate.checkmate:
        if gamestate.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE
    elif gamestate.draw:
        return STALEMATE
    score = 0
    for row in range(8):
        for col in range(8):
            if gamestate.board[row][col][0] == 'w':
                score += piece_values[gamestate.board[row][col][1]]
            elif gamestate.board[row][col][0] == 'b':
                score -= piece_values[gamestate.board[row][col][1]]
    return score
"""
Score the board
"""


def score_material(board):
    score = 0
    for row in range(8):
        for col in range(8):
            if board[row][col][0] == 'w':
                score += piece_values[board[row][col][1]]
            elif board[row][col][0] == 'b':
                score -= piece_values[board[row][col][1]]
    return score

