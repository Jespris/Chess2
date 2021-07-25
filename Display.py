"""
Main displaying file, responsible for:
- Displaying the board
- Displaying the pieces
- Displaying the movelog
- Displaying time
- Displaying eval bar
- Animating moves
- Displaying legal squares
"""

import pygame as p
from win32api import GetSystemMetrics

WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)
BOARDGAP = HEIGHT // 10
SQ_SIZE = (HEIGHT - 2 * BOARDGAP) // 8
IMAGES = {}


def load_images():
    pieces = ['wp', 'bp', 'wr', 'br', 'wb', 'bb', 'wn', 'bn', 'bq', 'wq', 'bk', 'wk']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))



def display_board(screen, gamestate):
    display_squares(screen)
    display_legal_squares(screen, gamestate)
    display_pieces(screen, gamestate)


def display_squares(screen):
    light = p.Color("burlywood1")
    dark = p.Color("burlywood4")
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                color = light
            else:
                color = dark
            p.draw.rect(screen, color, p.Rect(BOARDGAP + col * SQ_SIZE, BOARDGAP + row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def display_legal_squares(screen, gamestate):
    for square in gamestate.legal_moves:
        p.draw.rect(screen, p.Color("gray"), p.Rect(BOARDGAP + square[0] * SQ_SIZE + SQ_SIZE // 4,
                                                    BOARDGAP + square[1] * SQ_SIZE + SQ_SIZE // 4,
                                                    SQ_SIZE // 2, SQ_SIZE // 2))

def display_pieces(screen, gamestate):
    for row in range(8):
        for col in range(8):
            piece = gamestate.board[row][col]
            if piece != '--':
                screen.blit(IMAGES[piece], (BOARDGAP + col * SQ_SIZE, BOARDGAP + row * SQ_SIZE))

