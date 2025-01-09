import pygame as pg
from dataclasses import dataclass
from constants import SUNLIGHTSURF
from utils.utils import coordWorld2Relative

@dataclass
class Light:
  '''Base class for any object with light except the sun'''
  lightRadius: int
  x: float
  y: float
  relative: bool = True
  
  def __post_init__(self):
    # print("post init light")
    lights.append(self)
    
  def drawLight(self):
    '''draw light'''
    if self.relative:
      # print(self.x, self.y, self.x*20, self.y*20, coordWorld2Relative(self.x, self.y))
      pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), coordWorld2Relative(self.x,self.y), self.lightRadius)
    else:
      pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), (self.x,self.y), self.lightRadius)

lights: list[Light] = []