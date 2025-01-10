from constants import BLOCK_SIZE, pg
from sprites import pg
from utils.utils import pg


import pygame as pg


def rectWorld2Pixel(rect: pg.rect.Rect) -> pg.rect.Rect:
  '''convert world rect to pixel rect'''
  return pg.rect.Rect(rect.left * BLOCK_SIZE, rect.top * BLOCK_SIZE, rect.width * BLOCK_SIZE, rect.height * BLOCK_SIZE)