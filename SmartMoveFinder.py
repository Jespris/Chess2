"""
Responsible for finding a good move for the AI
"""

import random as r


piece_values = {'k': 0, 'q': 9, 'b': 3, 'n': 3, 'r': 5, 'p': 1}
CHECKMATE = 1000
STALEMATE = 0
# black wants a negative score, white positive


def find_random_move(legal_moves):
    return legal_moves[r.randint(0, len(legal_moves) - 1)]


def find_best_move(gamestate, legal_moves):
    turn_mult = 1 if gamestate.white_to_move else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    r.shuffle(legal_moves)
    for player_move in legal_moves:
        gamestate.make_move(player_move)
        opponent_moves = gamestate.get_legal_moves()
        opponent_max_score = -CHECKMATE
        for opponent_move in opponent_moves:
            gamestate.make_move(opponent_move)
            if gamestate.checkmate:
                score = - turn_mult * CHECKMATE
            elif gamestate.draw:
                score = 0
            else:
                score = -turn_mult * score_material(gamestate.board)
            if score > opponent_max_score:
                opponent_max_score = score
            gamestate.undo_move()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        gamestate.undo_move()
    return best_player_move


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

