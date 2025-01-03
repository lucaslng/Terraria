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

ironToolsSheet = SpriteSheet("iron_tools.png")

while sigma:
  surf.fill((50,50,50))
  asurf.fill((0,0,0,0))
  
  pickaxe = ironToolsSheet.get(0, 0, 16, 16, 200)
  axe = ironToolsSheet.get(16, 0, 16, 16, 15)
  shovel = ironToolsSheet.get(32, 0, 16, 16, 15)
  sword = ironToolsSheet.get(48, 0, 16, 16, 15)
  
  asurf.blit(pickaxe, (0, 0))
  # asurf.blit(axe, (0, 0))
  # asurf.blit(shovel, (0, 0))
  # asurf.blit(sword, (0, 0))
  
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