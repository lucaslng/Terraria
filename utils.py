import pygame as pg
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