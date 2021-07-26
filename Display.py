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


def display_board(screen, gamestate, square_selected, legal_moves, mouse_down, mouse_pos):
    display_squares(screen)
    display_square_selected(screen, square_selected)
    display_legal_squares(screen, gamestate, square_selected, legal_moves)
    display_drag_move(screen, gamestate, square_selected, mouse_down, mouse_pos)
    display_pieces(screen, gamestate, square_selected, mouse_down)


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


def display_square_selected(screen, square):
    if square:
        p.draw.rect(screen, p.Color("gold"), p.Rect(BOARDGAP + square[1] * SQ_SIZE, BOARDGAP + square[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def display_legal_squares(screen, gamestate, square_selected, legal_moves):
    if square_selected:
        for move in legal_moves:
            if move.start_row == square_selected[0] and move.start_col == square_selected[1]:
                p.draw.rect(screen, p.Color("gray"), p.Rect(BOARDGAP + move.end_col * SQ_SIZE + SQ_SIZE // 4,
                                                            BOARDGAP + move.end_row * SQ_SIZE + SQ_SIZE // 4,
                                                            SQ_SIZE // 2, SQ_SIZE // 2))


def display_pieces(screen, gamestate, sq_selected, mouse_down):
    for row in range(8):
        for col in range(8):
            piece = gamestate.board[row][col]
            if piece != '--' and not (sq_selected == (row, col) and mouse_down):
                screen.blit(IMAGES[piece], (BOARDGAP + col * SQ_SIZE, BOARDGAP + row * SQ_SIZE))


def display_drag_move(screen, gamestate, square_selected, mouse_down, mouse_pos):
    if square_selected and mouse_down:
        piece = gamestate.board[square_selected[0]][square_selected[1]]
        if piece != '--':
            screen.blit(IMAGES[piece], (mouse_pos[0] - SQ_SIZE // 2, mouse_pos[1] - SQ_SIZE // 2))

