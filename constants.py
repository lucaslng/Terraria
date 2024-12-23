import pygame as pg

WIDTH = 1000
HEIGHT = 600
FPS = 60

pg.init()

SURF = pg.display.set_mode((WIDTH, HEIGHT), vsync=1)
pg.time.set_timer(101, 500)
pg.display.set_caption("Terraria")

BLOCK_SIZE = 25
WORLD_HEIGHT = 256
WORLD_WIDTH = 1000
SHADOW_QUALITY = 3
gravity = 1 