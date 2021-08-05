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
import math
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


def display_board(screen, gamestate, square_selected, legal_moves, mouse_down, mouse_pos, eval):
    p.draw.rect(screen, p.Color("gray"), p.Rect(0, 0, WIDTH, HEIGHT))
    display_squares(screen)
    display_last_move(screen, gamestate)
    display_square_selected(screen, square_selected)
    display_legal_squares(screen, gamestate, square_selected, legal_moves)
    display_drag_move(screen, gamestate, square_selected, mouse_down, mouse_pos)
    display_pieces(screen, gamestate, square_selected, mouse_down)
    display_coordinates(screen)
    # eval bar
    if eval:
        display_eval_bar(screen, gamestate)
    display_move_log(screen, gamestate, eval)
    display_reset_button(screen)
    display_material_balance(screen, gamestate)


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


def display_move_log(screen, gamestate, eval):
    # display move nr, white move and black move separately
    box_pos = [BOARDGAP + 9 * SQ_SIZE, BOARDGAP]  # upper left corner
    box_width = 4 * SQ_SIZE
    box_height = 8 * SQ_SIZE
    p.draw.rect(screen, p.Color("white"), p.Rect(box_pos[0], box_pos[1], box_width, box_height))
    black = p.Color("black")
    display_opening(screen, gamestate, box_pos, box_width)
    move_nr_x_pos = box_pos[0] + SQ_SIZE // 4
    move_nr_start_y = box_pos[1] + SQ_SIZE // 4
    move_gap = SQ_SIZE // 3
    font = p.font.Font('freesansbold.ttf', SQ_SIZE // 4)
    log = gamestate.move_log
    moves_fit = 48
    move_x_gap = box_width // 3
    if log:  # there is moves to display
        # make new log to fit the display
        note_log = []
        start_integer = len(log) - moves_fit
        if start_integer % 2 != 0:
            start_integer += 1
        for move in range(start_integer, len(log)):
            if move >= 0:
                note_log.append([move, log[move].get_notation(), str(round(gamestate.eval_log[move + 1], 1))])

        for move in range(len(note_log)):
            if note_log[move][0] % 2 == 0:  # whites move
                text = font.render(str(note_log[move][0] // 2 + 1), True, black)
                textRect = text.get_rect()
                textRect.center = (move_nr_x_pos, move_nr_start_y + (move // 2) * move_gap)
                screen.blit(text, textRect)
                # moves
                white_move = note_log[move][1] + "   " + note_log[move][2] if eval else note_log[move][1]
                white_text = font.render(white_move, False, black)
                white_text_Rect = white_text.get_rect()
                white_text_Rect.center = (box_pos[0] + move_x_gap, move_nr_start_y + (move // 2) * move_gap)
                screen.blit(white_text, white_text_Rect)
            else:  # black played last move
                black_move = note_log[move][1] + "   " + note_log[move][2] if eval else note_log[move][1]
                black_text = font.render(black_move, False, black)
                black_text_rect = black_text.get_rect()
                row = move // 2  # if not (move == len(note_log) - 1 and len(note_log) == 48) else 23
                black_text_rect.center = (box_pos[0] + 2 * move_x_gap, move_nr_start_y + row * move_gap)
                screen.blit(black_text, black_text_rect)


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
    evaluation = max_eval - gamestate.eval_log[-1]
    if evaluation < 0:
        evaluation = 0
    elif evaluation > 20:
        evaluation = 20
    p.draw.rect(screen, p.Color("black"), p.Rect(BOARDGAP // 2, BOARDGAP, SQ_SIZE // 2, evaluation * pixels_per_eval))
    # draw middlepoint
    p.draw.rect(screen, p.Color("gold"), p.Rect(BOARDGAP // 2, HEIGHT // 2, SQ_SIZE // 2, SQ_SIZE // 10))


def display_opening(screen, gamestate, box_pos, box_width):
    text_center = [box_pos[0] + box_width // 2, box_pos[1] - SQ_SIZE // 4]
    # background
    p.draw.rect(screen, p.Color("white"), p.Rect(box_pos[0], box_pos[1] - SQ_SIZE // 2, box_width, SQ_SIZE // 2))
    font = p.font.Font('freesansbold.ttf', SQ_SIZE // 4)
    text = font.render(gamestate.opening, False, p.Color("black"))
    textRect = text.get_rect()
    textRect.center = (text_center[0], text_center[1])
    screen.blit(text, textRect)


def display_material_balance(screen, gamestate):
    black_center = (BOARDGAP + int(7 * SQ_SIZE), BOARDGAP - SQ_SIZE // 2)
    white_center = (BOARDGAP + int(7 * SQ_SIZE), BOARDGAP + int(8.5 * SQ_SIZE))
    font = p.font.Font('freesansbold.ttf', SQ_SIZE // 3)
    material = gamestate.material_balance
    white_text = str(gamestate.games_won[0]) + " White +" + str(material) if material > 0 else str(gamestate.games_won[0]) + " White"
    black_text = str(gamestate.games_won[1]) + " Black +" + str(abs(material)) if material < 0 else str(gamestate.games_won[1]) + " Black"
    text_1 = font.render(white_text, False, p.Color("black"))
    text_2 = font.render(black_text, False, p.Color("black"))
    text_1_rect = text_1.get_rect()
    text_2_rect = text_2.get_rect()
    text_1_rect.center = white_center
    text_2_rect.center = black_center
    screen.blit(text_1, text_1_rect)
    screen.blit(text_2, text_2_rect)

