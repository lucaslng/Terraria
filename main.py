import sys
import pygame as pg
from pygame.locals import *
import math
import random
from enum import Enum

pg.init()
WIDTH = 1000
HEIGHT = 600
FPS = 60
SURF = pg.display.set_mode((WIDTH, HEIGHT))
FRAME = SURF.get_rect()
BLOCK_SIZE = 20
WORLD_HEIGHT = 100
WORLD_WIDTH = 100
GRAVITY = 0.1
pg.display.set_caption("Terraria")
clock = pg.time.Clock()

class Player:
  camera = FRAME.copy()
  camera.center = (BLOCK_SIZE * (WORLD_WIDTH // 2), BLOCK_SIZE * round(WORLD_HEIGHT * 0.6))
  SPEED = BLOCK_SIZE // 4
  JUMP_HEIGHT = BLOCK_SIZE * 3
  texture = pg.transform.scale(pg.image.load("player.png"), (BLOCK_SIZE, BLOCK_SIZE*2))
  rect = pg.rect.Rect(camera.centerx-BLOCK_SIZE//2, camera.centery-BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE*2)
  dropSpeed = 0
  
  def updateRect(this):
    this.rect = pg.rect.Rect(this.camera.centerx-BLOCK_SIZE//2, this.camera.centery-BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE*2)
  def moveLeft(this):
    this.camera.center = (this.camera.centerx - this.SPEED, this.camera.centery)
    this.updateRect()
  def moveRight(this):
    this.camera.center = (this.camera.centerx + this.SPEED, this.camera.centery)
    this.updateRect()
  def jump(this):
    this.camera.center = (this.camera.centerx, this.camera.centery - this.JUMP_HEIGHT)
    this.updateRect()
  def drop(this):
    this.camera.center = (this.camera.centerx, this.camera.centery + this.dropSpeed)
    this.updateRect()
  def gravity(this):
    this.dropSpeed += GRAVITY
    if this.onBlock(): this.dropSpeed = 0
  def onBlock(this):
    if world[(this.rect.bottom//20) - 1][this.rect.centerx//20].name != "Air":
      return True
    else: return False
  
  
player = Player()

airTexture = pg.transform.scale(pg.image.load("air.jpg"), (BLOCK_SIZE, BLOCK_SIZE))
dirtTexture = pg.transform.scale(pg.image.load("dirt.png"), (BLOCK_SIZE, BLOCK_SIZE))
class Item:
  ITEM_SIZE = 20
  def __init__(this, name:str, itemTexture, stackSize:int):
    this.itemTexture = itemTexture
    this.stackSize = stackSize
    this.name = name
    # print(this.itemTextureFile)
  def drawItem(this, x:int, y:int):
    SURF.blit(this.itemTexture, (x, y))

class Block(Item):
  SIZE = BLOCK_SIZE
  def __init__(this, name:str, itemTexture, blockTexture, stackSize:int, x:int, y:int):
    super().__init__(name, itemTexture, stackSize)
    this.blockTexture = blockTexture
    this.rect = pg.rect.Rect(x*20, y*20, this.SIZE, this.SIZE)
    this.x = x
    this.y = y
  
  def drawBlock(this):
    SURF.blit(this.blockTexture, this.__relativeRect())
  
  def isInCamera(this):
    return this.rect.colliderect(player.camera)
  
  def __relativeRect(this): # on screen rect relative to the camera
    return pg.rect.Rect(this.rect.x - player.camera.x, this.rect.y - player.camera.y, this.SIZE, this.SIZE)

class Air(Block):
  def __init__(this, x, y):
    super().__init__("Air", airTexture, airTexture, 0, x, y)

class Dirt(Block):
  def __init__(this, x, y):
    super().__init__("Dirt", dirtTexture, dirtTexture, 64, x, y)

class World:
  def __init__(this):
    this.array = [[Air(x, y) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)]
    this.__generateAllDirt()
    
  
  # https://gpfault.net/posts/perlin-noise.txt.html
  # not currently using perlin noise tho
  def __generateDirtHeight(this, x:int) -> int:
    return round(0.5 * (-1.6 * 1.4 * math.sin(0.3 * math.e * x) + 1.6 * math.sin(-0.2 * math.pi * x)))
  
  def __generateAllDirt(this):
    for x in range(0, WORLD_WIDTH):
      for y in range(WORLD_HEIGHT-1, round(WORLD_HEIGHT*0.6) + this.__generateDirtHeight(x), -1):
        this.array[y][x] = Dirt(x, y)
  
  def __getitem__(this, x:int):
    return this.array[x]
  
  def draw(this):
    for row in this.array:
      for block in row:
        if block.isInCamera(): block.drawBlock()
  
  def __repr__(this):
    out = ""
    for row in this.array:
      for block in row:
        if block.name == "Air":
          out += "."
        elif block.name == "Dirt":
          out += "X"
      out += "\n"
    return out

world = World()
print(world)
while True:
  SURF.fill((255, 255, 255))
  keys = pg.key.get_pressed()
  world.draw()
  player.drop()
  player.gravity()
  
  if keys[pg.K_a]: player.moveLeft()
  if keys[pg.K_d]: player.moveRight()
  
  
  for event in pg.event.get():
    if keys[pg.K_SPACE]: player.jump()
    if event.type == QUIT:
      pg.quit()
      sys.exit()
  
  pg.display.flip()
  clock.tick(FPS)