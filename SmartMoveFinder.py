"""
Responsible for finding a good move for the AI
"""

import random as r


def find_random_move(legal_moves):
    return legal_moves[r.randint(0, len(legal_moves) - 1)]


def find_best_move():
    pass
