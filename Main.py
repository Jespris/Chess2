import pygame as p
from win32api import GetSystemMetrics
from Chess import Engine, Display

WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)
BOARDGAP = HEIGHT // 10
SQ_SIZE = (HEIGHT - 2 * BOARDGAP) // 8
FPS = 30



def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    screen.fill(p.Color("Gray"))
    gamestate = Engine.GameState(WIDTH, HEIGHT, SQ_SIZE)
    clock = p.time.Clock()
    sq_selected = ()
    mouse_clicks = []
    legal_moves = gamestate.get_legal_moves()
    move_made = False
    Display.load_images()
    flag = True
    while flag:
        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    flag = False
                if e.key == p.K_z:
                    gamestate.undo_move()
                    move_made = True  # will call get_legal moves later
            if e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                col = (mouse_pos[0] - BOARDGAP) // SQ_SIZE
                row = (mouse_pos[1] - BOARDGAP) // SQ_SIZE
                if 0 <= row < 8 and 0 <= col < 8:  # inside board
                    if sq_selected == (row, col):  # same piece twice
                        sq_selected = ()  # deselect
                        mouse_clicks = []
                    else:
                        sq_selected = (row, col)
                        mouse_clicks.append(sq_selected)
                    if len(mouse_clicks) == 2:  # successful move
                        move = Engine.Move(mouse_clicks[0], mouse_clicks[1], gamestate.board)
                        print(move.get_notation())
                        if move in legal_moves:
                            gamestate.make_move(move)
                            move_made = True
                        sq_selected = ()  # reset clicks
                        mouse_clicks = []
        if move_made:
            legal_moves = gamestate.get_legal_moves()
        Display.display_board(screen, gamestate)
        clock.tick(FPS)
        p.display.flip()


if __name__ == "__main__":
    main()