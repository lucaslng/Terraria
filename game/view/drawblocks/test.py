from time import perf_counter
import pygame as pg

BLOCK_SIZE = 32

blockRect = pg.rect.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)

start = perf_counter()
for i in range(1000000):
	rect = pg.rect.Rect(20, 20, BLOCK_SIZE, BLOCK_SIZE)
print(f'create time: {round(perf_counter()-start, 3)}')

start = perf_counter()
for i in range(1000000):
	rect = blockRect.copy()
	rect.topleft = 20, 20
print(f'copy time: {round(perf_counter()-start, 3)}')