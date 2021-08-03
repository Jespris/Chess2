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
BOARDGAP = HEIGHT // 8
SQ_SIZE = (HEIGHT - 2 * BOARDGAP) // 8
IMAGES = {}


def load_images():
    pieces = [-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + str(piece) + '.png'), (SQ_SIZE, SQ_SIZE))


def display_board(screen, gamestate, square_selected, legal_moves, mouse_down, mouse_pos):
    p.draw.rect(screen, p.Color("gray"), p.Rect(0, 0, WIDTH, HEIGHT))
    display_squares(screen)
    display_last_move(screen, gamestate)
    display_square_selected(screen, square_selected)
    display_legal_squares(screen, gamestate, square_selected, legal_moves)
    display_drag_move(screen, gamestate, square_selected, mouse_down, mouse_pos)
    display_pieces(screen, gamestate, square_selected, mouse_down)
    display_coordinates(screen)
    display_move_log(screen, gamestate)
    display_reset_button(screen)


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
            if piece != 0 and not (sq_selected == (row, col) and mouse_down):
                screen.blit(IMAGES[piece], (BOARDGAP + col * SQ_SIZE, BOARDGAP + row * SQ_SIZE))


def display_drag_move(screen, gamestate, square_selected, mouse_down, mouse_pos):
    if square_selected and mouse_down:
        piece = gamestate.board[square_selected[0]][square_selected[1]]
        if piece != 0:
            screen.blit(IMAGES[piece], (mouse_pos[0] - SQ_SIZE // 2, mouse_pos[1] - SQ_SIZE // 2))


def display_coordinates(screen):
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    font = p.font.Font('freesansbold.ttf', SQ_SIZE // 4)
    black = p.Color("black")
    indent = SQ_SIZE // 2
    gap = SQ_SIZE // 8
    for i in range(8):
        rank = rows_to_ranks[i]
        file = cols_to_files[i]
        rank_text = font.render(rank, False, black)
        file_text = font.render(file, False, black)
        rank_text_rect = rank_text.get_rect()
        rank_text_rect.center = (BOARDGAP + 8 * SQ_SIZE + gap, BOARDGAP + i * SQ_SIZE + indent)
        file_text_rect = file_text.get_rect()
        file_text_rect.center = (BOARDGAP + i * SQ_SIZE + indent, BOARDGAP + 8 * SQ_SIZE + gap)
        screen.blit(rank_text, rank_text_rect)
        screen.blit(file_text, file_text_rect)


def display_move_log(screen, gamestate):
    box_pos = [BOARDGAP + 9 * SQ_SIZE, BOARDGAP]  # upper left corner
    box_width = 4 * SQ_SIZE
    box_height = 8 * SQ_SIZE
    p.draw.rect(screen, p.Color("white"), p.Rect(box_pos[0], box_pos[1], box_width, box_height))
    black = p.Color("black")
    if len(gamestate.move_log) >= 2:
        move_nr = len(gamestate.move_log) // 2
        font = p.font.Font('freesansbold.ttf', SQ_SIZE // 4)
        row_height = SQ_SIZE // 3
        possible_amount_of_moves_displayed = box_height // row_height
        if move_nr > possible_amount_of_moves_displayed:  # cut the moves
            for i in range(1 + (move_nr - possible_amount_of_moves_displayed), move_nr + 1):
                text = font.render(str(i), True, black)
                textRect = text.get_rect()
                textRect.center = (box_pos[0] + SQ_SIZE // 6, box_pos[1] + (i - (move_nr - possible_amount_of_moves_displayed)) * row_height)
                screen.blit(text, textRect)

                # moves
                white_move = gamestate.move_log[i * 2 - 2].get_notation()
                black_move = gamestate.move_log[i * 2 - 1].get_notation()
                white_text = font.render(white_move, False, black)
                black_text = font.render(black_move, False, black)
                white_text_Rect = white_text.get_rect()
                white_text_Rect.center = (box_pos[0] + SQ_SIZE // 6 + SQ_SIZE, box_pos[1] + (i - (move_nr - possible_amount_of_moves_displayed)) * row_height)
                screen.blit(white_text, white_text_Rect)
                black_text_Rect = black_text.get_rect()
                black_text_Rect.center = (box_pos[0] + SQ_SIZE // 6 + 2 * SQ_SIZE, box_pos[1] + (i - (move_nr - possible_amount_of_moves_displayed)) * row_height)
                screen.blit(black_text, black_text_Rect)
        else:  # display from beginning
            for i in range(1, move_nr + 1):
                text = font.render(str(i), True, black)
                textRect = text.get_rect()
                textRect.center = (box_pos[0] + SQ_SIZE // 6, box_pos[1] + i * row_height)
                screen.blit(text, textRect)

                # moves
                white_move = gamestate.move_log[i * 2 - 2].get_notation()
                black_move = gamestate.move_log[i * 2 - 1].get_notation()
                white_text = font.render(white_move, False, black)
                black_text = font.render(black_move, False, black)
                white_text_Rect = white_text.get_rect()
                white_text_Rect.center = (box_pos[0] + SQ_SIZE // 6 + SQ_SIZE, box_pos[1] + i * row_height)
                screen.blit(white_text, white_text_Rect)
                black_text_Rect = black_text.get_rect()
                black_text_Rect.center = (box_pos[0] + SQ_SIZE // 6 + 2 * SQ_SIZE, box_pos[1] + i * row_height)
                screen.blit(black_text, black_text_Rect)


def display_last_move(screen, gamestate):
    highlight_color = p.Color("lightblue")
    if gamestate.move_log:
        move = gamestate.move_log[-1]
        p.draw.rect(screen, highlight_color, p.Rect(BOARDGAP + move.start_col * SQ_SIZE, BOARDGAP + move.start_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.draw.rect(screen, highlight_color, p.Rect(BOARDGAP + move.end_col * SQ_SIZE, BOARDGAP + move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def display_game_over(screen, gamestate, message):
    box_pos = [BOARDGAP + 2 * SQ_SIZE, BOARDGAP + 3 * SQ_SIZE + SQ_SIZE // 2]
    box_size = [4 * SQ_SIZE, 2 * SQ_SIZE]
    gap = 2
    p.draw.rect(screen, p.Color("black"), p.Rect(box_pos[0], box_pos[1], box_size[0], box_size[1]))
    p.draw.rect(screen, p.Color("white"),
                p.Rect(box_pos[0] + gap, box_pos[1] + gap, box_size[0] - 2 * gap, box_size[1] - 2 * gap))
    font = p.font.Font('freesansbold.ttf', SQ_SIZE // 4)
    text = font.render(message, False, p.Color("black"))
    textRect = text.get_rect()
    textRect.center = (box_pos[0] + box_size[0] // 2, box_pos[1] + box_size[1] // 2)
    screen.blit(text, textRect)

# reset button

def get_reset_button():
    box_pos = [BOARDGAP + 10 * SQ_SIZE + SQ_SIZE // 2, BOARDGAP + 8 * SQ_SIZE]
    box_size = [SQ_SIZE, SQ_SIZE // 2]
    return box_pos, box_size


def display_reset_button(screen):
    box_pos, box_size = get_reset_button()
    gap = 2
    p.draw.rect(screen, p.Color("black"), p.Rect(box_pos[0], box_pos[1], box_size[0], box_size[1]))
    p.draw.rect(screen, p.Color("white"), p.Rect(box_pos[0] + gap, box_pos[1] + gap, box_size[0] - 2*gap, box_size[1] - 2*gap))
    font = p.font.Font('freesansbold.ttf', SQ_SIZE // 4)
    text = font.render("Reset", False, p.Color("black"))
    textRect = text.get_rect()
    textRect.center = (box_pos[0] + box_size[0] // 2, box_pos[1] + box_size[1] // 2)
    screen.blit(text, textRect)


def display_eval_bar(screen, gamestate):
    # draw from black perspective, aka background is white
    gap = 4
    total = SQ_SIZE * 8
    # black border
    p.draw.rect(screen, p.Color("black"), p.Rect(BOARDGAP // 2 - gap, BOARDGAP - gap, SQ_SIZE // 2 + 2 * gap, total + 2 * gap))
    # white background
    p.draw.rect(screen, p.Color("white"), p.Rect(BOARDGAP // 2, BOARDGAP, SQ_SIZE // 2, total))
    # black eval
    max_eval = 10  # total eval range both directions => 20
    pixels_per_eval = total // (max_eval * 2)
    eval = max_eval - gamestate.eval_log[-1]
    p.draw.rect(screen, p.Color("black"), p.Rect(BOARDGAP // 2, BOARDGAP, SQ_SIZE // 2, eval * pixels_per_eval))
    # draw middlepoint
    p.draw.rect(screen, p.Color("gold"), p.Rect(BOARDGAP // 2, HEIGHT // 2, SQ_SIZE // 2, SQ_SIZE // 10))
