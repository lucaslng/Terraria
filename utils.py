import pygame as pg, math
from pygame.locals import *
from abc import ABC, abstractmethod
from dataclasses import dataclass

from constants import *
from entities import *
from inventory import Interactable

player = Player()

class Direction:
  '''Just to make code easier to read'''
  NORTH=0
  SOUTH=1
  WEST=2
  EAST=3

def sysexit() -> None:
  '''Helper function to exit the program'''
  pg.quit()
  raise SystemExit

# @dataclass
# class Executable(ABC):
#   '''Items that have a special effect to be executed when held'''
#   @abstractmethod
#   def execute(self):
#     '''execute whatever needs to be done'''
#     pass
  
#   @abstractmethod
#   def unexecute(self):
#     '''unexecute when item is swapped out'''
#     pass

# # def gaussianBlur(surf: pg.surface.Surface):
# #   '''apply gaussian blur on the alpha value of a surface'''
# #   pxarr = pg.PixelArray(surf)
# #   arr = [[pg.Color(pxarr[x][y]).r for x in range(pxarr.shape[0])] for y in range(pxarr.shape[1])] # not sure why it gets put into the r value but it works
# #   filter = 1 / 9
# #   for y in range(1, pxarr.shape[1] - 1):
# #     for x in range(1, pxarr.shape[0] - 1):
# #       pass
  
# #   return arr

# # s = pg.Surface((10, 10), pg.SRCALPHA)
# # pg.draw.rect(s, (5,8,0,255), (0,0,5,5))

# # print(gaussianBlur(s))


# def pixelToCoord(x: float, y: float) -> tuple[int, int]:
#   '''Returns coordinate based on pixel location'''
#   coord = int((x + player.camera.left) // BLOCK_SIZE), int(
#       (y + player.camera.top) // BLOCK_SIZE
#   )
#   return coord

# def relativeRect(rect: pg.rect.Rect) -> pg.rect.Rect:
#   '''Returns on screen rect relative to the camera'''
#   return pg.rect.Rect(
#       rect.x - player.camera.x, rect.y - player.camera.y, rect.width, rect.height
#   )

# def relativeCoord(x: float, y: float) -> tuple[int, int]:
#   '''Convert a pixel coordinate relative to the camera. Useful for drawing things and more.'''
#   return x - player.camera.x, y - player.camera.y

# def check_for_interaction() -> None:
#   '''loops over every visible block to check for interactable blocks'''
#   for y in range(player.camera.top // BLOCK_SIZE, (player.camera.bottom // BLOCK_SIZE) + 1):
#     for x in range(player.camera.left // BLOCK_SIZE, (player.camera.right // BLOCK_SIZE) + 1):
#       block = world.blockAt(x, y)
#       if isinstance(block, Interactable):
#         dist = math.dist(player.rect.center, block.rect.center)
#         if dist <= 3 * BLOCK_SIZE:
#           block.interact()
#           return

# def bresenham(x0: int, y0: int, x1: int, y1: int, checkVertices=False, quality: int=1):
#   '''Bresenham's algorithm to detect first non-air block along a line, starting from end point.'''
#   pointsTouched = list()
#   def plotLineLow(x0, y0, x1, y1):
#     dx = abs(x1 - x0)
#     dy = abs(y1 - y0)
#     xi = -quality if x0 < x1 else quality
#     yi = -quality if y0 < y1 else quality
#     xii = -1 if x0 < x1 else 1
#     yii = -1 if y0 < y1 else 1
#     d = (2 * dy) - dx
#     y = y1
#     x = x1
#     while x != x0 - xi:
#       # print(x, x0-x1)
#       blockTouched = world.blockAt(*pixelToCoord(x, y))
#       if not blockTouched.isAir:
#         if checkVertices:
#           pointsTouched.append((x, y))
#           if len(pointsTouched) == 2:
#             return pointsTouched
#         else: return x, y
#       if d > 0:
#         y += yi
#         d += 2 * (dy - dx)
#       else:
#         d += 2 * dy
#       x += xi
#       if not 0 <= x < WIDTH or not 0 <= y < HEIGHT: return pointsTouched
#       nextBlock = world.blockAt(*pixelToCoord(x, y))
#       if not nextBlock.isAir:
#         xi = xii
#         yi = yii
#     if checkVertices:
#       pointsTouched.append((x, y))
#       if len(pointsTouched) == 2:
#         return pointsTouched
#     else: return None

#   def plotLineHigh(x0: int, y0: int, x1: int, y1: int) -> tuple[int, int] | None:
#     dx = abs(x1 - x0)
#     dy = abs(y1 - y0)
#     xi = -quality if x0 < x1 else quality
#     yi = -quality if y0 < y1 else quality
#     xii = -1 if x0 < x1 else 1
#     yii = -1 if y0 < y1 else 1
#     d = (2 * dx) - dy
#     x = x1
#     y = y1
#     while y != y0 - yi:
#       blockTouched = world.blockAt(*pixelToCoord(x, y))
#       if not blockTouched.isAir:
#         if checkVertices:
#           pointsTouched.append((x, y))
#           # if len(pointsTouched) == 2:
#           return pointsTouched
#         else: return x, y
#       if d > 0:
#         x += xi
#         d += 2 * (dx - dy)
#       else:
#         d += 2 * dx
#       y += yi
#       if not 0 <= x < WIDTH or not 0 <= y < HEIGHT: return pointsTouched
#       nextBlock = world.blockAt(*pixelToCoord(x, y))
#       if not nextBlock.isAir:
#         xi = xii
#         yi = yii
#     if checkVertices:
#       return pointsTouched
#     else: return None

#   if abs(y1 - y0) < abs(x1 - x0):
#     return plotLineLow(x0, y0, x1, y1)
#   else:
#     return plotLineHigh(x0, y0, x1, y1)