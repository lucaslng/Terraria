import sys
import math
import random
import pickle
import time  # pickle stores game data onto local system
import pygame as pg
from pygame.locals import *
from abc import *
from dataclasses import dataclass
from typing import Callable
from enum import Enum
import pickle  # use pickle to store save
import time
import concurrent.futures



WIDTH = 1000
HEIGHT = 600
FPS = 60


BLOCK_SIZE = 20
WORLD_HEIGHT = 256
WORLD_WIDTH = 1000
SHADOW_QUALITY = 6
gravity = 1
SEED = time.time()
random.seed(SEED)

def pixelToCoord(x: float, y: float) -> tuple[int, int]:
  """Returns coordinate based on pixel location"""
  coord = int((x + player.camera.left) // BLOCK_SIZE), int(
      (y + player.camera.top) // BLOCK_SIZE
  )
  return coord


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
  return math.hypot(x1 - x2, y1 - y2)


def relativeRect(rect: pg.rect.Rect) -> pg.rect.Rect:
  """Returns on screen rect relative to the camera"""
  return pg.rect.Rect(
      rect.x - player.camera.x, rect.y - player.camera.y, rect.width, rect.height
  )


def relativeCoord(x: float, y: float) -> tuple[int, int]:
  '''Convert a pixel coordinate relative to the camera. Useful for drawing things and more.'''
  return x - player.camera.x, y - player.camera.y


