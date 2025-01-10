import pygame as pg
from pygame.locals import *
import sys

pg.init()

sigma = True

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

everythingSheet = SpriteSheet("everything.png")

while sigma:
  surf.fill((50,50,50))
  asurf.fill((0,0,0,0))
  
  cobblestone = everythingSheet.get(528, 0, 16, 16, 25)
  goldAxe = everythingSheet.get(192, 0, 16, 16, 15)
  goldPickaxe = everythingSheet.get(208, 0, 16, 16, 15)
  
  
  asurf.blit(cobblestone, (0, 0))
  asurf.blit(goldPickaxe, (200, 0))
  
  surf.blit(asurf, (0,0))
  
  pg.draw.rect(surf,(0,0,0),(0,0,200,200),2)
  pg.draw.rect(surf,(0,0,0),(0,200,200,200),2)
  pg.draw.rect(surf,(0,0,0),(200,0,200,200),2)
  pg.draw.rect(surf,(0,0,0),(200,200,200,200),2)
  
  for event in pg.event.get():
      if event.type == QUIT:
        pg.quit()
        sys.exit()
        
  pg.display.flip()