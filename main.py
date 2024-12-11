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
gravity = 1
pg.display.set_caption("Terraria")
clock = pg.time.Clock()

def pixelToCoord(x:int, y:int):
  coord = (x + player.camera.left) // BLOCK_SIZE, (y + player.camera.top) // BLOCK_SIZE
  # print(coord)
  return coord

def relativeRect(rect:pg.rect.Rect): # on screen rect relative to the camera
  return pg.rect.Rect(rect.x - player.camera.x, rect.y - player.camera.y, rect.width, rect.height)

class Item:
  ITEM_SIZE = BLOCK_SIZE
  def __init__(this, name:str, itemTexture, stackSize:int):
    this.itemTexture = itemTexture
    this.stackSize = stackSize
    this.name = name
    # print(this.itemTextureFile)
  def drawItem(this, x:int, y:int):
    SURF.blit(this.itemTexture, (x, y))

class Inventory:
  def __init__(this, rows:int, cols:int):
    this.inventory = [[Item for _ in range(cols)] for _ in range(rows)]
  
  def __getitem__(this, row:int):
    return this.inventory[row]

class HasInventory:
  def __init__(this, rows:int, cols:int):
    this.inventory = Inventory(rows, cols)

class Entity:
  
  hvelo = 0
  vvelo = 0
  gravityvelo = 0
  previousDirection = True
  isOnBlock = False
  
  def __init__(this, x:float, y:float, width:float, height:float, texture:pg.surface.Surface, health:float):
    this.rect = pg.rect.Rect(x, y, width, height)
    this.texture = texture
    this.reversedTexture = pg.transform.flip(texture, True, False)
    this.mask = pg.mask.from_surface(texture)
    this.health = health
    
  def moveLeft(this):
    if this.hvelo > -5: this.hvelo -= 2
  def moveRight(this):
    if this.hvelo < 5: this.hvelo += 2
  def jump(this):
    if this.vvelo > 4 and this.isOnBlock: this.vvelo -= 18
  
  def checkCollisionH(this) -> int:
    newrect = this.rect.copy()
    newrect.x += this.hvelo - 1
    blockRightTop = world.blockAt(newrect.right//BLOCK_SIZE, (newrect.top+10)//BLOCK_SIZE)
    blockRightBot = world.blockAt(newrect.right//BLOCK_SIZE, (newrect.centery+10)//BLOCK_SIZE)
    blockLeftBot = world.blockAt(newrect.left//BLOCK_SIZE, (newrect.centery+10)//BLOCK_SIZE)
    blockLeftTop = world.blockAt(newrect.left//BLOCK_SIZE, (newrect.top+10)//BLOCK_SIZE)
    # pg.draw.rect(SURF, (0,0,255),relativeRect(blockRightTop.rect),3)
    # pg.draw.rect(SURF, (255,0,255),relativeRect(blockRightBot.rect),3)
    # pg.draw.rect(SURF, (255,128,128),relativeRect(blockLeftBot.rect),3)
    # pg.draw.rect(SURF, (255,0,0),relativeRect(blockLeftTop.rect),3)
    if blockRightBot.collides(*newrect.topleft) or blockRightTop.collides(*newrect.topleft) or blockLeftBot.collides(*newrect.topleft) or blockLeftTop.collides(*newrect.topleft):
      # print("side collides! not moving!")
      return 0
    else:
      return this.hvelo
   
  def checkCollisionV(this) -> int:
    newrect = this.rect.copy()
    newrect.y += this.vvelo
    blockTopRight = world.blockAt((newrect.right - 8)//BLOCK_SIZE, newrect.top//BLOCK_SIZE)
    blockTopLeft = world.blockAt(newrect.left//BLOCK_SIZE, newrect.top//BLOCK_SIZE)
    blockBotRight = world.blockAt((newrect.right- 8)//BLOCK_SIZE, (newrect.bottom+10)//BLOCK_SIZE)
    blockBotLeft = world.blockAt(newrect.left//BLOCK_SIZE, (newrect.bottom+10)//BLOCK_SIZE)
    # blockTopRight.drawBlockOutline((0,255,0))
    # blockTopLeft.drawBlockOutline((0,255,255))
    # pg.draw.rect(SURF, (0,0,0), relativeRect(newrect), 2)
    if this.vvelo < 0:
      # print("attepmting to move up!")
      if blockTopRight.collides(*newrect.topleft) or blockTopLeft.collides(*newrect.topleft):
        # print("top collides! not moving!")
        this.vvelo = 0
        return 0
      else:
        return this.vvelo
    elif this.vvelo > 0:
      if blockBotRight.collides(*newrect.topleft) or blockBotLeft.collides(*newrect.topleft):
        # print("bot collides! not moving!")
        this.isOnBlock = True
        return 0
      else:
        this.isOnBlock = False
        return this.vvelo
    else:
      return 0
  
  def move(this):
    if this.hvelo < 0: this.hvelo += min(1, abs(this.hvelo)) # reduce horizontal velocity constantly to 0
    elif this.hvelo > 0: this.hvelo -= min(1, this.hvelo)
    this.rect.x += this.checkCollisionH()
    this.rect.y += this.checkCollisionV()
    # 
    if this.vvelo < 5: this.vvelo += gravity
  
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

class Player(Entity, HasInventory):
  camera = FRAME.copy()
  camera.center = (BLOCK_SIZE * (WORLD_WIDTH // 2), BLOCK_SIZE * round(WORLD_HEIGHT * 0.55))
  texture = pg.transform.scale(pg.image.load("player.png"), (BLOCK_SIZE, BLOCK_SIZE*2))
  reversedTexture = pg.transform.flip(texture, True, False)
  
  def __init__(this):
    Entity.__init__(this, this.camera.centerx-BLOCK_SIZE//2, this.camera.centery-BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE*2, this.texture, 10,)
    HasInventory.__init__(this, 4, 10)
    this.rect.center = this.camera.center
    this.centerRect = this.rect.copy()
    this.centerRect.center = FRAME.center
    # print(this.inventory[0][0])
  
  def hotbar(this) -> list[Item]:
    return this.inventory[0]
  
  def move(this):
    super().move()
    this.camera.center = this.rect.center
  
  def mine(this, block):
    print("mined", block.name)
    world[block.y][block.x] = Air(block.x, block.y)
  

player = Player()

class Block(Item):
  SIZE = BLOCK_SIZE
  def __init__(this, name:str, itemTexture, blockTexture, stackSize:int, x, y, isAir=False):
    super().__init__(name, itemTexture, stackSize)
    this.blockTexture = blockTexture
    this.rect = pg.rect.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE, this.SIZE, this.SIZE)
    this.mask = pg.mask.from_surface(blockTexture)
    this.x = x
    this.y = y
    this.isAir = isAir
  
  def drawBlockOutline(this, color:pg.color.Color):
    pg.draw.rect(SURF, color, relativeRect(this.rect), 3)
  
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

  def __repr__(this):
    return this.name
  
class Air(Block):
  texture = pg.surface.Surface((BLOCK_SIZE,BLOCK_SIZE))
  texture.fill((0,0,0,0))
  def __init__(this, x=-1, y=-1):
    super().__init__("Air", this.texture, this.texture, 0, x, y, isAir = True)

class Dirt(Block):
  texture = pg.transform.scale(pg.image.load("dirt.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(this, x=-1, y=-1):
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
    for y in range(player.camera.top//BLOCK_SIZE, (player.camera.bottom//BLOCK_SIZE)+1):
      for x in range(player.camera.left//BLOCK_SIZE, (player.camera.right//BLOCK_SIZE) + 1):
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

player.inventory[0][0] = Dirt()
print(player.inventory[0][0].name)
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