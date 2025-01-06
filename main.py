import sys, math, random, time, copy, threading, queue, collections, pickle          #pickle stores game data onto system
import pygame as pg
from pygame.locals import *
from pygame.math import Vector2

#import code from other files
from constants import *
from sprites import *

from abc import *
from dataclasses import dataclass
from collections import deque
from typing import Dict, List, Set, Tuple
from enum import Enum

SEED = time.time()
random.seed(SEED)
start = time.time()

pg.init()
pg.font.init()
clock = pg.time.Clock()


class Direction:
  NORTH=0
  SOUTH=1
  WEST=2
  EAST=3

def pixelToCoord(x: float, y: float) -> tuple[int, int]:
  """Returns coordinate based on pixel location"""
  coord = int((x + player.camera.left) // BLOCK_SIZE), int(
      (y + player.camera.top) // BLOCK_SIZE
  )
  return coord

def relativeRect(rect: pg.rect.Rect) -> pg.rect.Rect:
  """Returns on screen rect relative to the camera"""
  return pg.rect.Rect(
      rect.x - player.camera.x, rect.y - player.camera.y, rect.width, rect.height
  )

def relativeCoord(x: float, y: float) -> tuple[int, int]:
  '''Convert a pixel coordinate relative to the camera. Useful for drawing things and more.'''
  return x - player.camera.x, y - player.camera.y

def coordWorld2Pixel(x: int, y: int) -> tuple[int, int]:
  '''convert world coordinates to pixel'''
  return x * BLOCK_SIZE, y * BLOCK_SIZE

def rectWorld2Pixel(rect: pg.rect.Rect) -> pg.rect.Rect:
  '''convert world rect to pixel rect'''
  return pg.rect.Rect(rect.left * BLOCK_SIZE, rect.top * BLOCK_SIZE, rect.width * BLOCK_SIZE, rect.height * BLOCK_SIZE)

def coordWorld2Relative(x: int, y: int) -> tuple[int, int]:
  '''convert world coordinates to pixel on screen'''
  return relativeCoord(*coordWorld2Pixel(x, y))

def rectWorld2Relative(rect: pg.rect.Rect) -> pg.rect.Rect:
  '''convert world rect to relative rect'''
  pixelRect = rectWorld2Pixel(rect)
  return relativeRect(pixelRect)

def check_for_interaction() -> None:
  '''loops over every visible block to check for interactable blocks'''
  for y in range(player.camera.top // BLOCK_SIZE, (player.camera.bottom // BLOCK_SIZE) + 1):
    for x in range(player.camera.left // BLOCK_SIZE, (player.camera.right // BLOCK_SIZE) + 1):
      block = world.blockAt(x, y)
      if isinstance(block, Interactable):
        dist = math.dist(player.rect.center, block.rect.center)
        if dist <= 3 * BLOCK_SIZE:
          block.interact()
          return

def bresenham(x0: int, y0: int, x1: int, y1: int, checkVertices=False, quality: int=1):
  """Bresenham's algorithm to detect first non-air block along a line, starting from end point."""
  pointsTouched = list()
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
          pointsTouched.append((x, y))
          if len(pointsTouched) == 2:
            return pointsTouched
        else: return x, y
      if d > 0:
        y += yi
        d += 2 * (dy - dx)
      else:
        d += 2 * dy
      x += xi
      if not 0 <= x < WIDTH or not 0 <= y < HEIGHT: return pointsTouched
      nextBlock = world.blockAt(*pixelToCoord(x, y))
      if not nextBlock.isAir:
        xi = xii
        yi = yii
    if checkVertices:
      pointsTouched.append((x, y))
      if len(pointsTouched) == 2:
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
          pointsTouched.append((x, y))
          # if len(pointsTouched) == 2:
          return pointsTouched
        else: return x, y
      if d > 0:
        x += xi
        d += 2 * (dx - dy)
      else:
        d += 2 * dx
      y += yi
      if not 0 <= x < WIDTH or not 0 <= y < HEIGHT: return pointsTouched
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
class Light:
  '''Base class for any object with light except the sun'''
  lightRadius: int
  x: float
  y: float
  relative: bool = True
  
  def __post_init__(this):
    # print("post init light")
    lights.append(this)
    
  def drawLight(this):
    '''draw light'''
    if this.relative:
      # print(this.x, this.y, this.x*20, this.y*20, coordWorld2Relative(this.x, this.y))
      pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), coordWorld2Relative(this.x,this.y), this.lightRadius)
    else:
      pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), (this.x,this.y), this.lightRadius)

lights: list[Light] = []

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
  
  def isExecutable(this) -> bool:
    return isinstance(this, Executable)


class BlockType(Enum):
  '''Possible block types corresponding to the tool that they are mined with.'''
  NONE = -1
  PICKAXE = 0
  AXE = 1
  SHOVEL = 2
  SWORD = 3
  SHEARS = 4
  FLINTANDSTEEL = 5

@dataclass
class Block:
  '''Base block class'''
  SIZE = BLOCK_SIZE
  BACK_TINT = pg.surface.Surface((BLOCK_SIZE, BLOCK_SIZE), pg.SRCALPHA)
  BACK_TINT.fill((0,0,0,70))
  amountBroken = float(0)
  name: str
  texture: pg.surface.Surface
  x: int
  y: int
  hardness: float
  blockType: BlockType
  isAir: bool = False
  isEmpty: bool = False
  isBack: bool = False

  def __post_init__(this):
    this.texture = this.texture.convert_alpha()
    this.rect = pg.rect.Rect(
      this.x * BLOCK_SIZE, this.y * BLOCK_SIZE, this.SIZE, this.SIZE)
    this.vertices = (
      this.rect.topleft,
      this.rect.topright,
      this.rect.bottomleft,
      this.rect.bottomright,
    )
    this.mask = pg.mask.from_surface(this.texture)
    if this.isAir: this.mask.clear()
    this.edgeExist = [False for _ in range(4)]
    this.edgeId = [0 for _ in range(4)]
    
    if this.isBack and not this.isAir:
      this.texture.blit(this.BACK_TINT, (0,0))

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
    if this.isEmpty:
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
  
  def exposedVertices(this) -> set[tuple[int, int]]:
    result = set()
    if this.x-1 >= 0 and world[this.y][this.x-1].isAir:
      result.update((this.rect.topleft, this.rect.bottomleft))
    if this.x+1 < WORLD_WIDTH and world[this.y][this.x+1].isAir:
      result.update((this.rect.topright, this.rect.bottomright))
    if this.y-1 >= 0 and world[this.y-1][this.x].isAir:
      result.update((this.rect.topleft, this.rect.topright))
    return result

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
    world.mask.draw(world[y][x].mask, world[y][x].rect.topleft)

