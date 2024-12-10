import sys
import pygame as pg
from pygame.locals import *
import math
import random
from enum import Enum
import pickle # use pickle to store save

pg.init()
WIDTH = 1000
HEIGHT = 600
FPS = 60
SURF = pg.display.set_mode((WIDTH, HEIGHT))
FRAME = SURF.get_rect()
BLOCK_SIZE = 20
WORLD_HEIGHT = 100
WORLD_WIDTH = 1000
GRAVITY = 0.05
pg.display.set_caption("Terraria")
clock = pg.time.Clock()

def pixelToCoord(x:int, y:int):
  coord = (x + player.camera.left) // 20, (y + player.camera.top) // 20
  print(coord)
  return coord

class Player:
  camera = FRAME.copy()
  camera.center = (BLOCK_SIZE * (WORLD_WIDTH // 2), BLOCK_SIZE * round(WORLD_HEIGHT * 0.55))
  SPEED = BLOCK_SIZE // 4
  texture = pg.transform.scale(pg.image.load("player.png"), (BLOCK_SIZE, BLOCK_SIZE*2))
  reversedTexture = pg.transform.flip(texture, True, False)
  rect = pg.rect.Rect(camera.centerx-BLOCK_SIZE//2, camera.centery-BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE*2)
  hvelo = 0 # horizontal and vertical velocity
  vvelo = 0
  gravityvelo = 0
  previousDirection = True # true for right, false for left
  
  
  def move(this):
    print(this.rect.centerx//20, this.rect.centery//20)
    this.rect.y += this.gravityvelo
    this.gravity()
    if this.hvelo < 0: this.hvelo += min(1, abs(this.hvelo))
    elif this.hvelo > 0: this.hvelo -= min(1, this.hvelo)
    this.vvelo += min(0.5, abs(this.vvelo))
    print(this.hvelo, this.vvelo)
    if world[(this.rect.bottom//20)][((this.rect.centerx+this.hvelo)//20)].name == "Air" and world[(this.rect.top//20)][((this.rect.centerx+this.hvelo)//20)].name == "Air":
      this.rect.x += this.hvelo
    if world[int((this.rect.bottom+this.vvelo)/20)+1][(this.rect.centerx//20)].name == "Air":
      this.rect.y += this.vvelo
    this.camera.center = this.rect.center
  
  def moveLeft(this):
    if this.hvelo > -5: this.hvelo -= 2
  def moveRight(this):
    if this.hvelo < 5: this.hvelo += 2
  def jump(this):
    if this.onBlock(): this.vvelo -= 7
  def gravity(this):
    if not this.onBlock():
      if this.gravityvelo < 5: this.gravityvelo += GRAVITY
    else:
      this.gravityvelo = 0
    
    
  def onBlock(this):
    if world[(this.rect.bottom//20) + 1][this.rect.centerx//20].name != "Air":
      return True
    else: return False
  
  def mine(this, block):
    world[block.y][block.x] = Air(block.x, block.y)
  
  def draw(this):
    if this.hvelo < 0:
      SURF.blit(this.reversedTexture, FRAME.center)
      this.previousDirection = 0
    elif this.hvelo > 0:
      SURF.blit(this.texture, FRAME.center)
      this.previousDirection = 1
    elif this.previousDirection:
      SURF.blit(this.texture, FRAME.center)
    else:
      SURF.blit(this.reversedTexture,FRAME.center)

  
  
player = Player()

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
  texture = pg.transform.scale(pg.image.load("air.jpg"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(this, x, y):
    super().__init__("Air", this.texture, this.texture, 0, x, y)

class Dirt(Block):
  texture = pg.transform.scale(pg.image.load("dirt.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(this, x, y):
    super().__init__("Dirt", this.texture, this.texture, 64, x, y)

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
  
  def hoveredBlock(this) -> Block:
    mousepos = pg.mouse.get_pos()
    x, y = pixelToCoord(*mousepos)
    return this[y][x]
  
  def __getitem__(this, x:int):
    return this.array[x]
  
  def draw(this):
    for y in range(player.camera.top//20, (player.camera.bottom//20)+1):
      for x in range(player.camera.left//20, (player.camera.right//20) + 1):
        this[y][x].drawBlock()
  
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
  player.draw()
  player.move()
  
  if keys[pg.K_a]: player.moveLeft()
  if keys[pg.K_d]: player.moveRight()
  if keys[pg.K_SPACE]: player.jump()
  
  for event in pg.event.get():
    if pg.mouse.get_pressed()[0]:
      player.mine(world.hoveredBlock())
    if event.type == QUIT:
      pg.quit()
      sys.exit()
  
  pg.display.flip()
  clock.tick(FPS)