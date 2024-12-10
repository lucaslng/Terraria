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
  # print(coord)
  return coord

def relativeRect(rect:pg.rect.Rect): # on screen rect relative to the camera
  return pg.rect.Rect(rect.x - player.camera.x, rect.y - player.camera.y, rect.width, rect.height)

class Entity:
  
  hvelo = 0
  vvelo = 0
  gravityvelo = 0
  previousDirection = True
  
  def __init__(this, x:float, y:float, width:float, height:float, texture:pg.surface.Surface):
    this.rect = pg.rect.Rect(x, y, width, height)
    this.texture = texture
    this.reversedTexture = pg.transform.flip(texture, True, False)
    this.mask = pg.mask.from_surface(texture)
    
  def moveLeft(this):
    if this.hvelo > -5: this.hvelo -= 2
  def moveRight(this):
    if this.hvelo < 5: this.hvelo += 2
  def jump(this):
    if this.isOnBlock(): this.vvelo -= 7
  def gravity(this):
    if not this.isOnBlock():
      if this.gravityvelo < 5: this.gravityvelo += GRAVITY
    else:
      this.gravityvelo = 0
  
  def move(this):
    # print(this.rect.centerx//20, this.rect.centery//20)
    
    if this.hvelo < 0: this.hvelo += min(1, abs(this.hvelo)) # reduce horizontal velocity constantly to 0
    elif this.hvelo > 0: this.hvelo -= min(1, this.hvelo)
    
    this.vvelo += min(0.5, abs(this.vvelo)) # reduce vertical velocity constantly to 0
    
    # print(this.hvelo, this.vvelo)
    
    newrect = this.rect.copy()
    newrect.x += this.hvelo
    newrect.y += this.vvelo
    # print(newrect.right, newrect.top)
    blockTop = world.blockAt(newrect.right//20, newrect.top//20-1)
    blockTopRight = world.blockAt(newrect.right//20+1, newrect.top//20-1)
    blockTopLeft = world.blockAt(newrect.left//20, newrect.top//20-1)
    blockRightTop = world.blockAt(newrect.right//20+1, newrect.top//20)
    blockRightBot = world.blockAt(newrect.right//20+1, newrect.centery//20)
    blockBotRight = world.blockAt(newrect.right//20+1, newrect.bottom//20)
    blockBot = world.blockAt(newrect.right//20, newrect.bottom//20)
    blockBotLeft = world.blockAt(newrect.left//20, newrect.bottom//20)
    blockLeftBot = world.blockAt(newrect.left//20, newrect.centery//20)
    blockLeftTop = world.blockAt(newrect.left//20, newrect.top//20)
    pg.draw.rect(SURF, (0,0,0), relativeRect(newrect), width=3)
    if blockRightBot.collides(*newrect.topleft):
      print("collides rbot")
    else: print("no")
    if blockLeftBot.collides(*newrect.topleft):
      print("collides lbot")
    else: print("no")
    # pg.draw.rect(SURF, (0,0,0),relativeRect(blockTop.rect),3)
    # pg.draw.rect(SURF, (255,0,0),relativeRect(blockTopRight.rect),3)
    # pg.draw.rect(SURF, (0,255,0),relativeRect(blockTopLeft.rect),3)
    # pg.draw.rect(SURF, (0,0,255),relativeRect(blockRightTop.rect),3)
    # pg.draw.rect(SURF, (255,0,255),relativeRect(blockRightBot.rect),3)
    # pg.draw.rect(SURF, (255,255,0),relativeRect(blockBotRight.rect),3)
    # pg.draw.rect(SURF, (0,255,255),relativeRect(blockBot.rect),3)
    # pg.draw.rect(SURF, (128,255,128),relativeRect(blockBotLeft.rect),3)
    # pg.draw.rect(SURF, (255,128,128),relativeRect(blockLeftBot.rect),3)
    # pg.draw.rect(SURF, (128,128,255),relativeRect(blockLeftTop.rect),3)
    # if blockTop.mask.overlap(this.mask, blockTop.offset(*newrect.topleft)):
    #   print("yes")
    # else:
    #   print("no")
      
    this.rect.x += this.hvelo
    
    this.rect.y += this.gravityvelo # gravity drop
    this.gravity() # update gravityvelo
  
  def isOnBlock(this):
    return not world[(this.rect.bottom//20)][this.rect.centerx//20].isAir
  
  def draw(this):
    pass
    if this.hvelo < 0:
      SURF.blit(this.reversedTexture, relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.reversedTexture)
      this.previousDirection = 0
    elif this.hvelo > 0:
      SURF.blit(this.texture, relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.texture)
      this.previousDirection = 1
    elif this.previousDirection:
      SURF.blit(this.texture, relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.texture)
    else:
      SURF.blit(this.reversedTexture,relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.reversedTexture)

class Player(Entity):
  camera = FRAME.copy()
  camera.center = (BLOCK_SIZE * (WORLD_WIDTH // 2), BLOCK_SIZE * round(WORLD_HEIGHT * 0.55))
  SPEED = BLOCK_SIZE // 4
  texture = pg.transform.scale(pg.image.load("player.png"), (BLOCK_SIZE, BLOCK_SIZE*2))
  reversedTexture = pg.transform.flip(texture, True, False)
  
  def __init__(this):
    super().__init__(this.camera.centerx-BLOCK_SIZE//2, this.camera.centery-BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE*2, this.texture)
    this.rect.center = this.camera.center
    this.centerRect = this.rect.copy()
    this.centerRect.center = FRAME.center
  
  def move(this):
    super().move()
    this.camera.center = this.rect.center
  
  def mine(this, block):
    world[block.y][block.x] = Air(block.x, block.y)
  

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
  def __init__(this, name:str, itemTexture, blockTexture, stackSize:int, x:int, y:int, isAir=False):
    super().__init__(name, itemTexture, stackSize)
    this.blockTexture = blockTexture
    this.rect = pg.rect.Rect(x*20, y*20, this.SIZE, this.SIZE)
    this.mask = pg.mask.from_surface(blockTexture)
    this.x = x
    this.y = y
    this.isAir = isAir
  
  def drawBlock(this):
    SURF.blit(this.blockTexture, relativeRect(this.rect))
  
  def offset(this, x:int, y:int) -> tuple[int, int]:
    return x - this.rect.x, y - this.rect.y
  
  def collides(this, x:int, y:int) -> bool:
    if this.mask.overlap(player.mask, this.offset(x, y)):
      pg.draw.rect(SURF, (255,0,0), relativeRect(this.rect),width=3)
      return True
    else:
      return False
  
  def isInCamera(this):
    return this.rect.colliderect(player.camera)
  
class Air(Block):
  texture = pg.surface.Surface((20,20))
  texture.fill((0,0,0,0))
  def __init__(this, x, y):
    super().__init__("Air", this.texture, this.texture, 0, x, y, isAir = True)

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
    return this.blockAt(*pixelToCoord(*mousepos))
  
  def blockAt(this, x, y) -> Block:
    return this[y][x]
  
  def __getitem__(this, x:int):
    return this.array[x]
  
  def draw(this):
    for y in range(player.camera.top//20, (player.camera.bottom//20)+1):
      for x in range(player.camera.left//20, (player.camera.right//20) + 1):
        if not this[y][x].isAir:
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
# print(world)
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