def check_for_interaction() -> None:
  '''loops over every visible block to check for interactable blocks'''
  for y in range(player.camera.top // BLOCK_SIZE, (player.camera.bottom // BLOCK_SIZE) + 1):
    for x in range(player.camera.left // BLOCK_SIZE, (player.camera.right // BLOCK_SIZE) + 1):
      block = world.blockAt(x, y)
      if isinstance(block, Interactable):
        dist = distance(player.rect.centerx, player.rect.centery,
                        block.rect.centerx, block.rect.centery)
        if dist <= 3 * BLOCK_SIZE:
          block.interact()
          return


def bresenham(x0: int, y0: int, x1: int, y1: int, checkVertices=False, quality: int=1) -> tuple[int, int] | None:
  """Bresenham's algorithm to detect first non-air block along a line, starting from end point."""
  pointsTouched = set()
  def plotLineLow(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    xi = -quality if x0 < x1 else quality
    yi = -quality if y0 < y1 else quality
    xii = -1 if x0 < x1 else 1
    yii = -1 if y0 < y1 else 1
    d = (2 * dy) - dx
    y = y1
    x = x1
    while x != x0 - xi:
      # print(x, x0-x1)
      blockTouched = world.blockAt(*pixelToCoord(x, y))
      if not blockTouched.isAir:
        if checkVertices:
          pointsTouched.add((x, y))
          if len(pointsTouched) == 2:
            return pointsTouched
        else: return x, y
      if d > 0:
        y += yi
        d += 2 * (dy - dx)
      else:
        d += 2 * dy
      x += xi
      nextBlock = world.blockAt(*pixelToCoord(x, y))
      if not nextBlock.isAir:
        xi = xii
        yi = yii
    if checkVertices:
      return pointsTouched
    else: return None

  def plotLineHigh(x0: int, y0: int, x1: int, y1: int) -> tuple[int, int] | None:
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    xi = -quality if x0 < x1 else quality
    yi = -quality if y0 < y1 else quality
    xii = -1 if x0 < x1 else 1
    yii = -1 if y0 < y1 else 1
    d = (2 * dx) - dy
    x = x1
    y = y1
    while y != y0 - yi:
      blockTouched = world.blockAt(*pixelToCoord(x, y))
      if not blockTouched.isAir:
        if checkVertices:
          pointsTouched.add((x, y))
          if len(pointsTouched) == 2:
            return pointsTouched
        else: return x, y
      if d > 0:
        x += xi
        d += 2 * (dx - dy)
      else:
        d += 2 * dx
      y += yi
      nextBlock = world.blockAt(*pixelToCoord(x, y))
      if not nextBlock.isAir:
        xi = xii
        yi = yii
    if checkVertices:
      return pointsTouched
    else: return None

  if abs(y1 - y0) < abs(x1 - x0):
    return plotLineLow(x0, y0, x1, y1)
  else:
    return plotLineHigh(x0, y0, x1, y1)


class Interactable(ABC):
  '''Abstract class for something that can be interacted with (press e key when near)'''

  def interact(this):
    '''To be called when Interactable is interacted with.'''
    pass


@dataclass
class Item:
  """Base item class"""

  SIZE = 15
  name: str
  texture: pg.surface.Surface
  stackSize: int

  def slotTexture(this) -> pg.surface.Surface:
    return pg.transform.scale_by(this.texture, 0.8)

  def drawItem(this, x: int, y: int):
    SURF.blit(this.itemTexture, (x, y))

  def __eq__(this, other) -> bool:
    if other is None:
      return False
    return this.name == other.name

  def isPlaceable(this) -> bool:
    return isinstance(this, PlaceableItem)

  def isTool(this) -> bool:
    return isinstance(this, Tool)


class BlockType(Enum):
  '''Possible block types corresponding to the tool that they are mined with.'''
  NONE = -1
  PICKAXE = 0
  AXE = 1
  SHOVEL = 2
  SWORD = 3
  SHEARS = 4

@dataclass
class Block:
  '''Base block class'''
  SIZE = BLOCK_SIZE
  amountBroken = float(0)
  name: str
  texture: pg.surface.Surface
  x: int
  y: int
  hardness: float
  blockType: BlockType
  isAir: bool = False

  def __post_init__(this):
    this.rect = pg.rect.Rect(
      this.x * BLOCK_SIZE, this.y * BLOCK_SIZE, this.SIZE, this.SIZE)
    this.vertices = (
      this.rect.topleft,
      this.rect.topright,
      this.rect.bottomleft,
      this.rect.bottomright,
    )
    this.mask = pg.mask.from_surface(this.texture)

  def drawBlockOutline(this, color: pg.color.Color):
    pg.draw.rect(ASURF, color, relativeRect(this.rect), 2)

  def drawBlock(this):
    SURF.blit(this.texture, relativeRect(this.rect))
    breakingRect = relativeRect(this.rect.copy())
    breakingRect.scale_by_ip(
      this.amountBroken / this.hardness, this.amountBroken / this.hardness
    )
    pg.draw.rect(ASURF, (0, 0, 0, 100), breakingRect)

  def offset(this, x: int, y: int) -> tuple[int, int]:
    return x - this.rect.x, y - this.rect.y

  def collides(this, x: int, y: int) -> bool:
    if this.isAir:
      return False
    if this.mask.overlap(player.mask, this.offset(x, y)):
      # pg.draw.rect(SURF, (255, 0, 0), relativeRect(this.rect), width=3)
      return True
    else:
      return False
  
  def item(this):
    return BlockItemRegistry.getItem(type(this))

  def isInCamera(this) -> bool:
    return this.rect.colliderect(player.camera)

  def __repr__(this):
    return this.name

  def __hash__(this):
    return hash((this.x, this.y))

  def __eq__(this, other):
    return hash(this) == hash(other)


@dataclass
class PlaceableItem(Item):
  '''Items that have a corresponding block and can be placed.'''
  @classmethod
  def block(cls):
    return BlockItemRegistry.getBlock(cls)
  
  def place(this, x: int, y: int) -> None:
    world[y][x] = this.block()(x, y)


class AirBlock(Block):
  '''Empty air block'''
  texture = pg.surface.Surface((BLOCK_SIZE, BLOCK_SIZE))
  texture.fill((0, 0, 0, 0))
  def __init__(this, x=-1, y=-1):
    super().__init__("Air", this.texture, x, y, 0, BlockType.NONE, isAir=True)

class CraftingTableBlock(Block, Interactable):
  craftingTableTexture = pg.transform.scale(
    pg.image.load("crafting_table.png"), (BLOCK_SIZE, BLOCK_SIZE))
  
  def __init__(self, x, y):
    Block.__init__(self, name="Crafting Table", texture=self.craftingTableTexture,
                   x=x, y=y, hardness=2.5, blockType=BlockType.AXE)

  def interact(self):
    craftingMenu.isActive = not craftingMenu.isActive

class CraftingTableItem(PlaceableItem):
  craftingTableTexture = pg.transform.scale(pg.image.load("crafting_table.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Crafting Table", this.craftingTableTexture, 64)

class DirtVariant:
  def __init__(this, name: str, texture):
    this.name = name
    this.texture = texture
class DirtVariantDirt(DirtVariant):
  dirtTexture = pg.transform.scale(
    pg.image.load("dirt.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(this):
    super().__init__("Dirt", this.dirtTexture)
class DirtVariantGrass(DirtVariant):
  grassTexture = pg.transform.scale(
    pg.image.load("grass_block.png"), (BLOCK_SIZE, BLOCK_SIZE)
  )
  grassItemTexture = pg.transform.scale(grassTexture, (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Grass Block", this.grassTexture)
class DirtBlock(Block):
  def __init__(this, x, y, variant: DirtVariant = DirtVariantDirt()):
    super().__init__(variant.name, variant.texture, x, y, 1, BlockType.SHOVEL)
class DirtItem(PlaceableItem):
  dirtItemTexture = pg.transform.scale(pg.image.load("dirt.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Dirt", this.dirtItemTexture, 64)

class StoneBlock(Block):
  stoneTexture = pg.transform.scale(
    pg.image.load("stone.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(this, x, y):
    super().__init__("Stone", this.stoneTexture, x, y, 5, BlockType.PICKAXE)
class CobblestoneBlock(Block):
  cobblestoneTexture = pg.transform.scale(
    pg.image.load("cobblestone.png"), (BLOCK_SIZE, BLOCK_SIZE))
  cobblestoneItemTexture = pg.transform.scale(cobblestoneTexture, (Item.SIZE, Item.SIZE))
  def __init__(this, x, y):
    super().__init__("Cobblestone", this.cobblestoneTexture, x, y, 2, BlockType.PICKAXE)
class CobbleStoneItem(PlaceableItem):
  cobblestoneItemTexture = pg.transform.scale(
    pg.image.load("cobblestone.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Cobblestone", this.cobblestoneItemTexture, 64)


class Generated(ABC):
  '''Things that can be generated by simplex noise'''
  veinSize: int
  rarity: int
class IronOreBlock(Block, Generated):
  ironOreTexture = pg.transform.scale(
    pg.image.load("iron_ore.png"), (BLOCK_SIZE, BLOCK_SIZE))
  veinSize = 3.2
  rarity = 0.38
  def __init__(this, x, y):
    Block.__init__(this, "Iron Ore", this.ironOreTexture, x, y, 6, BlockType.PICKAXE)
class IronOreItem(PlaceableItem):
  ironOreItemTexture = pg.transform.scale(pg.image.load("iron_ore.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Iron Ore", this.ironOreItemTexture, 64)

class CoalOreBlock(Block, Generated):
  coalTexture = pg.transform.scale(pg.image.load("coal_ore.png"), (BLOCK_SIZE, BLOCK_SIZE))
  veinSize = 3.9
  rarity = 0.3
  def __init__(this, x, y):
    Block.__init__(this, "Coal Ore", this.coalTexture, x, y, 3, BlockType.PICKAXE)
class CoalItem(Item):
  coalItemTexture = pg.transform.scale(pg.image.load("coal.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Coal", this.coalItemTexture, 64)

ores = {CoalOreBlock, IronOreBlock}

class BlockItemRegistry:
  block2Item = {}
  item2Block = {}
  
  @classmethod
  def register(cls, blockCls, itemCls):
    cls.block2Item[blockCls] = itemCls
    cls.item2Block[itemCls] = blockCls

  @classmethod
  def getItem(cls, blockCls):
    return cls.block2Item.get(blockCls)

  @classmethod
  def getBlock(cls, itemCls):
    return cls.item2Block.get(itemCls)

BlockItemRegistry.register(CraftingTableBlock, CraftingTableItem)
BlockItemRegistry.register(DirtBlock, DirtItem)
BlockItemRegistry.register(StoneBlock, CobbleStoneItem)
BlockItemRegistry.register(CobblestoneBlock, CobbleStoneItem)
BlockItemRegistry.register(IronOreBlock, IronOreItem)
BlockItemRegistry.register(CoalOreBlock, CoalItem)

class Slot:
  """Slot class"""

  item: Item = None
  count: int = 0
  isActive = False
  size = 40

  def draw(this, x: float, y: float, size: float = size) -> None:
    pg.draw.rect(SURF, (200, 200, 200),
                 (x, y, size, size))
    if this.isActive:
      pg.draw.rect(SURF, (0, 0, 0),
                   (x, y, size, size), 2)
    else:
      pg.draw.rect(SURF, (90, 90, 90),
                   (x, y, size, size), 2)

    if this.item is not None:
      item_texture = this.item.texture
      scaled_texture = pg.transform.scale(
          item_texture, (size - 6, size - 6)
      )
      # center texture in the slot
      texture_rect = scaled_texture.get_rect(
          center=(x + size // 2, y + size // 2)
      )
      SURF.blit(scaled_texture, texture_rect.topleft)

      if this.count > 1:
        count_text = font20.render(
            str(this.count), True, (255, 255, 255))
        # item counter is in the bottom right of the slot
        text_rect = count_text.get_rect(
            bottomright=(x + size - 5,
                         y + size - 5)
        )
        SURF.blit(count_text, text_rect.topleft)

@dataclass
class Section:
  rows: int
  cols: int
  x: float
  y: float
  slotSize: int = 40
  def __post_init__(this):
    this.array = [[Slot() for _ in range(this.cols)] for _ in range(this.rows)]
  def __getitem__(this, i: int) -> list[Slot]:
    return this.array[i]
  def draw(this) -> None:
    for r in range(this.rows):
      for c in range(this.cols):
        this[r][c].draw(this.x+c*this.slotSize, this.y+r*this.slotSize, size = this.slotSize)
class Menu:
  '''A menu is effectively a list of Sections. One section is an array of Slots.'''
  def __init__(this, *args: Section, isActive: bool = False):
    this.isActive = isActive
    this.sections = [args[i] for i in range(len(args))]
  
  def draw(this) -> None:
    for section in this.sections:
      section.draw()

class CraftingMenu(Menu):
  def __init__(this):
    super().__init__(Section(3, 3, WIDTH*0.4, HEIGHT*0.3, 60), Section(1, 1, WIDTH*0.4+240, HEIGHT*0.3+60, 60))
  #   self.grid = [[None for _ in range(3)] for _ in range(3)]  # 3x3 grid

  #   self.grid_pos = (200, 100)
  #   self.slot_size = 50
  #   self.slot_padding = 5

  #   self.result_slot_pos = (self.grid_pos[0] + 4 * (
  #     self.slot_size + self.slot_padding), self.grid_pos[1] + self.slot_size + self.slot_padding)
  #   self.result_item = None

  # def draw(self):
  #   for row in range(3):
  #     for col in range(3):
  #       x = self.grid_pos[0] + col * (self.slot_size + self.slot_padding)
  #       y = self.grid_pos[1] + row * (self.slot_size + self.slot_padding)

  #       pg.draw.rect(SURF, (200, 200, 200),
  #                    (x, y, self.slot_size, self.slot_size))

  #       item = self.grid[row][col]
  #       if item:
  #         scaled_item = pg.transform.scale(
  #           item.texture, (self.slot_size, self.slot_size))
  #         SURF.blit(scaled_item, (x, y))

  #   pg.draw.rect(SURF, (150, 150, 150),
  #                (*self.result_slot_pos, self.slot_size, self.slot_size))

  #   if self.result_item:
  #     scaled_result = pg.transform.scale(
  #       self.result_item.texture, (self.slot_size, self.slot_size))
  #     SURF.blit(scaled_result, self.result_slot_pos)

  # def place_item(self, item, row, col):
  #   if 0 <= row < 3 and 0 <= col < 3:
  #     self.grid[row][col] = item
  #     self.check_crafting_recipe()

  # def check_crafting_recipe(self):
  #   # implement when i feel like it (when i get more chatgpt credits)
  #   pass

  # def craft(self):
  #   if self.result_item:
  #     player.inventory.add_item(self.result_item)

  #     self.grid = [[None for _ in range(3)] for _ in range(3)]
  #     self.result_item = None

@dataclass
class Inventory:
  """Inventory class"""
  rows: int
  cols: int
  
  def __post_init__(this):
    this.inventory = [[Slot() for _ in range(this.cols)]
                      for _ in range(this.rows)]

  def addItem(this, item: Item) -> None:
    for r in range(this.rows):
      for c in range(this.cols):
        slot = this.inventory[r][c]
        # if item exist increase by one
        if slot.item and slot.item == item:
          if slot.count < slot.item.stackSize:  # stack size limit
            slot.count += 1
            return
        # if slot empty add the item
        elif slot.item is None:
          slot.item = item
          slot.count = 1
          return

  def isPlaceable(this) -> bool:
    return isinstance(this, PlaceableItem)

  def __getitem__(this, row: int):
    return this.inventory[row]


@dataclass
class Tool(Item):
  speed: float
  blockType: BlockType


class WoodenPickaxe(Tool):
  woodenPickaxeTexture = pg.transform.scale(
    pg.image.load("wooden_pickaxe.png"), (Item.SIZE, Item.SIZE))

  def __init__(this):
    super().__init__("Wooden Pickaxe", this.woodenPickaxeTexture, 1, 1.5, BlockType.PICKAXE)


class HasInventory:
  """Parent class for classes than have an inventory"""

  def __init__(this, rows: int, cols: int):
    this.inventory = Inventory(rows=rows, cols=cols)


class Entity:
  """Base entity class. Contains methods for moving, drawing, and gravity"""

  hvelo = 0
  vvelo = 0
  gravityvelo = 0
  previousDirection = True
  isOnBlock = False
  animations = {}

  def __init__(
      this,
      x: float,
      y: float,
      width: float,
      height: float,
      texture: pg.surface.Surface,
      health: float,
      speed: float,
      jumpHeight: float,
  ):
    this.rect = pg.rect.Rect(x, y, width, height)
    this.texture = texture
    this.reversedTexture = pg.transform.flip(texture, True, False)
    this.mask = pg.mask.from_surface(texture)
    this.health = health
    this.speed = speed
    this.jumpHeight = jumpHeight

  def moveLeft(this) -> None:
    if this.hvelo > -5:
      this.hvelo -= this.speed

  def moveRight(this) -> None:
    if this.hvelo < 5:
      this.hvelo += this.speed

  def jump(this) -> None:
    if this.vvelo > 4 and this.isOnBlock:
      this.vvelo -= this.jumpHeight

  def checkCollisionH(this) -> int:
    newrect = this.rect.copy()
    newrect.x += this.hvelo - 1
    blockRightTop = world.blockAt(
      x = newrect.right // BLOCK_SIZE,
      y = (newrect.top + 10) // BLOCK_SIZE
    )
    blockRightBot = world.blockAt(
      x = newrect.right // BLOCK_SIZE, 
      y = (newrect.centery + 10) // BLOCK_SIZE
    )
    blockLeftBot = world.blockAt(
      x = newrect.left // BLOCK_SIZE,
      y = (newrect.centery + 10) // BLOCK_SIZE
    )
    blockLeftTop = world.blockAt(
      x = newrect.left // BLOCK_SIZE,
      y = (newrect.top + 10) // BLOCK_SIZE
    )
    # pg.draw.rect(SURF, (0,0,255),relativeRect(blockRightTop.rect),3)
    # pg.draw.rect(SURF, (255,0,255),relativeRect(blockRightBot.rect),3)
    # pg.draw.rect(SURF, (255,128,128),relativeRect(blockLeftBot.rect),3)
    # pg.draw.rect(SURF, (255,0,0),relativeRect(blockLeftTop.rect),3)
    if (
        blockRightBot.collides(*newrect.topleft)
        or blockRightTop.collides(*newrect.topleft)
        or blockLeftBot.collides(*newrect.topleft)
        or blockLeftTop.collides(*newrect.topleft)
    ):
      # print("side collides! not moving!")
      return 0
    else:
      return this.hvelo

  def checkCollisionV(this) -> int:
    newrect = this.rect.copy()
    newrect.y += this.vvelo
    blockTopRight = world.blockAt(
      x = (newrect.right - 8) // BLOCK_SIZE,
      y = newrect.top // BLOCK_SIZE
    )
    blockTopLeft = world.blockAt(
      x = newrect.left // BLOCK_SIZE,
      y = newrect.top // BLOCK_SIZE
    )
    blockBotRight = world.blockAt(
      x = (newrect.right - 8) // BLOCK_SIZE,
      y = (newrect.bottom + 10) // BLOCK_SIZE
    )
    blockBotLeft = world.blockAt(
      x = newrect.left // BLOCK_SIZE,
      y = (newrect.bottom + 10) // BLOCK_SIZE
    )
    # blockTopRight.drawBlockOutline((0,255,0))
    # blockTopLeft.drawBlockOutline((0,255,255))
    # pg.draw.rect(SURF, (0,0,0), relativeRect(newrect), 2)
    if this.vvelo < 0:
      # print("attepmting to move up!")
      if (
        blockTopRight.collides(*newrect.topleft)
        or blockTopLeft.collides(*newrect.topleft)
        ):
        # print("top collides! not moving!")
        this.vvelo = 0
        return 0
      else:
        return this.vvelo
    elif this.vvelo > 0:
      if (
        blockBotRight.collides(*newrect.topleft)
        or blockBotLeft.collides(*newrect.topleft)
      ):
        # print("bot collides! not moving!")
        this.isOnBlock = True
        return 0
      else:
        this.isOnBlock = False
        return this.vvelo
    else:
      return 0

  def move(this) -> None:
    if this.hvelo < 0:
      this.hvelo += min(1, abs(this.hvelo))  # reduce horizontal velocity constantly to 0
    elif this.hvelo > 0:
      this.hvelo -= min(1, this.hvelo)
    this.rect.x += this.checkCollisionH()
    this.rect.y += this.checkCollisionV()
    if this.vvelo < 5:
      this.vvelo += gravity

  def draw(this) -> None:
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
      SURF.blit(this.reversedTexture, relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.reversedTexture)

  def update(this) -> None:
    this.move()
    this.draw()


class Player(Entity, HasInventory):
  texture = pg.transform.scale(
      pg.image.load("player.png"), (BLOCK_SIZE, BLOCK_SIZE * 2)
  )
  reversedTexture = pg.transform.flip(texture, True, False)
  reach = 4 * BLOCK_SIZE
  full_heart_texture = pg.transform.scale(
      pg.image.load("full_heart.png"), (20, 20))
  half_heart_texture = pg.transform.scale(
      pg.image.load("half_heart.png"), (20, 20))
  empty_heart_texture = pg.transform.scale(
      pg.image.load("empty_heart.png"), (20, 20))
  blockFacing = None

  def __init__(this):
    this.camera = FRAME.copy()
    this.camera.center = (
      BLOCK_SIZE * (WORLD_WIDTH // 2),
      BLOCK_SIZE * round(WORLD_HEIGHT * 0.55),
    )
    Entity.__init__(
        this,
        this.camera.centerx - BLOCK_SIZE // 2,
        this.camera.centery - BLOCK_SIZE,
        BLOCK_SIZE,
        BLOCK_SIZE * 2,
        this.texture,
        10,
        2,
        18,
    )

    HasInventory.__init__(this, 4, 10)
    
    this.heldSlotIndex = 0  # number from 0 to 9
    this.rect.center = this.camera.center
    this.centerRect = this.rect.copy()
    this.centerRect.center = FRAME.center
    this.max_health = 20
    this.health = this.max_health

    this.falling = False
    this.fall_start_y = None
    this.fall_damage_threshold = 4 * BLOCK_SIZE
    this.is_initial_spawn = True
    this.spawn_protection_timer = 60

    this.usingItem = False
    this.placingBlock = False

    for item in defaultItems: this.inventory.addItem(item) 

    # beginning tick, tick length
    this.animations["usingItem"] = pg.time.get_ticks() + 200
    this.animations["placingBlock"] = 250

  def draw_health(this):
    """Draw health as hearts on the screen"""
    HEART_SPACING = 25
    HEART_X_START = 10
    HEART_Y = 10

    full_hearts = this.health // 2
    half_hearts = this.health % 2
    empty_hearts = (this.max_health - this.health) // 2

    # Full hearts
    for i in range(full_hearts):
      SURF.blit(
          this.full_heart_texture, (HEART_X_START +
                                    i * HEART_SPACING, HEART_Y)
      )
    # Draw half heart
    if half_hearts:
      SURF.blit(
          this.half_heart_texture,
          (HEART_X_START + full_hearts * HEART_SPACING, HEART_Y),
      )
    # Draw empty hearts
    for i in range(empty_hearts):
      SURF.blit(
          this.empty_heart_texture,
          (
              HEART_X_START +
              (full_hearts + half_hearts + i) * HEART_SPACING,
              HEART_Y,
          ),
      )

  def draw(this):
    super().draw()

  def hotbar(this) -> list[Slot]:
    '''Returns the first row of the player's inventory'''
    return this.inventory[0]

  def heldSlot(this) -> Slot:
    '''Returns the held slot, or None if the slot is empty'''
    slot = this.hotbar()[this.heldSlotIndex]
    if slot:
      return slot
    else:
      return None

  def changeSlot(this, index: int):
    this.heldSlot().isActive = False
    this.heldSlotIndex = index
    this.heldSlot().isActive = True

  def drawHeldItem(this):
    slot = this.heldSlot()
    if slot.item:
      texture = slot.item.slotTexture()
      if this.usingItem and pg.time.get_ticks() % 200 < 100:
        texture = pg.transform.rotozoom(texture, -35, 1)
      elif this.animations["placingBlock"] < 100:
        texture = pg.transform.rotozoom(
          texture, -this.animations["placingBlock"] / 3.8, 1)
        this.animations["placingBlock"] += 1000 / FPS
        this.placingBlock = False
      if this.previousDirection == False:
        texture = pg.transform.flip(texture, True, False)
      SURF.blit(texture, FRAME.center)

  def drawHotbar(this):
    """Draws the first row of the inventory on the screen"""
    HOTBAR_X = (WIDTH - (this.inventory.cols * Slot.size)) // 2
    HOTBAR_Y = HEIGHT - Slot.size - 10

    for col in range(this.inventory.cols):
      slot_x = HOTBAR_X + col * Slot.size
      slot_y = HOTBAR_Y
      slot = this.hotbar()[col]
      slot.draw(slot_x, slot_y)

  def move(this):
    if this.is_initial_spawn:
      this.falling = False
      this.fall_start_y = None

      this.spawn_protection_timer -= 1
      if this.spawn_protection_timer <= 0:
        this.is_initial_spawn = False

    if this.vvelo > 0:
      if not this.falling:
        this.falling = True
        this.fall_start_y = this.rect.bottom

    super().move()
    this.camera.center = this.rect.center

    if this.falling and this.isOnBlock and not this.is_initial_spawn:
      fall_distance = abs(this.fall_start_y - this.rect.bottom)

      if fall_distance > this.fall_damage_threshold:
        # damage based on fall distance
        damage = int(
          (fall_distance - this.fall_damage_threshold) / BLOCK_SIZE)
        this.health = max(0, this.health - damage)

      this.falling = False
      this.fall_start_y = None

  def mine(this):
    if this.blockFacing:
      if this.blockFacing.amountBroken < this.blockFacing.hardness:
        miningSpeed = 1
        if this.heldSlot().item and this.heldSlot().item.isTool() and this.heldSlot().item.blockType == this.blockFacing.blockType:
          miningSpeed = this.heldSlot().item.speed
        this.usingItem = True
        this.blockFacing.amountBroken += miningSpeed / FPS
      else:
        # print("mined", this.blockFacing.name,
        #       "got", this.blockFacing.item().name)

        world[this.blockFacing.y][this.blockFacing.x] = AirBlock(
            this.blockFacing.x, this.blockFacing.y
        )
        this.inventory.addItem(this.blockFacing.item()())

  def place(this):
    if this.heldSlot().item and this.heldSlot().count > 0 and this.heldSlot().item.isPlaceable():
      x, y = pixelToCoord(*pg.mouse.get_pos())
      if world.blockAt(x, y).isAir:
        this.animations["placingBlock"] = 0
        this.heldSlot().item.place(x, y)
        this.heldSlot().count -= 1
        if this.heldSlot().count == 0:
          this.heldSlot().item = None

  def drawCircle(this):
    pg.draw.circle(ASURF, (0, 0, 0, 120), FRAME.center, BLOCK_SIZE * 4)

  def getBlockFacing(this):
    """Returns the block that the player is facing, if it is in range"""
    blockPixel = bresenham(*pg.mouse.get_pos(), *FRAME.center)
    if blockPixel:
      block = world.blockAt(*pixelToCoord(*bresenham(*pg.mouse.get_pos(), *FRAME.center)))
      for vertex in block.vertices:
        if distance(*relativeCoord(*vertex), *FRAME.center) < this.reach:
          return block
    return None

  def drawBlockFacing(this):
    if this.blockFacing:
      this.blockFacing.drawBlockOutline((0, 0, 0, 200))

  # def sweep(this):
  # https://www.redblobgames.com/articles/visibility/
  # endpoints = []

  def update(this):
    super().update()
    this.blockFacing = this.getBlockFacing()
    this.drawBlockFacing()
    this.drawHotbar()
    this.drawHeldItem()
    this.draw_health()
    if not pg.mouse.get_pressed()[0]:
      this.usingItem = False


class Sun:
  size = BLOCK_SIZE * 5
  sunTexture = pg.transform.scale(pg.image.load("sun.png"), (size, size))
  # pg.transform.threshold(sunTexture, sunTexture, (0,0,0,255), (120,120,120,0), (0,0,0,0), 1, inverse_set=True)
  def __init__(this):
    this.pos = (FRAME.centerx, 0)
  def draw(this):
    ASURF.blit(this.sunTexture, (HEIGHT * 0.1, HEIGHT * 0.1, this.size, this.size))


class World:
  litVertices = list()
  vertices = set()
  def __init__(this):
    this.array = [
        [AirBlock(x, y) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    this.__generateWorld()

  class SimplexNoise:
    def __init__(this, scale: float, dimension: int, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT):
      if dimension == 1:
        this.noise = this.__noise1d(width, scale)
      elif dimension == 2:
        this.noise = this.__noise2d(width, height, scale)
      else:
        return None

    def __getitem__(this, x: int):
      return this.noise[x]

    @staticmethod
    def __fade(t):
      return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def __lerp(a, b, t):
      return a + t * (b - a)

    @staticmethod
    def __generatePermutation():
      random.seed(random.randint(0, sys.maxsize))
      p = list(range(256))
      random.shuffle(p)
      random.seed(SEED)
      return p + p  # Double for wraparound

    @staticmethod
    def __gradient1d(h):
      return 1 if h % 2 == 0 else -1

    @staticmethod
    def __gradient2d(h):
      """Compute 2D gradient direction based on hash value."""
      directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
      return directions[h % 4]

    def __noise1d(this, width, scale=1.0):
      perm = this.__generatePermutation()
      noise = []

      for i in range(width):
        x = i / scale
        x0 = math.floor(x)
        x1 = x0 + 1

        dx0 = x - x0
        dx1 = x - x1

        u = this.__fade(dx0)

        g0 = this.__gradient1d(perm[x0 % 256])
        g1 = this.__gradient1d(perm[x1 % 256])

        n0 = g0 * dx0
        n1 = g1 * dx1

        value = this.__lerp(n0, n1, u)
        noise.append(value)

      return noise

    def __noise2d(this, width, height, scale=1.0):
      perm = this.__generatePermutation()
      noise = []

      for y in range(height):
        row = []
        for x in range(width):
          sx = x / scale
          sy = y / scale

          x0 = math.floor(sx)
          y0 = math.floor(sy)

          x1 = x0 + 1
          y1 = y0 + 1

          dx0 = sx - x0
          dy0 = sy - y0
          dx1 = sx - x1
          dy1 = sy - y1

          u = this.__fade(dx0)
          v = this.__fade(dy0)

          g00 = this.__gradient2d(perm[(x0 + perm[y0 % 256]) % 256])
          g10 = this.__gradient2d(perm[(x1 + perm[y0 % 256]) % 256])
          g01 = this.__gradient2d(perm[(x0 + perm[y1 % 256]) % 256])
          g11 = this.__gradient2d(perm[(x1 + perm[y1 % 256]) % 256])

          n00 = g00[0] * dx0 + g00[1] * dy0
          n10 = g10[0] * dx1 + g10[1] * dy0
          n01 = g01[0] * dx0 + g01[1] * dy1
          n11 = g11[0] * dx1 + g11[1] * dy1

          nx0 = this.__lerp(n00, n10, u)
          nx1 = this.__lerp(n01, n11, u)

          value = this.__lerp(nx0, nx1, v)
          row.append(value)
        noise.append(row)

      return noise

  def __generateWorld(this):
    grassHeightNoise = this.SimplexNoise(19, 1)
    stoneHeightNoise = this.SimplexNoise(30, 1)
    oresNoise = {}
    cavesNoise = this.SimplexNoise(9, 2)
    for ore in ores:
      oresNoise[ore.__name__] = (this.SimplexNoise(ore.veinSize, 2), ore)
    for x in range(0, WORLD_WIDTH):
      grassHeight = round(WORLD_HEIGHT * 0.58 + 9 * grassHeightNoise[x])
      stoneHeight = round(grassHeight + 5 + 5 * stoneHeightNoise[x])

      # Stone pass
      for y in range(WORLD_HEIGHT - 1, stoneHeight, -1):
        this.array[y][x] = StoneBlock(x, y)

      # Ore pass
      for y in range(WORLD_HEIGHT - 1, stoneHeight, -1):
        for _, v in oresNoise.items():
          oreNoise, ore = v
          if oreNoise[y][x] > ore.rarity:
            this.array[y][x] = ore(x, y)

      # Dirt pass
      for y in range(stoneHeight, grassHeight, -1):
        this.array[y][x] = DirtBlock(x, y)

      # Grass Dirt pass
      this.array[grassHeight][x] = DirtBlock(
          x, grassHeight, DirtVariantGrass()
      )

      # cave pass
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, - 1):
        if cavesNoise[y][x] > 0.1:
          this.array[y][x] = AirBlock(x, y)

  def hoveredBlock(this) -> Block:
    mousepos = pg.mouse.get_pos()
    return this.blockAt(*pixelToCoord(*mousepos))

  def blockAt(this, x, y) -> Block:
    return this[y][x]

  def __getitem__(this, x: int):
    return this.array[x]
  
  def topBlock(this, x) -> Block:
    for i in range(0, WORLD_HEIGHT-1):
      if not this[i][x].isAir:
        return this[i][x]

  def draw(this):
    this.vertices.clear()
    for y in range(
        player.camera.top // BLOCK_SIZE, (player.camera.bottom //
                                          BLOCK_SIZE) + 1
    ):
      for x in range(
          player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1,
      ):
        block = this[y][x]
        if not block.isAir:
          if (y-1>=0 and this[y-1][x].isAir) or (x-1>=0 and this[y][x-1].isAir) or (x+1<WORLD_WIDTH and this[y][x+1].isAir): this.vertices.update(map(lambda a: relativeCoord(*a), block.vertices))
          block.drawBlock()
    
  def castRays(this):
    this.litVertices.clear()
    for x in range(0, WIDTH, 20):
      bottomBlock = this.blockAt(*pixelToCoord(x, HEIGHT-1))
      if bottomBlock.isAir:
        this.vertices.update((relativeCoord(*bottomBlock.rect.bottomleft), relativeCoord(*bottomBlock.rect.bottomright)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
      pool.map(this.__findPointsTouched, this.vertices)
    this.litVertices.extend((FRAME.topleft, FRAME.topright, relativeCoord(*this.topBlock(WORLD_WIDTH-1).rect.topleft), relativeCoord(*this.topBlock(0).rect.topright)))
    this.litVertices.sort(key=lambda a: math.atan2(sun.pos[1]-a[1], sun.pos[0]-a[0]))
    pg.draw.polygon(LIGHTSURF, (255,255,255,0), [sun.pos] + this.litVertices)
  
  def __findPointsTouched(this, vertex):
    this.litVertices.extend(bresenham(*vertex, *sun.pos, checkVertices=True, quality=SHADOW_QUALITY))
  
  def update(this):
    this.draw()
    this.castRays()

if __name__ == "__main__":
  start = time.time()
  pg.init()
  clock = pg.time.Clock()
  SURF = pg.display.set_mode((WIDTH, HEIGHT), vsync=1)
  pg.display.set_caption("Terraria")
  LIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  FRAME = SURF.get_rect()
  ASURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  ASURF.fill((0, 0, 0, 0))
  defaultItems = [WoodenPickaxe(), CraftingTableItem()]
  player = Player()
  craftingMenu = CraftingMenu()
  font = pg.font.Font(None, 15)
  font20 = pg.font.Font(None, 20)
  world = World()
  sun = Sun()
  end = time.time()
  print("Load time:", end-start, "seconds")
  while True:
    SURF.fill((255, 255, 255))
    ASURF.fill((0, 0, 0, 0))
    LIGHTSURF.fill((0, 0, 0, 200))
    keys = pg.key.get_pressed()
    
    sun.draw()
    world.update()
    player.update()
    # temporarily game over logic
    if player.health <= 0:
      print("The skbidi has died")
      pg.quit()
      sys.exit()

    if keys[pg.K_a]:
      player.moveLeft()
    if keys[pg.K_d]:
      player.moveRight()
    if keys[pg.K_SPACE]:
      player.jump()
    if keys[pg.K_1]:
      player.changeSlot(0)
    if keys[pg.K_2]:
      player.changeSlot(1)
    if keys[pg.K_3]:
      player.changeSlot(2)
    if keys[pg.K_4]:
      player.changeSlot(3)
    if keys[pg.K_5]:
      player.changeSlot(4)
    if keys[pg.K_6]:
      player.changeSlot(5)
    if keys[pg.K_7]:
      player.changeSlot(6)
    if keys[pg.K_8]:
      player.changeSlot(7)
    if keys[pg.K_9]:
      player.changeSlot(8)
    if keys[pg.K_0]:
      player.changeSlot(9)

    if pg.mouse.get_pressed()[0]:
      player.mine()
    if pg.mouse.get_pressed()[2]:
      player.place()

    for event in pg.event.get():
      if event.type == QUIT:
        pg.quit()
        sys.exit()
      elif event.type == KEYDOWN and event.key == pg.K_e:
        check_for_interaction()

    pg.draw.circle(SURF,(255,255,0),sun.pos,5)
    SURF.blit(ASURF, (0, 0))
    LIGHTSURF = pg.transform.smoothscale(LIGHTSURF, (WIDTH//20, HEIGHT//20))
    LIGHTSURF = pg.transform.smoothscale(LIGHTSURF, (WIDTH, HEIGHT))
    SURF.blit(LIGHTSURF, ((0,0)))
      
    if craftingMenu.isActive: craftingMenu.draw()

    pg.display.flip()
    print("fps: ", round(clock.get_fps(), 2))
    clock.tick(FPS)