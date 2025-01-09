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