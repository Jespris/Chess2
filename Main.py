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
    Display.load_images()
    flag = True
    while flag:
        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    flag = False
            if e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                gamestate.mouseclicks(mouse_pos)
        Display.display_board(screen, gamestate)
        clock.tick(FPS)
        p.display.flip()





if __name__ == "__main__":
    main()