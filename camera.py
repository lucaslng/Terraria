from constants import BLOCK_SIZE, FRAME, SUNLIGHTSURF
from gamestate import GameState
import pygame as pg

from main import Player, World


def drawScreen(gameState: GameState, surf: pg.Surface):
  world: World = gameState.world
  player: Player = gameState.player
  x, y = player.x, player.y
  camera = FRAME.copy()
  camera.center = x, y
  
  visibleBlocks = [
    [(world[y][x], world.back[y][x], world.lightmap[y][x]) for x in range(camera.left // BLOCK_SIZE,
        (camera.right // BLOCK_SIZE) + 1)]
          for y in range(camera.top // BLOCK_SIZE,
            (camera.bottom // BLOCK_SIZE) + 1)
  ]
  
  for row in visibleBlocks:
      for blockTuple in row:
        block, backBlock, light = blockTuple
        if not backBlock.isAir and block.isEmpty:
          backBlock.drawBlock()
        if not block.isAir:
          block.drawBlock()
        pg.draw.rect(SUNLIGHTSURF, (0,0,0,light), player.relativeRect(block.rect))
  
  return surf