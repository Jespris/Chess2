import pygame as p
from win32api import GetSystemMetrics
import Engine, Display, SmartMoveFinder
from multiprocessing import Process, Queue

WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)
BOARDGAP = HEIGHT // 10
SQ_SIZE = (HEIGHT - 2 * BOARDGAP) // 8
FPS = 30


def main():
    p.init()
    p.mixer.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption('Chess2')
    screen.fill(p.Color("Gray"))
    gamestate = Engine.GameState(WIDTH, HEIGHT, SQ_SIZE, [0, 0])
    gamestate.get_boardstate()
    clock = p.time.Clock()
    sq_selected = ()
    mouse_clicks = []
    mouse_down = False
    legal_moves = gamestate.get_legal_moves()
    move_made = False
    Display.load_images()
    game_over = False
    white_human = True
    black_human = False
    play_alap = True
    show_eval = True
    AI_thinking = False
    move_finder_process = None
    flag = True
    while flag:
        is_human_turn = (gamestate.white_to_move and white_human) or (not gamestate.white_to_move and black_human)
        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    flag = False
                if e.key == p.K_z:
                    gamestate.undo_move()
                    move_made = True  # will call get_legal moves later
                    game_over = False
                    if gamestate.eval_log:
                        gamestate.eval_log.pop()
                if e.key == p.K_n:
                    gamestate.promote_to = 3 if gamestate.white_to_move else -3
                if e.key == p.K_b:
                    gamestate.promote_to = 4 if gamestate.white_to_move else -4
                if e.key == p.K_r:
                    gamestate.promote_to = 2 if gamestate.white_to_move else -2
            if e.type == p.KEYUP:
                gamestate.promote_to = 5 if gamestate.white_to_move else -5
            if e.type == p.MOUSEBUTTONDOWN:
                mouse_down = True
                mouse_pos = p.mouse.get_pos()
                if not game_over:
                    col = (mouse_pos[0] - BOARDGAP) // SQ_SIZE
                    row = (mouse_pos[1] - BOARDGAP) // SQ_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:  # inside board
                        if sq_selected == (row, col):  # same piece twice
                            sq_selected = ()  # deselect
                            mouse_clicks = []
                        else:
                            if sq_selected:
                                if gamestate.board[row][col] and gamestate.board[sq_selected[0]][sq_selected[1]] / gamestate.board[row][col] > 0:  #clicked same color piece
                                    sq_selected = (row, col)
                                    mouse_clicks = [sq_selected]
                                else:
                                    sq_selected = (row, col)
                                    mouse_clicks.append(sq_selected)
                            else:
                                sq_selected = (row, col)
                                mouse_clicks.append(sq_selected)
                        if len(mouse_clicks) == 2 and is_human_turn:  # successful move
                            move = Engine.Move(mouse_clicks[0], mouse_clicks[1], gamestate.board)
                            for i in range(len(legal_moves)):
                                if move == legal_moves[i]:
                                    move = legal_moves[i]
                                    gamestate.make_move(move)
                                    gamestate.get_opening()
                                    gamestate.evaluate_endgame()
                                    gamestate.eval_log.append(SmartMoveFinder.score_board(gamestate))
                                    # play_sound('move_piece', 0.5)
                                    move_made = True
                                    sq_selected = ()  # reset clicks
                                    mouse_clicks = []
                            if not move_made:
                                mouse_clicks = [sq_selected]
                reset_pos, reset_size = Display.get_reset_button()
                if reset_pos[0] < mouse_pos[0] < reset_pos[0] + reset_size[0] and reset_pos[1] < mouse_pos[1] < reset_pos[1] + reset_size[1]:
                    gamestate = Engine.GameState(WIDTH, HEIGHT, SQ_SIZE, gamestate.games_won)
                    legal_moves = gamestate.get_legal_moves()
                    sq_selected = ()
                    mouse_clicks = []
                    game_over = False
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
                            if gamestate.board[row][col] and gamestate.board[sq_selected[0]][sq_selected[1]] / gamestate.board[row][col] > 0:  # clicked same color piece
                                sq_selected = ()  # clear selection
                                mouse_clicks = []
                            else:
                                sq_selected = (row, col)
                                mouse_clicks.append(sq_selected)
                        else:
                            sq_selected = ()
                            mouse_clicks = []
                    if len(mouse_clicks) == 2 and is_human_turn:  # successful move
                        move = Engine.Move(mouse_clicks[0], mouse_clicks[1], gamestate.board)
                        print(move.get_notation())
                        for i in range(len(legal_moves)):
                            if move == legal_moves[i]:
                                move = legal_moves[i]
                                gamestate.make_move(move)
                                gamestate.get_opening()
                                gamestate.evaluate_endgame()
                                gamestate.eval_log.append(SmartMoveFinder.score_board(gamestate))
                                # play_sound('move_piece', 0.5)
                                move_made = True
                                sq_selected = ()  # reset clicks
                                mouse_clicks = []
                                break
                        if not move_made:
                            sq_selected = ()
                            mouse_clicks = []

        # AI moves
        if not game_over and not is_human_turn:
            if not AI_thinking:
                # threading to interact with board while ai is thinking
                AI_thinking = True
                print("thinking...")
                return_queue = Queue()  # used to pass data between threads
                move_finder_process = Process(target=SmartMoveFinder.find_best_move, args=(gamestate, legal_moves, return_queue))
                move_finder_process.start()  # call find_best_move(gamestate, legal_moves, return_queue)

            if not move_finder_process.is_alive():
                print("done thinking")
                (AI_move, board_states_depth, opening_name, in_opening) = return_queue.get()
                gamestate.states_depth_log.append(board_states_depth)
                gamestate.in_opening = in_opening
                gamestate.opening = opening_name
                if AI_move is None:
                    AI_move = SmartMoveFinder.find_random_move(legal_moves)
                gamestate.make_move(AI_move)
                gamestate.evaluate_endgame()
                gamestate.eval_log.append(SmartMoveFinder.score_board(gamestate))
                # play_sound('move_piece', 0.5)
                print("Played move: " + AI_move.get_notation())
                move_made = True
                AI_thinking = False

        if move_made:
            legal_moves = gamestate.get_legal_moves()
            gamestate.get_draw()

        Display.display_board(screen, gamestate, sq_selected, legal_moves, mouse_down, p.mouse.get_pos(),
                              ((not white_human and not black_human) or show_eval))

        # Checkmate and draw
        if gamestate.checkmate:
            if gamestate.white_to_move:
                Display.display_game_over(screen, gamestate, "Black wins by checkmate!")
                if not game_over:
                    gamestate.games_won[1] += 1
            else:
                Display.display_game_over(screen, gamestate, "White wins by checkmate!")
                if not game_over:
                    gamestate.games_won[0] += 1
            game_over = True
        elif gamestate.draw:
            # only add scores once
            if not game_over:
                gamestate.games_won[0] += 0.5
                gamestate.games_won[1] += 0.5
            game_over = True
            Display.display_game_over(screen, gamestate, "Draw!")

        if game_over and play_alap and (not white_human and not black_human):  # play forever
            gamestate = Engine.GameState(WIDTH, HEIGHT, SQ_SIZE, gamestate.games_won)
            legal_moves = gamestate.get_legal_moves()
            game_over = False

        clock.tick(FPS)
        p.display.flip()


def play_sound(sound_name, volume):
    sound = p.mixer.Sound('sounds/' + sound_name + '.mp3')
    sound.set_volume(volume)
    sound.play()


if __name__ == "__main__":
    main()