@dataclass
class Executable(ABC):
  '''Items that have a special effect to be executed when held'''
  @abstractmethod
  def execute(this):
    '''execute whatever needs to be done'''
    pass
  
  @abstractmethod
  def unexecute(this):
    '''unexecute when item is swapped out'''
    pass

class AirBlock(Block):
  '''Empty air block'''
  texture = pg.surface.Surface((BLOCK_SIZE, BLOCK_SIZE))
  texture.fill((0, 0, 0, 0))
  def __init__(this, x=-1, y=-1, isBack=False):
    super().__init__("Air", this.texture, x, y, 0, BlockType.NONE, isAir=True, isEmpty=True, isBack=isBack)

class CraftingTableBlock(Block, Interactable):
  craftingTableTexture = pg.transform.scale(
    pg.image.load("crafting_table.png"), (BLOCK_SIZE, BLOCK_SIZE))
  
  def __init__(this, x, y, isBack=False):
    Block.__init__(this, name="Crafting Table", texture=this.craftingTableTexture,
                   x=x, y=y, hardness=2.5, blockType=BlockType.AXE, isBack=isBack)

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
  def __init__(this, x, y, variant: DirtVariant = DirtVariantDirt(), isBack=False):
    super().__init__(variant.name, variant.texture, x, y, 1.5, BlockType.SHOVEL, isBack=isBack)
    
    this.variant = variant.name.lower()
