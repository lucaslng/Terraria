import sys
import pygame as pg
from pygame.locals import *
import math
from math import radians, hypot
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
  '''Returns coordinate based on pixel location'''
  coord = (x + player.camera.left) // BLOCK_SIZE, (y + player.camera.top) // BLOCK_SIZE
  return coord

def relativeRect(rect:pg.rect.Rect):
  '''Returns on screen rect relative to the camera'''
  return pg.rect.Rect(rect.x - player.camera.x, rect.y - player.camera.y, rect.width, rect.height)

def distance(x1, y1, x2, y2):
  return hypot(x1-x2, y1-y2)

class Item:
  '''Base item class'''
  ITEM_SIZE = BLOCK_SIZE
  def __init__(this, name:str, itemTexture, stackSize:int):
    this.itemTexture = itemTexture
    this.stackSize = stackSize
    this.name = name
  def drawItem(this, x:int, y:int):
    SURF.blit(this.itemTexture, (x, y))
  def __eq__(this, other) -> bool:
    if other == None: return False
    return this.name == other.name

class Inventory:
  '''Inventory class'''
  class Slot:
    '''Inventory slot class'''
    item:Item = None
    count:int = 0
    def __repr__(this):
      return this.item.name + "x" + str(this.count)
    def __str__(this):
      return this.item.name+"x"+str(this.count)
  
  def __init__(this, rows:int, cols:int):
    this.rows = rows
    this.cols = cols
    this.inventory = [[this.Slot() for _ in range(cols)] for _ in range(rows)]
  
  def __repr__(this):
    out = ""
    for r in this.inventory:
      for slot in r:
        out += str(slot)
      out += "\n"
    print(out)
    return out

  def addItem(this, item: Item):
    for r in range(this.rows):
        for c in range(this.cols):
            slot = this.inventory[r][c]
            # If item already exists in slot, increment count
            if slot.item and slot.item == item:
                if slot.count < slot.item.stackSize:  # Check stack size limit
                    slot.count += 1
                    return
            # If slot is empty, add the item
            elif slot.item is None:
                slot.item = item
                slot.count = 1
                return
    print("Inventory full!")  # Handle full inventory
  
  def __getitem__(this, row:int):
    return this.inventory[row]
  
  def drawHotbar(this):
      """Draws the first row of the inventory on the screen"""
      SLOT_SIZE = 40  #size of each slot
      HOTBAR_X = (WIDTH - (this.cols * SLOT_SIZE)) // 2
      HOTBAR_Y = HEIGHT - SLOT_SIZE - 10
      FONT = pg.font.Font(None, 20)
      
      for col in range(this.cols):
          slot_x = HOTBAR_X + col * SLOT_SIZE
          slot_y = HOTBAR_Y
          
          #draws the slots
          pg.draw.rect(SURF, (200, 200, 200), (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE))
          pg.draw.rect(SURF, (0, 0, 0), (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE), 2)
          
          slot = this.inventory[0][col]
          if slot.item is not None:
            item_texture = slot.item.itemTexture
            scaled_texture = pg.transform.scale(item_texture, (SLOT_SIZE - 6, SLOT_SIZE - 6))
            #center texture in the slot
            texture_rect = scaled_texture.get_rect(center=(slot_x + SLOT_SIZE // 2, slot_y + SLOT_SIZE // 2))
            SURF.blit(scaled_texture, texture_rect.topleft)

            if slot.count > 0:
                count_text = FONT.render(str(slot.count), True, (255, 255, 255))
                #item counter is in the bottom right of the slot
                text_rect = count_text.get_rect(bottomright=(slot_x + SLOT_SIZE - 5, slot_y + SLOT_SIZE - 5))
                SURF.blit(count_text, text_rect.topleft)
           

class HasInventory:
  '''Parent class for classes than have an inventory'''
  def __init__(this, rows:int, cols:int):
    this.inventory = Inventory(rows, cols)

class Entity:
  '''Base entity class. Contains methods for moving, drawing, and gravity'''
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

vertices = []
class Player(Entity, HasInventory):
  camera = FRAME.copy()
  camera.center = (BLOCK_SIZE * (WORLD_WIDTH // 2), BLOCK_SIZE * round(WORLD_HEIGHT * 0.55))
  texture = pg.transform.scale(pg.image.load("player.png"), (BLOCK_SIZE, BLOCK_SIZE*2))
  reversedTexture = pg.transform.flip(texture, True, False)
  viewDistance = 4 * BLOCK_SIZE
  full_heart_texture = pg.transform.scale(pg.image.load("full_heart.png"), (20, 20))
  half_heart_texture = pg.transform.scale(pg.image.load("half_heart.png"), (20, 20))
  empty_heart_texture = pg.transform.scale(pg.image.load("empty_heart.png"), (20, 20))
  
  def __init__(this):
    Entity.__init__(this, this.camera.centerx-BLOCK_SIZE//2, this.camera.centery-BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE*2, this.texture, 10,)
    HasInventory.__init__(this, 4, 10)
    this.rect.center = this.camera.center
    this.centerRect = this.rect.copy()
    this.centerRect.center = FRAME.center
    this.max_health = 20
    this.health = this.max_health
    
  def draw_health(this):
        """Draw player's health as hearts on the screen"""
        HEART_SPACING = 25
        HEART_X_START = 10
        HEART_Y = 10

        full_hearts = this.health // 2
        half_hearts = this.health % 2
        empty_hearts = (this.max_health - this.health) // 2

        # Draw full hearts
        for i in range(full_hearts):
            SURF.blit(this.full_heart_texture, 
                      (HEART_X_START + i * HEART_SPACING, HEART_Y))
        
        # Draw half heart if needed
        if half_hearts:
            SURF.blit(this.half_heart_texture, (HEART_X_START + full_hearts * HEART_SPACING, HEART_Y))
        
        # Draw empty hearts
        for i in range(empty_hearts):
            SURF.blit(this.empty_heart_texture, 
                      (HEART_X_START + (full_hearts + half_hearts + i) * HEART_SPACING, HEART_Y))

  def take_damage(this, damage_amount):
        """Reduce player health when taking damage"""
        this.health = max(0, this.health - damage_amount)
        
        # Optional: Add game over logic if health reaches 0
        if this.health <= 0:
            print("Game Over!")
            # You could add game over logic here, like resetting the game or showing a game over screen

  def draw(this):
        # Existing draw method remains the same
        super().draw()
        
        # Add health drawing to the draw method
        this.draw_health()
  
  def hotbar(this) -> list[Item]:
    return this.inventory[0]
  
  def move(this):
    super().move()
    this.camera.center = this.rect.center
  
  def mine(this, block):
    if not block.isAir:
      print("mined", block.name)
      world[block.y][block.x] = Air(block.x, block.y)
      this.inventory.addItem(block)
  
  def drawCircle(this):
    pg.draw.circle(ASURF, (0,0,0,120),FRAME.center,BLOCK_SIZE*4)
    
  
  def sweep(this):
    # https://www.redblobgames.com/articles/visibility/
    endpoints = []
    
  
ASURF = pg.surface.Surface((WIDTH,HEIGHT),pg.SRCALPHA)
ASURF.fill((0,0,0,0))
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
    if this.isAir: return False
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
  itemTexture = pg.transform.scale(texture, (15, 15))
  def __init__(this, x=-1, y=-1):
    super().__init__("Dirt", this.itemTexture, this.texture, 64, x, y)

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
        block = this[y][x]
        if not block.isAir:
          blockRelativeRect = relativeRect(block.rect)
          if distance(*blockRelativeRect.topleft, *FRAME.center) <= player.viewDistance:
            vertices.append((blockRelativeRect.topleft,math.atan2(blockRelativeRect.top-FRAME.centery, blockRelativeRect.left-FRAME.centerx)))
          if distance(*blockRelativeRect.topright, *FRAME.center) <= player.viewDistance:
            vertices.append((blockRelativeRect.topright,math.atan2(blockRelativeRect.top-FRAME.centery,blockRelativeRect.right-FRAME.centerx)))
          if distance(*blockRelativeRect.bottomleft, *FRAME.center) <= player.viewDistance:
            vertices.append((blockRelativeRect.bottomleft,math.atan2(blockRelativeRect.bottom-FRAME.centery,blockRelativeRect.left-FRAME.centerx)))
          if distance(*blockRelativeRect.bottomright, *FRAME.center) <= player.viewDistance:
            vertices.append((blockRelativeRect.bottomright,math.atan2(blockRelativeRect.bottom-FRAME.centery,blockRelativeRect.right-FRAME.centerx)))
          block.drawBlock()
  
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


while True:
  SURF.fill((255, 255, 255))
  ASURF.fill((0,0,0,0))
  keys = pg.key.get_pressed()
  vertices.clear()
  world.draw()
  player.draw()
  player.move()
  player.inventory.drawHotbar()
  print(player.inventory.inventory[0][0].count)
  player.drawCircle()
  for vertice in vertices:
    pg.draw.circle(ASURF,(0,255,0,120),vertice[0],3)
    # if distance(*FRAME.center, *vertice[0]) <= 5:
    pg.draw.line(ASURF,(0,0,0,40),FRAME.center,vertice[0])
  SURF.blit(ASURF,(0,0))
  
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