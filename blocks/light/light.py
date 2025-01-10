from dataclasses import dataclass
import pygame as pg

@dataclass
class Light:
  '''Base class for any class with light except the sun'''
  lightRadius: int
  # def drawLight(self):
  #   '''draw light'''
  #   if self.relative:
  #     # print(self.x, self.y, self.x*20, self.y*20, player.coordWorld2Relative(self.x, self.y))
  #     pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), player.coordWorld2Relative(self.x,self.y), self.lightRadius)
  #   else:
  #     pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), (self.x,self.y), self.lightRadius)