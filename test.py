import pygame as pg
from pygame.locals import *
import sys

pg.init()

surf = pg.display.set_mode((800, 800), vsync=1)
asurf = pg.surface.Surface((800,800), pg.SRCALPHA)

class SpriteSheet:
  '''sprite sheet class'''
  def __init__(this, imageName: str):
    this.sheet = pg.image.load(imageName).convert_alpha()
  def get(this, x, y, width, height, scale, colour=(0,0,0)):
    image = pg.Surface((width, height)).convert_alpha()
    image.blit(this.sheet, (0, 0), (x, y, width, height))
    image = pg.transform.scale(image, (scale, scale))
    image.set_colorkey(colour)
    return image

# class Animation:
#   def __init__(this, *args):
#     this.arr: List[pg.surface.Surface] = list(args)

catSheet = SpriteSheet("cat.png")
cat1 = catSheet.get(8, 16, 16, 16, 200)
cat2 = catSheet.get(40, 16, 16, 16, 200)
cat3 = catSheet.get(72, 16, 16, 16, 200)
cat4 = catSheet.get(104, 16, 16, 16, 200)
# cat5 = catSheet.get(135, 272, 16, 16, 200)
# cat6 = catSheet.get(167, 272, 16, 16, 200)
# cat7 = catSheet.get(200, 272, 16, 16, 200)
# cat8 = catSheet.get(232, 272, 16, 16, 200)
# sprites = {

while 1:
  surf.fill((50,50,50))
  asurf.fill((0,0,0,0))
  asurf.blit(cat1, (0,0))
  asurf.blit(cat2, (200,0))
  asurf.blit(cat3, (0,200))
  asurf.blit(cat4, (200,200))
  surf.blit(asurf, (0,0))
  pg.draw.rect(surf,(0,0,0),(0,0,200,200),2)
  pg.draw.rect(surf,(0,0,0),(0,200,200,200),2)
  pg.draw.rect(surf,(0,0,0),(200,0,200,200),2)
  pg.draw.rect(surf,(0,0,0),(200,200,200,200),2)
  pg.display.flip()
  for event in pg.event.get():
      if event.type == QUIT:
        pg.quit()
        sys.exit()