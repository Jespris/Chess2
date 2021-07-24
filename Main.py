import pygame as p
from win32api import GetSystemMetrics
from Chess import Engine

WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)
SQ_SIZE = (HEIGHT // 5) // 8
FPS = 30
IMAGES = {}


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    screen.fill(p.Color("Gray"))
    clock = p.time.Clock()
    flag = True
    while flag:
        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    flag = False
        clock.tick(FPS)
        p.display.flip()





if __name__ == "__main__":
    main()