class DirtItem(PlaceableItem):
  dirtItemTexture = pg.transform.scale(pg.image.load("dirt.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Dirt", this.dirtItemTexture, 64)
    
class OakLogBlock(Block):
    oakLogTexture = pg.transform.scale(pg.image.load("oak_log.png"), (BLOCK_SIZE, BLOCK_SIZE))  
    def __init__(this, x, y, isBack=False):
        super().__init__("Oak Log", this.oakLogTexture, x, y, 2.5, BlockType.AXE, isBack=isBack)
class OakLogItem(PlaceableItem):
    oakLogItemTexture = pg.transform.scale(pg.image.load("oak_log.png"), (Item.SIZE, Item.SIZE))
    def __init__(this):
        super().__init__("Oak Log", this.oakLogItemTexture, 64)

class LeavesBlock(Block):
    leavesTexture = pg.transform.scale(pg.image.load("leaves.png"), (BLOCK_SIZE, BLOCK_SIZE))  
    def __init__(this, x, y, isBack=False):
        super().__init__("Leaves", this.leavesTexture, x, y, 1, BlockType.SHEARS, isBack=isBack)

class StoneBlock(Block):
  stoneTexture = pg.transform.scale(
    pg.image.load("stone.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(this, x, y, isBack=False):
    super().__init__("Stone", this.stoneTexture, x, y, 5, BlockType.PICKAXE, isBack=isBack)
class CobblestoneBlock(Block):
  cobblestoneTexture = pg.transform.scale(
    pg.image.load("cobblestone.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(this, x, y, isBack=False):
    super().__init__("Cobblestone", this.cobblestoneTexture, x, y, 5.5, BlockType.PICKAXE, isBack=isBack)
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
  ironOreTexture = sprites["ironOre"]
  veinSize = 3.2
  rarity = 0.38
  def __init__(this, x, y, isBack=False):
    Block.__init__(this, "Iron Ore", this.ironOreTexture, x, y, 6, BlockType.PICKAXE, isBack=isBack)
class IronOreItem(PlaceableItem):
  ironOreItemTexture = sprites["ironOre"]
  def __init__(this):
    super().__init__("Iron Ore", this.ironOreItemTexture, 64)

class CoalOreBlock(Block, Generated):
  coalTexture = sprites["coalOre"]
  veinSize = 3.9
  rarity = 0.3
  def __init__(this, x, y, isBack=False):
    Block.__init__(this, "Coal Ore", this.coalTexture, x, y, 3, BlockType.PICKAXE, isBack=isBack)
class CoalItem(Item):
  coalItemTexture = sprites["coalOre"]
  def __init__(this):
    super().__init__("Coal", this.coalItemTexture, 64)

ores = {CoalOreBlock, IronOreBlock}

class TorchBlock(Block, Light):
  torchTexture = pg.transform.scale(pg.image.load("torch.png").convert_alpha(), (BLOCK_SIZE,BLOCK_SIZE))
  def __init__(this, x, y, isBack=False):
    Block.__init__(this, "Torch", this.torchTexture, x, y, 1, BlockType.NONE, isEmpty=True, isBack=isBack)
    Light.__init__(this, 100, x, y)
    lights.append(this)
class TorchItem(PlaceableItem, Executable):
  torchItemTexture = pg.transform.scale(pg.image.load("torch.png").convert_alpha(), (Item.SIZE, Item.SIZE))
  def __init__(this):
    PlaceableItem.__init__(this, "Torch", this.torchItemTexture, 64)
  def execute(this):
    player.lightRadius = 100
  def unexecute(this):
    player.lightRadius = BLOCK_SIZE//2

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
BlockItemRegistry.register(OakLogBlock, OakLogItem)
BlockItemRegistry.register(IronOreBlock, IronOreItem)
BlockItemRegistry.register(CoalOreBlock, CoalItem)
BlockItemRegistry.register(TorchBlock, TorchItem)

class Slot:
  """Slot class"""
  item: Item = None
  count: int = 0
  isActive = False
  size = 40

  def draw(this, x: float, y: float, size: float = size, transparent=False) -> None:
    if not transparent:
      pg.draw.rect(SURF, (200, 200, 200), (x, y, size, size))
    else:
      pg.draw.rect(ASURF, (200, 200, 200, 160), (x, y, size, size))
      
    if this.isActive:
      pg.draw.rect(SURF, (0, 0, 0), (x, y, size, size), 2)
    else:
      pg.draw.rect(SURF, (90, 90, 90), (x, y, size, size), 2)

    if this.item is not None:
      item_texture = this.item.texture
      scaled_texture = pg.transform.scale(item_texture, (size - 6, size - 6))
      
      #center texture in the slot
      texture_rect = scaled_texture.get_rect()
      texture_rect.center = (x + size / 2, y + size / 2)
      SURF.blit(scaled_texture, texture_rect.topleft)

      if this.count > 1:
        count_text = font20.render(str(this.count), True, (255, 255, 255))
        
        #item counter in the bottom right of the slot
        text_rect = count_text.get_rect(bottomright= (x + size - 5, y + size - 5))
        SURF.blit(count_text, text_rect.topleft)
        
      #Draw durability bar
      if this.item.isTool() and this.item.durability != this.item.startingDurability:
        bar_height = 3
        bar_width = size - 4
        bar_x = x + 2
        bar_y = y + size - bar_height - 1
        
        tool: Tool = this.item
        durability_percentage = tool.durability / tool.startingDurability
        
        if durability_percentage > 0.6:
          colour = (0, 255, 0)
        elif durability_percentage > 0.3:
          colour = (255, 165, 0)
        else:
          colour = (255, 0, 0)
        
        pg.draw.rect(SURF, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pg.draw.rect(SURF, colour, (bar_x, bar_y, int(bar_width * durability_percentage), bar_height))

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
  
  def draw(this, transparent=False) -> None:
    for r in range(this.rows):
      for c in range(this.cols):
        this[r][c].draw(this.x+c*this.slotSize, this.y+r*this.slotSize, size = this.slotSize, transparent=transparent)
        
class Menu:
  '''A menu is effectively a list of Sections. One section is an array of Slots.'''
  def __init__(this, *args: Section, isActive: bool = False):
    this.isActive = isActive
    this.sections = [args[i] for i in range(len(args))]
  
  def draw(this, transparent=False) -> None:
    for section in this.sections:
      section.draw(transparent)


@dataclass
class Inventory:
  """Inventory class"""
  rows: int
  cols: int
  menux: int
  menuy: int
  
  def __post_init__(this):
    this.inventory = [[Slot() for _ in range(this.cols)]
                      for _ in range(this.rows)]
    this.menu = Menu(Section(this.rows, this.cols, this.menux, this.menuy))

  def addItem(this, item: Item) -> bool:
    """Attempts to add an item to the inventory"""
    #add item to stack with existing items
    for r in range(this.rows):
        for c in range(this.cols):
            slot = this.inventory[r][c]
            if slot.item and slot.item == item and slot.count < slot.item.stackSize:
                slot.count += 1
                this.menu.draw()
                return True
                
    #find first empty slot if there isn't an existing slot
    for r in range(this.rows):
        for c in range(this.cols):
            slot = this.inventory[r][c]
            if slot.item is None:
                slot.item = item
                slot.count = 1
                #print('added to inventory')
                this.menu.draw()
                return True
                
    return False  #inventory full

  def isPlaceable(this) -> bool:
    return isinstance(this, PlaceableItem)

  def __getitem__(this, row: int):
    return this.inventory[row]


@dataclass
class Tool(Item):
  speed: float
  startingDurability: int
  blockType: BlockType
  
  def __post_init__(this):
    this.durability = this.startingDurability

class Shears(Tool):
  shearsTexture = pg.transform.scale(
    pg.image.load("shears.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Shears", this.shearsTexture, 1, 1.5, 238, BlockType.SHEARS)
    
'''Wooden'''
class WoodenPickaxe(Tool):
  def __init__(this):
    super().__init__("Wooden Pickaxe", sprites["woodenPickaxe"], 1, 1.5, 59, BlockType.PICKAXE)  
class WoodenAxe(Tool):
  def __init__(this):
    super().__init__("Wooden Axe", sprites["woodenAxe"], 1, 1.5, 59, BlockType.AXE)
class WoodenShovel(Tool):
  def __init__(this):
    super().__init__("Wooden Shovel", sprites["woodenShovel"], 1, 1.5, 59, BlockType.SHOVEL)
class WoodenSword(Tool):
  def __init__(this):
    super().__init__("Wooden Sword", sprites["woodenSword"], 1, 1, 59, BlockType.SWORD)
    
'''Stone'''
class StonePickaxe(Tool):
  def __init__(this):
    super().__init__("Stone Pickaxe", sprites["stonePickaxe"], 1, 3, 131, BlockType.PICKAXE)
class StoneAxe(Tool):
  def __init__(this):
    super().__init__("Stone Axe", sprites["stoneAxe"], 1, 2.5, 131, BlockType.AXE)
class StoneShovel(Tool):
  def __init__(this):
    super().__init__("Stone Shovel", sprites["stoneShovel"], 1, 2.5, 131, BlockType.SHOVEL)
class StoneSword(Tool):
  def __init__(this):
    super().__init__("Stone Sword", sprites["stoneSword"], 1, 1, 131, BlockType.SWORD)
    
'''Iron'''
class IronPickaxe(Tool):
  def __init__(this):
    super().__init__("Iron Pickaxe", sprites["ironPickaxe"], 1, 5, 250, BlockType.PICKAXE)
class IronAxe(Tool):
  def __init__(this):
    super().__init__("Iron Axe", sprites["ironAxe"], 1, 3.5, 250, BlockType.AXE)
class IronShovel(Tool):
  def __init__(this):
    super().__init__("Iron Shovel", sprites["ironShovel"], 1, 3.5, 250, BlockType.SHOVEL)
    
'''Diamond'''
class DiamondPickaxe(Tool):
  pass
  

class HasInventory:
  """Parent class for classes than have an inventory"""

  def __init__(this, rows: int, cols: int, menux: int, menuy: int):
    this.inventory = Inventory(rows=rows, cols=cols, menux=menux, menuy=menuy)


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
    this.reversedTexture = pg.transform.flip(texture, True, False).convert_alpha()
    this.mask = pg.mask.from_surface(texture)
    this.health = health
    this.speed = speed
    this.jumpHeight = jumpHeight
    
    # kinematic vectors
    this.position = Vector2(x, y)
    this.velocity = Vector2()
    this.accel = Vector2()
    
    # kinematic constants
    this.HORIZONTAL_ACCEL = 1
    this.HORIZONTAL_FRICTION = 0.2

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


class Player(Entity, HasInventory, Light):
  texture = sprites["cat"]["walk"][0]
  thisSprites = sprites["cat"]
  blockFacing = None
  reach = 4 * BLOCK_SIZE
  
  full_heart_texture = pg.transform.scale(pg.image.load("full_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))
  half_heart_texture = pg.transform.scale(pg.image.load("half_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))
  empty_heart_texture = pg.transform.scale(pg.image.load("empty_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))

  def __init__(this):
    Light.__init__(this, BLOCK_SIZE//2, *FRAME.center, relative=False)
    this.camera = FRAME.copy()
    this.camera.center = (
      BLOCK_SIZE * (WORLD_WIDTH // 2),
      BLOCK_SIZE * round(WORLD_HEIGHT * 0.55),
    )
    
    Entity.__init__(
        this,
        this.camera.centerx - BLOCK_SIZE // 2,
        this.camera.centery - BLOCK_SIZE // 2,
        BLOCK_SIZE,
        BLOCK_SIZE,
        this.texture,
        10,
        2,
        18,
    )
    this.mask = pg.mask.Mask((20, 20), True)

    HasInventory.__init__(this, 4, 10, 15, 80)
    
    this.heldSlotIndex = 0  # number from 0 to 9
    this.rect.center = this.camera.center
    this.centerRect = this.rect.copy()
    this.centerRect.center = FRAME.center
    this.max_health = 20
    this.health = this.max_health

    this.falling = False
    this.fall_start_y = None
    this.fall_damage_threshold = 10 * BLOCK_SIZE
    this.is_initial_spawn = True
    this.spawn_protection_timer = 120

    this.usingItem = False
    this.placingBlock = False

    #Add items at the beginning of the game to the player
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

    #Full hearts
    for i in range(full_hearts):
      SURF.blit(this.full_heart_texture, (HEART_X_START + i * HEART_SPACING, HEART_Y))   
    #Half hearts
    if half_hearts:
      SURF.blit(this.half_heart_texture,(HEART_X_START + full_hearts * HEART_SPACING, HEART_Y))     
    #Empty hearts
    for i in range(empty_hearts):
      SURF.blit(this.empty_heart_texture,(HEART_X_START +(full_hearts + half_hearts + i) * HEART_SPACING,HEART_Y))

  def draw(this):
    # print(this.vvelo)
    if this.hvelo < 0:
      if this.vvelo < -4:
        this.thisSprites["jump"].drawFrame(*relativeRect(this.rect).topleft, 2, flipped=True)
      else:
        this.thisSprites["walk"].drawAnimated(*relativeRect(this.rect).topleft, flipped=True)
      this.previousDirection = 0
    elif this.hvelo > 0:
      if this.vvelo < -4:
        this.thisSprites["jump"].drawFrame(*relativeRect(this.rect).topleft, 2)
      else:
        this.thisSprites["walk"].drawAnimated(*relativeRect(this.rect).topleft)
      this.previousDirection = 1
    elif this.previousDirection:
      this.thisSprites["sit"].drawAnimated(*relativeRect(this.rect).topleft)
    else:
      this.thisSprites["sit"].drawAnimated(*relativeRect(this.rect).topleft, flipped=True)

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

  def executeHeldSlotEffect(this):
    '''do whatever the heldslot says needs to be done'''
    if this.heldSlot().item and this.heldSlot().item.isExecutable():
      this.heldSlot().item.execute()
  
  def changeSlot(this, index: int):
    this.heldSlot().isActive = False
    if this.heldSlot().item and this.heldSlot().item.isExecutable():
      this.heldSlot().item.unexecute()
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
      
  def drawInventory(this) -> None:
    """Draw the inventory in the top left corner"""
    for r in range(this.inventory.rows):
      for c in range(this.inventory.cols):
          slot = this.inventory.inventory[r][c]

          slot_x = this.inventory.menux + (c * Slot.size)
          slot_y = this.inventory.menuy + (r * Slot.size)
          slot.draw(slot_x, slot_y, Slot.size, True)

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
        
        if this.heldSlot().item and this.heldSlot().item.isTool():
          #Checks if durability is 0
          if this.heldSlot().item.blockType == this.blockFacing.blockType:
            miningSpeed = this.heldSlot().item.speed
          if this.heldSlot().item.durability == 0:
            this.heldSlot().item = None
            this.heldSlot().count = 0
            
        this.usingItem = True
        this.blockFacing.amountBroken += miningSpeed / FPS
      else:
        # print("mined", this.blockFacing.name,
        #       "got", this.blockFacing.item().name)
        world.mask.erase(world[this.blockFacing.y][this.blockFacing.x].mask, this.blockFacing.rect.topleft)
        world[this.blockFacing.y][this.blockFacing.x] = AirBlock(
            this.blockFacing.x, this.blockFacing.y
        )
        if world.back[this.blockFacing.y][this.blockFacing.x].isAir: world.regenerateLight(this.blockFacing.x, this.blockFacing.y)
        item = this.blockFacing.item()
        
        if this.heldSlot().item and this.heldSlot().item.isTool():
          if this.heldSlot().item.blockType == this.blockFacing.blockType:
            miningSpeed = this.heldSlot().item.speed
            
          this.heldSlot().item.durability -= 1
        
        if item:
          this.inventory.addItem(item())

  def place(this):
    if this.heldSlot().item and this.heldSlot().count > 0 and this.heldSlot().item.isPlaceable():
      x, y = pixelToCoord(*pg.mouse.get_pos())
      if world.blockAt(x, y).isAir:
        this.animations["placingBlock"] = 0
        this.heldSlot().item.place(x, y)
        this.heldSlot().count -= 1
        if this.heldSlot().count == 0:
          this.heldSlot().item = None
        if world.back[y][x].isAir: world.regenerateLight(x, y)

  def drawCircle(this):
    pg.draw.circle(ASURF, (0, 0, 0, 120), FRAME.center, BLOCK_SIZE * 4)

  def getBlockFacing(this):
    """Returns the block that the player is facing, if it is in range"""
    blockPixel = bresenham(*pg.mouse.get_pos(), *FRAME.center)
    if blockPixel:
      block = world.blockAt(*pixelToCoord(*bresenham(*pg.mouse.get_pos(), *FRAME.center)))
      for vertex in block.vertices:
        if math.dist(relativeCoord(*vertex), FRAME.center) < this.reach:
          return block
    return None

  def drawBlockFacing(this):
    if this.blockFacing:
      this.blockFacing.drawBlockOutline((0, 0, 0, 200))

  def update(this):
    super().update()
    
    this.blockFacing = this.getBlockFacing()
    this.drawBlockFacing()
    this.drawHeldItem()
    this.drawHUD()
    if not pg.mouse.get_pressed()[0]:
      this.usingItem = False
    this.executeHeldSlotEffect()
  
  def drawHUD(this):
    this.draw_health()
    this.drawHotbar()
    this.drawInventory()

class Sun:
  size = BLOCK_SIZE * 5
  sunTexture = pg.transform.scale(pg.image.load("sun.png"), (size, size))
  # pg.transform.threshold(sunTexture, sunTexture, (0,0,0,255), (120,120,120,0), (0,0,0,0), 1, inverse_set=True)
  def __init__(this):
    this.pos = (FRAME.centerx, 0)
  def draw(this):
    ASURF.blit(this.sunTexture, (HEIGHT * 0.1, HEIGHT * 0.1, this.size, this.size))

@dataclass
class Edge:
  x: int
  y: int
  ex: int
  ey: int
  
  def draw(this):
    # if this.x != this.ex and this.y != this.ey: print("diagonal wtf")
    pg.draw.line(SURF,(0,0,0),relativeCoord(this.x*BLOCK_SIZE, this.y*BLOCK_SIZE),relativeCoord(this.ex*BLOCK_SIZE, this.ey*BLOCK_SIZE), 3)
    # pg.draw.circle(SURF,(0,255,0),relativeCoord(this.x*BLOCK_SIZE,this.y*BLOCK_SIZE), 3)
    # pg.draw.circle(SURF,(0,255,0),relativeCoord(this.ex*BLOCK_SIZE,this.ey*BLOCK_SIZE), 3)
  def __repr__(this):
    return str((this.x, this.y, this.ex, this.ey))

class World:
  litVertices = list()
  vertices = set()
  edgePool: List[Edge] = list()
  def __init__(this):
    this.array = [
        [AirBlock(x, y) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    # cannot deepcopy pygame surface so I have to loop over it again
    this.back = [
        [AirBlock(x, y, isBack=True) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    
    this.mask = pg.mask.Mask((WORLD_WIDTH*BLOCK_SIZE, WORLD_HEIGHT*BLOCK_SIZE))
    this.generateWorld()
    this.generateMask()
    this.generateLight()

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

        value = pg.math.lerp(n0, n1, u)
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

          nx0 = pg.math.lerp(n00, n10, u)
          nx1 = pg.math.lerp(n01, n11, u)

          value = pg.math.lerp(nx0, nx1, v)
          row.append(value)
        noise.append(row)

      return noise

  def generateWorld(this):
    # Precompute noise
    grassHeightNoise = this.SimplexNoise(19, 1)
    stoneHeightNoise = this.SimplexNoise(30, 1)
    cavesNoise = this.SimplexNoise(9, 2)

    oresNoise = {
      ore.__name__: (this.SimplexNoise(ore.veinSize, 2), ore)
      for ore in ores
    }

    # Generate terrain in batch
    for x in range(WORLD_WIDTH):
      grassHeight = round(WORLD_HEIGHT * 0.58 + 9 * grassHeightNoise[x])
      stoneHeight = round(grassHeight + 5 + 5 * stoneHeightNoise[x])

      # Stone and Dirt pass in batch
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, -1):
          if y > stoneHeight:
              this.array[y][x] = StoneBlock(x, y)
              this.back[y][x] = StoneBlock(x, y, isBack=True)
          else:
              this.array[y][x] = DirtBlock(x, y)
              this.back[y][x] = DirtBlock(x, y, isBack=True)

      # Grass block
      this[grassHeight][x] = DirtBlock(
          x, grassHeight, DirtVariantGrass()
      )

      # Cave pass
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, -1):
          if cavesNoise[y][x] > 0.1:
              this.array[y][x] = AirBlock(x, y)

      # Ore pass
      for ore_name, (oreNoise, ore) in oresNoise.items():
          for y in range(WORLD_HEIGHT - 1, stoneHeight, -1):
              if oreNoise[y][x] > ore.rarity and not this[y][x].isAir:
                  this.array[y][x] = ore(x, y)
      
      # Tree pass
      if isinstance(this[grassHeight][x], DirtBlock) and this[grassHeight][x].variant == "grass block":
          if random.random() > 0.8:  # Simplified tree placement
              this.__generateTree(x, grassHeight - 1)

  def generateMask(this):
    for row in this.array:
      for block in row:
        this.mask.draw(block.mask, block.rect.topleft)
        
  def __generateTree(this, x, y):
    if x < 3: return
    if x > WORLD_WIDTH - 3: return
    height = random.randint(3, 7)
    for r in range(y-height-1, y+1):
      for c in range(x-2, x+3):
        if not this[r][c].isAir: return
    for i in range(height):
      this[y-i][x] = OakLogBlock(x, y-i)
    this[y-height][x-2] = LeavesBlock(x-2, y-height)
    this[y-height][x-1] = LeavesBlock(x-1, y-height)
    this[y-height][x] = LeavesBlock(x, y-height)
    this[y-height][x+1] = LeavesBlock(x+1, y-height)
    this[y-height][x+2] = LeavesBlock(x+2, y-height)
    this[y-height-1][x-1] = LeavesBlock(x-1, y-height-1)
    this[y-height-1][x] = LeavesBlock(x, y-height-1)
    this[y-height-1][x+1] = LeavesBlock(x+1, y-height-1)
    this[y+1][x] = DirtBlock(x, y+1)
    
  
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
  
  def getVisibleBlocks(this):
    this.visibleBlocks = [
      [(this[y][x], this.back[y][x], this.lightmap[y][x]) for x in range(player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1)]
            for y in range(player.camera.top // BLOCK_SIZE,
              (player.camera.bottom // BLOCK_SIZE) + 1)
    ]

  def draw(this):
    for row in this.visibleBlocks:
      for blockTuple in row:
        block, backBlock, light = blockTuple
        if not backBlock.isAir and block.isEmpty:
          backBlock.drawBlock()
        if not block.isAir:
          block.drawBlock()
        pg.draw.rect(SUNLIGHTSURF, (0,0,0,light), relativeRect(block.rect))
  
  def buildEdgePool(this):
    this.edgePool.clear()
    this.vertices.clear()
    # frame is 30 x 50 blocks
    for y in range(
        player.camera.top // BLOCK_SIZE,
        (player.camera.bottom // BLOCK_SIZE) + 1
    ):
      for x in range(
          player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1,
      ):
        for j in range(4):
          this[y][x].edgeExist[j] = False
    
    for y in range(
        player.camera.top // BLOCK_SIZE,
        (player.camera.bottom // BLOCK_SIZE) + 1
    ):
      for x in range(
          player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1,
      ):
        cur = this[y][x]
        if not cur.isAir:
          # west
          if x-1 >= 0 and this[y][x-1].isAir:
            if y-1 >= 0 and this[y-1][x].edgeExist[Direction.WEST] and this[y-1][x].edgeId[Direction.WEST]<len(this.edgePool):
              # print("edge exists")
              this.edgePool[this[y-1][x].edgeId[Direction.WEST]].ey += 1
              # print(this.edgePool[this[y-1][x].edgeId[Direction.WEST]])
              cur.edgeId[Direction.WEST] = this[y-1][x].edgeId[Direction.WEST]
              cur.edgeExist[Direction.WEST] = True
            else:
              edge = Edge(x, y, x, y+1)
              edgeId = len(this.edgePool)
              cur.edgeId[Direction.WEST] = edgeId
              this.edgePool.append(edge)
              cur.edgeExist[Direction.WEST] = True
          # east
          if x+1 < (player.camera.right // BLOCK_SIZE) + 1 and this[y][x+1].isAir and this[y-1][x].edgeId[Direction.EAST]<len(this.edgePool):
            if y-1 >= 0 and this[y-1][x].edgeExist[Direction.EAST]:
              this.edgePool[this[y-1][x].edgeId[Direction.EAST]].ey += 1
              cur.edgeId[Direction.EAST] = this[y-1][x].edgeId[Direction.EAST]
              cur.edgeExist[Direction.EAST] = True
            else:
              edge = Edge(x+1, y, x+1, y+1)
              edgeId = len(this.edgePool)
              cur.edgeId[Direction.EAST] = edgeId
              this.edgePool.append(edge)
              cur.edgeExist[Direction.EAST] = True
          # north
          if y-1 >= 0 and this[y-1][x].isAir:
            if x-1 >= 0 and this[y][x-1].edgeExist[Direction.NORTH] and this[y][x-1].edgeId[Direction.NORTH]<len(this.edgePool):
              this.edgePool[this[y][x-1].edgeId[Direction.NORTH]].ex += 1
              cur.edgeId[Direction.NORTH] = this[y][x-1].edgeId[Direction.NORTH]
              cur.edgeExist[Direction.NORTH] = True
            else:
              edge = Edge(x, y, x+1, y)
              edgeId = len(this.edgePool)
              cur.edgeId[Direction.NORTH] = edgeId
              this.edgePool.append(edge)
              cur.edgeExist[Direction.NORTH] = True
          # south
          if y+1 < player.camera.bottom // BLOCK_SIZE + 1 and this[y+1][x].isAir and this[y][x-1].edgeId[Direction.SOUTH]<len(this.edgePool):
            if x-1 >= 0 and this[y][x-1].edgeExist[Direction.SOUTH]:
              this.edgePool[this[y][x-1].edgeId[Direction.SOUTH]].ex += 1
              cur.edgeId[Direction.SOUTH] = this[y][x-1].edgeId[Direction.SOUTH]
              cur.edgeExist[Direction.SOUTH] = True
            else:
              edge = Edge(x, y+1, x+1, y+1)
              edgeId = len(this.edgePool)
              cur.edgeId[Direction.SOUTH] = edgeId
              this.edgePool.append(edge)
              cur.edgeExist[Direction.SOUTH] = True
    for i in range(len(this.edgePool)):
      this.vertices.add(relativeCoord(this.edgePool[i].x*BLOCK_SIZE,this.edgePool[i].y*BLOCK_SIZE))
      this.vertices.add(relativeCoord(this.edgePool[i].ex*BLOCK_SIZE,this.edgePool[i].ey*BLOCK_SIZE))
      this.edgePool[i].draw()

  def generateLight(this):
    lightmap = [
      [255 if not this[y][x].isEmpty or not this.back[y][x].isEmpty else 0 for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)]
    
    lightstarttime = time.time()
    for i in range(5):
      newlightmap = copy.deepcopy(lightmap)
      for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
          if this[y][x].isEmpty and this.back[y][x].isEmpty: continue
          for r in range(-1, 2):
            if not 0 <= y + r < WORLD_HEIGHT: continue
            for c in range(-1, 2):
              if not 0 <= x + c < WORLD_WIDTH: continue
              if r == 0 and c == 0: continue
              lightmap[y][x] = min(lightmap[y][x], newlightmap[y+r][x+c] + i * 50)
              
    lightendtime = time.time()
    print("lightmap time:", round(lightendtime - lightstarttime, 2))
    this.lightmap = lightmap
  
  def regenerateLight(this, xcenter: int, ycenter: int):
    radius = 5
    count = 0
    for y in range(ycenter - radius, ycenter + radius + 1):
        for x in range(xcenter - radius, xcenter + radius + 1):
          this.lightmap[y][x] = 255 if not this[y][x].isEmpty or not this.back[y][x].isEmpty else 0
          
    for i in range(5):
      newlightmap = [row[:] for row in this.lightmap] # copy lightmap array
      for y in range(ycenter - radius, ycenter + radius + 1):
        for x in range(xcenter - radius, xcenter + radius + 1):
          if this[y][x].isEmpty and this.back[y][x].isEmpty: continue
          for r in range(-1, 2):
            if not ycenter - radius <= y + r <= ycenter + radius: continue
            for c in range(-1, 2):
              if not xcenter - radius <= x + c <= xcenter + radius: continue
              if r == 0 and c == 0: continue
              this.lightmap[y][x] = min(this.lightmap[y][x], newlightmap[y+r][x+c] + i * 50)
              count += 1
    
  def update(this):
    this.getVisibleBlocks()
    this.draw()
    # this.buildEdgePool()
    
    this.visibleBlocks.clear()
    
    
'''Menu stuff'''
class Button:
    def __init__(this, x, y, width, height, text):
        this.rect = pg.Rect(x, y, width, height)
        this.text = text
        
        this.hover_animation = 0
        this.press_animation = 0
        this.is_pressed = False
        
        this.base_colour = (45, 45, 45)
        this.hover_colour = (75, 75, 75)
        
        #Corner roundness
        this.corner_radius = 15
        
    def update(this, mouse_pos):
        #Hover animation
        target_hover = 1 if this.rect.collidepoint(mouse_pos) else 0
        this.hover_animation += (target_hover - this.hover_animation) * 0.15
        
        #Click animation
        if this.is_pressed:
            this.press_animation += (1 - this.press_animation) * 0.2
        else:
            this.press_animation += (0 - this.press_animation) * 0.2
        
    def handle_event(this, event, mouse_pos):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if this.rect.collidepoint(mouse_pos):
                this.is_pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            this.is_pressed = False
        
    def draw(this, font, text_colour, shadow_colour):
        current_color = [int(this.base_colour[i] + (this.hover_colour[i] - this.base_colour[i]) * this.hover_animation) for i in range(3)]
        
        hover_offset = int(this.hover_animation * 3)
        press_offset = int(this.press_animation * 2)
        button_rect = this.rect.copy()
        button_rect.y -= hover_offset - press_offset
        
        this._draw_button(button_rect, current_color)
        this._draw_text(font, text_colour, shadow_colour, button_rect)
        
    def _draw_button(this, button_rect, colour):
        # Draw shadow first
        shadow_rect = button_rect.copy()
        shadow_rect.y += 4
        pg.draw.rect(SURF, (0, 0, 0, 64), shadow_rect, border_radius=this.corner_radius)
        
        #Base button
        button_surface = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        pg.draw.rect(button_surface, colour, button_surface.get_rect(), border_radius=this.corner_radius)
        
        button_mask = pg.mask.from_surface(button_surface)
        
        #Highlight surface
        highlight_surface = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        highlight_color = (255, 255, 255, 30)
        
        highlight_rect = pg.Rect(0, 0, button_rect.width, 8)
        pg.draw.rect(highlight_surface, highlight_color, highlight_rect)
        
        masked_highlight = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        button_mask.to_surface(masked_highlight, setcolor=highlight_color, unsetcolor=(0,0,0,0))
        
        final_highlight = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        final_highlight.blit(masked_highlight, (0,0), highlight_rect)
        
        SURF.blit(button_surface, button_rect)
        SURF.blit(final_highlight, button_rect)
        
    def _draw_text(this, font, text_colour, shadow_color, button_rect):
        #Scale text with the hover animation
        scale_factor = 1 + this.hover_animation * 0.05
        
        text_surf = font.render(this.text, True, text_colour)
        text_surf = pg.transform.scale(text_surf, (int(text_surf.get_width() * scale_factor), int(text_surf.get_height() * scale_factor)))
        text_rect = text_surf.get_rect(center=button_rect.center)
        
        #Text shadow
        shadow_surf = font.render(this.text, True, shadow_color)
        shadow_surf = pg.transform.scale(shadow_surf, (int(shadow_surf.get_width() * scale_factor), int(shadow_surf.get_height() * scale_factor)))
        shadow_rect = shadow_surf.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        
        SURF.blit(shadow_surf, shadow_rect)
        SURF.blit(text_surf, text_rect)

class MainMenu:
    def __init__(this, width, height):
        this.width = width
        this.height = height
        this.screen = pg.display.set_mode((width, height))
        
        this._createButtons()

        this.buttonFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 36)
        this.splashFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 28)
        
        this.buttonTextColour = (240, 240, 240)
        this.textShadow = (20, 20, 20, 160)
        
        #Background
        this.bgPanorama = pg.image.load("title screen background animation.jpg").convert()
        
        this.overlay = pg.Surface((this.width, this.height))
        this.overlay.fill((0, 0, 0))
        this.overlay.set_alpha(40)
        
        this.bgScrollSpeed = 20
        this.bgOffset = 0
        
        #Title
        this.titleImage = pg.image.load("title screen title.png").convert_alpha()
        this.titleImageRect = this.titleImage.get_rect(center=(this.width // 2, this.height // 4))
        
        #Splash text stuff
        this.splashTexts = [
            "Dont sue us Minecraft!",
            "Made with Pygame!",
            "Lorem ipsum!",
            "Pygame >",
        ]
        
        this.currentSplash = random.choice(this.splashTexts)
        this.splashAngle = -15
        this.splashWaveOffset = 0
        this.splashScale = 1.0
        
    def _createButtons(this):
        buttonWidth, buttonHeight = 400, 50
        buttonX = (this.width - buttonWidth) // 2
        spacing = 24  #space between buttons
        startY = this.height // 2
        
        this.buttons = {
            'play': Button(buttonX, startY, buttonWidth, buttonHeight, "Play"),
            'instructions': Button(buttonX, startY + buttonHeight + spacing, buttonWidth, buttonHeight, "Instructions"),
            'keybinds': Button(buttonX, startY + (buttonHeight + spacing) * 2, buttonWidth, buttonHeight, "Options"),
            'quit': Button(buttonX, startY + (buttonHeight + spacing) * 3, buttonWidth, buttonHeight, "Quit")
        }
        
    def _updateBackground(this, time):
        this.bgOffset = (this.bgOffset + this.bgScrollSpeed * time / 1000.0) % this.bgPanorama.get_width()

    def _draw(this):
        #Draw background
        this.screen.blit(this.bgPanorama, (-this.bgOffset, 0))
        this.screen.blit(this.bgPanorama, (this.bgPanorama.get_width() - this.bgOffset, 0))
        this.screen.blit(this.overlay, (0, 0))
        
        #Title
        this.screen.blit(this.titleImage, this.titleImageRect)
        
        #Splash text
        this.splashWaveOffset += 0.03
        this.splashScale = 1.0 + math.sin(this.splashWaveOffset * 0.5) * 0.03  #subtle pulse
        
        splashSurf = this.splashFont.render(this.currentSplash, True, (255, 255, 0))
        splashSurf = pg.transform.rotate(splashSurf, this.splashAngle)
        splashSurf = pg.transform.scale(splashSurf, 
                                       (int(splashSurf.get_width() * this.splashScale),
                                        int(splashSurf.get_height() * this.splashScale)))
        
        splashYOffset = math.sin(this.splashWaveOffset) * 6
        splashPos = (this.width // 2 + 180, this.height // 4 + splashYOffset)
        this.screen.blit(splashSurf, splashPos)
        
        for button in this.buttons.values():
            button.draw(this.buttonFont, this.buttonTextColour, this.textShadow)

    def run(this):
        clock = pg.time.Clock()
        
        while True:
            mousePos = pg.mouse.get_pos()           
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    
                if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                    for button in this.buttons.values():
                        button.handle_event(event, mousePos)

                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if this.buttons['play'].rect.collidepoint(mousePos):
                        return
                    elif this.buttons['instructions'].rect.collidepoint(mousePos):
                        #InstructionsScreen.run()
                        pass
                    elif this.buttons['keybinds'].rect.collidepoint(mousePos):
                        pass
                    elif this.buttons['quit'].rect.collidepoint(mousePos):
                        pg.quit()
                        sys.exit()

            for button in this.buttons.values():
                button.update(mousePos)
            
            this._updateBackground(clock.get_time())
            this._draw()
            
            pg.display.flip()
            clock.tick(FPS)
    
#TODO work on these later hopefully        
class InstructionsScreen:
  pass
          
def change_keybinds():
    pass
class PauseScreen:
  def __init__(this, width, height):
    this.width = width
    this.height = height
    this.screen = pg.display.set_mode((width, height))

    this.buttonFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 36)
   
    this.buttonTextColour = (240, 240, 240)
    this.textShadow = (20, 20, 20, 160)
    
    resumeButton = Button((this.width - 400) // 2, this.height // 2,  400, 50, "Back to Game")
    quitButton = Button((this.width - 400) // 2, (this.height // 2) + 100, 400, 50, "Save and Quit") 

  
  def run(this):
    clock = pg.time.Clock()
    white = (255, 255, 255)
    SURF.fill(white)
    
    while True:
      mousePos = pg.mouse.get_pos()           
      for event in pg.event.get():
          if event.type == pg.QUIT:
              pg.quit()
              sys.exit()
              
      pg.display.flip()
      clock.tick(FPS)

class LoadingScreen:
    def __init__(this, width, height):
        this.width = width
        this.height = height
        this.screen = pg.display.set_mode((width, height))
        
        this.font = pg.font.Font("MinecraftRegular-Bmg3.otf", 20)
        this.titleFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 40)

        this.loading_messages = [
            "Generating world...",
            "Creating caves...",
            "Growing trees...",
            "Placing ores...",
            "Loading terrain...",
        ]    
        
        #?   message change interval is currently not working 😐
        this.currentMessage = 0
        this.messageChangeTimer = time.time()
        this.messageChangeInterval = 1.5    #seconds
        this.progress = 0.0
        this.startTime = time.time()

        this.barWidth = 400
        this.barHeight = 20
        this.barX = (width - this.barWidth) // 2
        this.bar_y = height // 2 + 30
        
    def update(this, progress):
        this.progress = progress
        
        current_time = time.time()
        if current_time - this.messageChangeTimer >= this.messageChangeInterval:
            this.currentMessage = (this.currentMessage + 1) % len(this.loading_messages)
            this.messageChangeTimer = current_time

    def draw(this):
        this.screen.fill((25, 25, 25))

        title = this.titleFont.render("Loading world...", True, (255, 255, 255))
        title_rect = title.get_rect(center=(this.width // 2, this.height // 3))
        this.screen.blit(title, title_rect)

        #Loading message
        message = this.font.render(this.loading_messages[this.currentMessage], True, (200, 200, 200))
        message_rect = message.get_rect(center=(this.width // 2, this.height // 2 - 20))
        this.screen.blit(message, message_rect)

        #Progress bar
        pg.draw.rect(this.screen, (50, 50, 50), (this.barX, this.bar_y, this.barWidth, this.barHeight))
        fill_width = int(this.barWidth * this.progress)
        pg.draw.rect(this.screen, (106, 176, 76), (this.barX, this.bar_y, fill_width, this.barHeight))

        #Percentage
        percentage = f"{int(this.progress * 100)}%"
        percent_text = this.font.render(percentage, True, (255, 255, 255))
        percent_rect = percent_text.get_rect(center=(this.width // 2, this.bar_y + 40))
        this.screen.blit(percent_text, percent_rect)

        #Elapsed load time
        elapsed_time = time.time() - this.startTime
        elapsed_text = this.font.render(f"Time elapsed: {elapsed_time:.1f} seconds", True, (200, 200, 200))
        elapsed_rect = elapsed_text.get_rect(center=(this.width // 2, this.bar_y + 120))
        this.screen.blit(elapsed_text, elapsed_rect)

        pg.display.flip()
        clock.tick(FPS)

class ThreadedWorldGenerator:
    def __init__(this):
        this.world = None
        this.loading_screen = LoadingScreen(WIDTH, HEIGHT)
        this.generation_thread = None
        this.progress_queue = queue.Queue()
        this.is_complete = False
        this.should_terminate = threading.Event()
        this.start_time = time.time()

    def generate_world_thread(this):
        this.world = World()
        generation_steps = [
            (this.world.generateWorld, 0.6),
            (this.world.generateMask, 0.2),
            (this.world.generateLight, 0.2)
        ]
        current_progress = 0.0
        
        for step_func, step_weight in generation_steps:
            if this.should_terminate.is_set():
                return
                
            step_func()
            current_progress += step_weight
            this.progress_queue.put(current_progress)

        this.progress_queue.put(1.0)
        this.is_complete = True
        
        total_time = time.time() - this.start_time
        print(f"World generation completed in {total_time:.2f} seconds")

    def start_generation(this):
        """Start world generation in a separate thread."""
        this.generation_thread = threading.Thread(target=this.generate_world_thread)
        this.generation_thread.start()
        
    def get_generated_world(this):
        if not this.is_complete:
            raise RuntimeError("World generation not complete")
        return this.world

    def update_loading_screen(this):
        latest_progress = None
        while not this.progress_queue.empty():
            try:
                latest_progress = this.progress_queue.get_nowait()
            except queue.Empty:
                break
        
        if latest_progress is not None:
            this.loading_screen.update(latest_progress)
        
        this.loading_screen.draw()
        

'''Main Loop'''
if __name__ == "__main__":
  SUNLIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  LIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  FRAME = SURF.get_rect()
  ASURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  ASURF.fill((0, 0, 0, 0))
  
  #Give player items at the beginning of the game
  defaultItems = [IronPickaxe(), IronAxe(), StoneAxe(), WoodenShovel(), CraftingTableItem()] + [CobbleStoneItem() for _ in range(192)] + [TorchItem() for _ in range(64)]
  
  world_generator = ThreadedWorldGenerator()
  world_generator.start_generation()
  
  MainMenu(WIDTH, HEIGHT).run()
    
  while not world_generator.is_complete:
      world_generator.update_loading_screen()
    
  pg.time.wait(50)
  
  font = pg.font.Font(None, 15)
  font20 = pg.font.Font(None, 20)
  
  player = Player()
  world = World()
  sun = Sun()
  
  end = time.time()
  print(f"World generation time: {end - start:.3f} seconds")
  
  while True:
    frameStartTime = time.time()
    SURF.fill((255, 255, 255))
    ASURF.fill((0, 0, 0, 0))
    SUNLIGHTSURF.fill((0, 0, 0, 255))
    LIGHTSURF.fill((0, 0, 0, 0))
    keys = pg.key.get_pressed()
    
    #sun.draw()
    world.update()
    player.update()
    
    #Temporarily game over logic
    if player.health <= 0:
      print("The skbidi would have died")

    #Player controls
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

    if pg.mouse.get_pressed()[0]:   #left click
      player.mine()
    if pg.mouse.get_pressed()[2]:   #right click
      player.place()

    for event in pg.event.get():
      if event.type == QUIT:
        pg.quit()
        sys.exit()
      elif event.type == 101:
        print("fps: ", round(clock.get_fps(), 2))    
        
      elif event.type == KEYDOWN and event.key == pg.K_ESCAPE:
        PauseScreen(WIDTH, HEIGHT).run()
        
      elif event.type == KEYDOWN and event.key == pg.K_e:
        check_for_interaction()
      elif event.type == KEYDOWN and event.key == pg.K_m:
        pixel = tuple(map(lambda a: BLOCK_SIZE*a,pixelToCoord(*pg.mouse.get_pos())))
        print(pixel, world.mask.get_at(pixel), world.blockAt(*pixelToCoord(*pg.mouse.get_pos())).rect.topleft)
        
        # print(world.mask.get_at())

    SURF.blit(ASURF, (0, 0))
    # print(lights)
    for light in lights:
      # print(light)
      light.drawLight()
    SUNLIGHTSURF = pg.transform.smoothscale(SUNLIGHTSURF, (WIDTH//15, HEIGHT//15))
    SUNLIGHTSURF = pg.transform.smoothscale(SUNLIGHTSURF, (WIDTH, HEIGHT))
    # SUNLIGHTSURF.blit(LIGHTSURF, (0,0))
    SURF.blit(SUNLIGHTSURF, ((0,0)))
    player.drawHUD()
    
    SURF.blit(font20.render(str(pixelToCoord(*player.camera.center)), True, (0,0,0)), (20, 50))
    
    frameEndTime = time.time()
    clock.tick(FPS)
    pg.display.flip()