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
    p.display.set_caption('Chess2')
    screen.fill(p.Color("Gray"))
    gamestate = Engine.GameState(WIDTH, HEIGHT, SQ_SIZE)
    clock = p.time.Clock()
    sq_selected = ()
    mouse_clicks = []
    mouse_down = False
    legal_moves = gamestate.get_legal_moves()
    move_made = False
    Display.load_images()
    game_over = False
    flag = True
    while flag:
        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    flag = False
                if e.key == p.K_z:
                    gamestate.undo_move()
                    move_made = True  # will call get_legal moves later
                if e.key == p.K_n:
                    gamestate.promote_to = 'n'
                if e.key == p.K_b:
                    gamestate.promote_to = 'b'
                if e.key == p.K_r:
                    gamestate.promote_to = 'r'
            if e.type == p.KEYUP:
                gamestate.promote_to = 'q'
            if e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    mouse_down = True
                    mouse_pos = p.mouse.get_pos()
                    col = (mouse_pos[0] - BOARDGAP) // SQ_SIZE
                    row = (mouse_pos[1] - BOARDGAP) // SQ_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:  # inside board
                        if sq_selected == (row, col):  # same piece twice
                            sq_selected = ()  # deselect
                            mouse_clicks = []
                        else:
                            if sq_selected:
                                if gamestate.board[sq_selected[0]][sq_selected[1]][0] == gamestate.board[row][col][0]:  #clicked same color piece
                                    sq_selected = (row, col)
                                    mouse_clicks = [sq_selected]
                                else:
                                    sq_selected = (row, col)
                                    mouse_clicks.append(sq_selected)
                            else:
                                sq_selected = (row, col)
                                mouse_clicks.append(sq_selected)
                        if len(mouse_clicks) == 2:  # successful move
                            move = Engine.Move(mouse_clicks[0], mouse_clicks[1], gamestate.board)
                            print(move.get_notation())
                            for i in range(len(legal_moves)):
                                if move == legal_moves[i]:
                                    move = legal_moves[i]
                                    gamestate.make_move(move)
                                    move_made = True
                                    sq_selected = ()  # reset clicks
                                    mouse_clicks = []
                            if not move_made:
                                mouse_clicks = [sq_selected]
                    reset_pos, reset_size = Display.get_reset_button()
                    if reset_pos[0] < mouse_pos[0] < reset_pos[0] + reset_size[0] and reset_pos[1] < mouse_pos[1] < reset_pos[1] + reset_size[1]:
                        gamestate = Engine.GameState(WIDTH, HEIGHT, SQ_SIZE)
                        legal_moves = gamestate.get_legal_moves()
                        sq_selected = ()
                        mouse_clicks = []
            if e.type == p.MOUSEBUTTONUP:
                mouse_down = False
                mouse_pos = p.mouse.get_pos()
                col = (mouse_pos[0] - BOARDGAP) // SQ_SIZE
                row = (mouse_pos[1] - BOARDGAP) // SQ_SIZE
                if 0 <= row < 8 and 0 <= col < 8:  # inside board
                    if sq_selected == (row, col):  # same piece twice
                        sq_selected = (row, col)  # hold selection
                        mouse_clicks = [sq_selected]
                    else:
                        if sq_selected:
                            if gamestate.board[sq_selected[0]][sq_selected[1]][0] == gamestate.board[row][col][0]:  # clicked same color piece
                                sq_selected = ()  # clear selection
                                mouse_clicks = []
                            else:
                                sq_selected = (row, col)
                                mouse_clicks.append(sq_selected)
                        else:
                            sq_selected = ()
                            mouse_clicks = []
                    if len(mouse_clicks) == 2:  # successful move
                        move = Engine.Move(mouse_clicks[0], mouse_clicks[1], gamestate.board)
                        print(move.get_notation())
                        for i in range(len(legal_moves)):
                            if move == legal_moves[i]:
                                move = legal_moves[i]
                                gamestate.make_move(move)
                                move_made = True
                                sq_selected = ()  # reset clicks
                                mouse_clicks = []
                        if not move_made:
                            mouse_clicks = [sq_selected]
        if move_made:
            legal_moves = gamestate.get_legal_moves()

        Display.display_board(screen, gamestate, sq_selected, legal_moves, mouse_down, p.mouse.get_pos())

        if gamestate.checkmate:
            game_over = True
            if gamestate.white_to_move:
                Display.display_game_over(screen, gamestate, "Black wins by checkmate!")
            else:
                Display.display_game_over(screen, gamestate, "White wins by checkmate!")
        elif gamestate.draw:
            game_over = True
            Display.display_game_over(screen, gamestate, "Draw!")

        clock.tick(FPS)
        p.display.flip()


if __name__ == "__main__":
    main()