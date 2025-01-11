import pygame as pg
import random
import time

WIDTH = 1280
HEIGHT = 720
FPS = 60

pg.init()

SURF = pg.display.set_mode((WIDTH, HEIGHT))
SUNLIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
LIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
FRAME = SURF.get_rect()
ASURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
OVERLAY = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)

clock = pg.time.Clock()
pg.time.set_timer(101, 500)
pg.display.set_caption("Terraria")

SEED = time.time()
random.seed(SEED)

font = pg.font.Font(None, 15)
font20 = pg.font.Font(None, 20)

BLOCK_SIZE = 32
WORLD_HEIGHT = 256
WORLD_WIDTH = 500    #default is 2500
SHADOW_QUALITY = 3
gravity = 1 

# other helpful stuff
BIG = 2147483647