import pygame as pg
import random
import time

WIDTH = 1280
HEIGHT = 720
FPS = 60

pg.init()

SURF = pg.display.set_mode((WIDTH, HEIGHT))
FRAME = SURF.get_rect()

clock = pg.time.Clock()
pg.time.set_timer(101, 500)
pg.display.set_caption("Terraria")

SEED = time.time()
random.seed(SEED)

font = pg.font.Font(None, 15)
font20 = pg.font.Font(None, 20)

BLOCK_SIZE = 32
BLOCK_RECT = pg.rect.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)
WORLD_HEIGHT = 100
WORLD_WIDTH = 200    #default is 1000

# other helpful stuff
BIG = 2147483647