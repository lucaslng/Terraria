import math, random, time, copy, threading, pickle          #pickle stores game data onto system
import pygame as pg
from pygame.locals import *
from pygame.math import Vector2

#import code from other files
from constants import *
from sprites import *
from customqueue import Queue
from utils import Direction, sysexit

from abc import *
from dataclasses import dataclass
from typing import *
from enum import Enum

SEED = time.time()
random.seed(SEED)
start = time.time()

pg.init()
pg.font.init()
clock = pg.time.Clock()

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

  def interact(self):
    '''To be called when Interactable is interacted with.'''
    pass

@dataclass
class Light:
  '''Base class for any object with light except the sun'''
  lightRadius: int
  x: float
  y: float
  relative: bool = True
  
  def __post_init__(self):
    # print("post init light")
    lights.append(self)
    
  def drawLight(self):
    '''draw light'''
    if self.relative:
      # print(self.x, self.y, self.x*20, self.y*20, coordWorld2Relative(self.x, self.y))
      pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), coordWorld2Relative(self.x,self.y), self.lightRadius)
    else:
      pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), (self.x,self.y), self.lightRadius)

lights: list[Light] = []

@dataclass
class Item:
  """Base item class"""

  SIZE = 15
  name: str
  texture: pg.surface.Surface
  stackSize: int

  def slotTexture(self) -> pg.surface.Surface:
    return pg.transform.scale_by(self.texture, 0.8)

  def drawItem(self, x: int, y: int):
    SURF.blit(self.itemTexture, (x, y))

  def __eq__(self, other) -> bool:
    if other is None:
      return False
    return self.name == other.name

  def isPlaceable(self) -> bool:
    return isinstance(self, PlaceableItem)

  def isTool(self) -> bool:
    return isinstance(self, Tool)
  
  def isExecutable(self) -> bool:
    return isinstance(self, Executable)


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

  def __post_init__(self):
    self.texture = self.texture.convert_alpha()
    self.rect = pg.rect.Rect(
      self.x * BLOCK_SIZE, self.y * BLOCK_SIZE, self.SIZE, self.SIZE)
    self.vertices = (
      self.rect.topleft,
      self.rect.topright,
      self.rect.bottomleft,
      self.rect.bottomright,
    )
    self.mask = pg.mask.from_surface(self.texture)
    if self.isAir: self.mask.clear()
    self.edgeExist = [False for _ in range(4)]
    self.edgeId = [0 for _ in range(4)]
    
    if self.isBack and not self.isAir:
      self.texture.blit(self.BACK_TINT, (0,0))

  def drawBlockOutline(self, color: pg.color.Color):
    pg.draw.rect(ASURF, color, relativeRect(self.rect), 2)

  def drawBlock(self):
    SURF.blit(self.texture, relativeRect(self.rect))
    breakingRect = relativeRect(self.rect.copy())
    breakingRect.scale_by_ip(
      self.amountBroken / self.hardness, self.amountBroken / self.hardness
    )
    pg.draw.rect(ASURF, (0, 0, 0, 100), breakingRect)

  def offset(self, x: int, y: int) -> tuple[int, int]:
    return x - self.rect.x, y - self.rect.y

  def collides(self, x: int, y: int) -> bool:
    if self.isEmpty:
      return False
    if self.mask.overlap(player.mask, self.offset(x, y)):
      # pg.draw.rect(SURF, (255, 0, 0), relativeRect(self.rect), width=3)
      return True
    else:
      return False
  
  def item(self):
    return BlockItemRegistry.getItem(type(self))

  def isInCamera(self) -> bool:
    return self.rect.colliderect(player.camera)
  
  def exposedVertices(self) -> set[tuple[int, int]]:
    result = set()
    if self.x-1 >= 0 and world[self.y][self.x-1].isAir:
      result.update((self.rect.topleft, self.rect.bottomleft))
    if self.x+1 < WORLD_WIDTH and world[self.y][self.x+1].isAir:
      result.update((self.rect.topright, self.rect.bottomright))
    if self.y-1 >= 0 and world[self.y-1][self.x].isAir:
      result.update((self.rect.topleft, self.rect.topright))
    return result

  def __repr__(self):
    return self.name

  def __hash__(self):
    return hash((self.x, self.y))

  def __eq__(self, other):
    return hash(self) == hash(other)


@dataclass
class PlaceableItem(Item):
  '''Items that have a corresponding block and can be placed.'''
  @classmethod
  def block(cls):
    return BlockItemRegistry.getBlock(cls)
  
  def place(self, x: int, y: int) -> None:
    world[y][x] = self.block()(x, y)
    # world.mask.draw(world[y][x].mask, world[y][x].rect.topleft)

@dataclass
class Executable(ABC):
  '''Items that have a special effect to be executed when held'''
  @abstractmethod
  def execute(self):
    '''execute whatever needs to be done'''
    pass
  
  @abstractmethod
  def unexecute(self):
    '''unexecute when item is swapped out'''
    pass

class AirBlock(Block):
  '''Empty air block'''
  texture = pg.surface.Surface((BLOCK_SIZE, BLOCK_SIZE))
  texture.fill((0, 0, 0, 0))
  def __init__(self, x=-1, y=-1, isBack=False):
    super().__init__("Air", self.texture, x, y, 0, BlockType.NONE, isAir=True, isEmpty=True, isBack=isBack)

class CraftingTableBlock(Block, Interactable):
  craftingTableTexture = pg.transform.scale(
    pg.image.load("crafting_table.png"), (BLOCK_SIZE, BLOCK_SIZE))
  
  def __init__(self, x, y, isBack=False):
    Block.__init__(self, name="Crafting Table", texture=self.craftingTableTexture,
                   x=x, y=y, hardness=2.5, blockType=BlockType.AXE, isBack=isBack)

class CraftingTableItem(PlaceableItem):
  craftingTableTexture = pg.transform.scale(pg.image.load("crafting_table.png"), (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Crafting Table", self.craftingTableTexture, 64)

class DirtVariant:
  def __init__(self, name: str, texture):
    self.name = name
    self.texture = texture
class DirtVariantDirt(DirtVariant):
  dirtTexture = pg.transform.scale(
    pg.image.load("dirt.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(self):
    super().__init__("Dirt", self.dirtTexture)
class DirtVariantGrass(DirtVariant):
  grassTexture = pg.transform.scale(
    pg.image.load("grass_block.png"), (BLOCK_SIZE, BLOCK_SIZE)
  )
  grassItemTexture = pg.transform.scale(grassTexture, (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Grass Block", self.grassTexture)
class DirtBlock(Block):
  def __init__(self, x, y, variant: DirtVariant = DirtVariantDirt(), isBack=False):
    super().__init__(variant.name, variant.texture, x, y, 1.5, BlockType.SHOVEL, isBack=isBack)
    
    self.variant = variant.name.lower()
class DirtItem(PlaceableItem):
  dirtItemTexture = pg.transform.scale(pg.image.load("dirt.png"), (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Dirt", self.dirtItemTexture, 64)
    
class OakLogBlock(Block):
    oakLogTexture = pg.transform.scale(pg.image.load("oak_log.png"), (BLOCK_SIZE, BLOCK_SIZE))  
    def __init__(self, x, y, isBack=False):
        super().__init__("Oak Log", self.oakLogTexture, x, y, 2.5, BlockType.AXE, isBack=isBack)
class OakLogItem(PlaceableItem):
    oakLogItemTexture = pg.transform.scale(pg.image.load("oak_log.png"), (Item.SIZE, Item.SIZE))
    def __init__(self):
        super().__init__("Oak Log", self.oakLogItemTexture, 64)

class LeavesBlock(Block):
    leavesTexture = pg.transform.scale(pg.image.load("leaves.png"), (BLOCK_SIZE, BLOCK_SIZE))  
    def __init__(self, x, y, isBack=False):
        super().__init__("Leaves", self.leavesTexture, x, y, 1, BlockType.SHEARS, isBack=isBack)

class StoneBlock(Block):
  stoneTexture = pg.transform.scale(
    pg.image.load("stone.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(self, x, y, isBack=False):
    super().__init__("Stone", self.stoneTexture, x, y, 5, BlockType.PICKAXE, isBack=isBack)
class CobblestoneBlock(Block):
  cobblestoneTexture = pg.transform.scale(
    pg.image.load("cobblestone.png"), (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(self, x, y, isBack=False):
    super().__init__("Cobblestone", self.cobblestoneTexture, x, y, 5.5, BlockType.PICKAXE, isBack=isBack)
class CobbleStoneItem(PlaceableItem):
  cobblestoneItemTexture = pg.transform.scale(
    pg.image.load("cobblestone.png"), (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Cobblestone", self.cobblestoneItemTexture, 64)


class Generated(ABC):
  '''Things that can be generated by simplex noise'''
  veinSize: int
  rarity: int
  
class IronOreBlock(Block, Generated):
  ironOreTexture = sprites["ironOre"]
  veinSize = 3.2
  rarity = 0.38
  def __init__(self, x, y, isBack=False):
    Block.__init__(self, "Iron Ore", self.ironOreTexture, x, y, 6, BlockType.PICKAXE, isBack=isBack)
class IronOreItem(PlaceableItem):
  ironOreItemTexture = sprites["ironOre"]
  def __init__(self):
    super().__init__("Iron Ore", self.ironOreItemTexture, 64)

class CoalOreBlock(Block, Generated):
  coalTexture = sprites["coalOre"]
  veinSize = 3.9
  rarity = 0.3
  def __init__(self, x, y, isBack=False):
    Block.__init__(self, "Coal Ore", self.coalTexture, x, y, 3, BlockType.PICKAXE, isBack=isBack)
class CoalItem(Item):
  coalItemTexture = sprites["coalOre"]
  def __init__(self):
    super().__init__("Coal", self.coalItemTexture, 64)

ores = {CoalOreBlock, IronOreBlock}

class TorchBlock(Block, Light):
  torchTexture = pg.transform.scale(pg.image.load("torch.png").convert_alpha(), (BLOCK_SIZE,BLOCK_SIZE))
  def __init__(self, x, y, isBack=False):
    Block.__init__(self, "Torch", self.torchTexture, x, y, 1, BlockType.NONE, isEmpty=True, isBack=isBack)
    Light.__init__(self, 100, x, y)
    lights.append(self)
class TorchItem(PlaceableItem, Executable):
  torchItemTexture = pg.transform.scale(pg.image.load("torch.png").convert_alpha(), (Item.SIZE, Item.SIZE))
  def __init__(self):
    PlaceableItem.__init__(self, "Torch", self.torchItemTexture, 64)
  def execute(self):
    player.lightRadius = 100
  def unexecute(self):
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

  def draw(self, x: float, y: float, size: float = size, transparent=False) -> None:
    if not transparent:
      pg.draw.rect(SURF, (200, 200, 200), (x, y, size, size))
    else:
      pg.draw.rect(ASURF, (200, 200, 200, 160), (x, y, size, size))
      
    if self.isActive:
      pg.draw.rect(SURF, (0, 0, 0), (x, y, size, size), 2)
    else:
      pg.draw.rect(SURF, (90, 90, 90), (x, y, size, size), 2)

    if self.item is not None:
      item_texture = self.item.texture
      scaled_texture = pg.transform.scale(item_texture, (size - 6, size - 6))
      
      #center texture in the slot
      texture_rect = scaled_texture.get_rect()
      texture_rect.center = (x + size / 2, y + size / 2)
      SURF.blit(scaled_texture, texture_rect.topleft)

      if self.count > 1:
        count_text = font20.render(str(self.count), True, (255, 255, 255))
        
        #item counter in the bottom right of the slot
        text_rect = count_text.get_rect(bottomright= (x + size - 5, y + size - 5))
        SURF.blit(count_text, text_rect.topleft)
        
      #Draw durability bar
      if self.item.isTool() and self.item.durability != self.item.startingDurability:
        bar_height = 3
        bar_width = size - 4
        bar_x = x + 2
        bar_y = y + size - bar_height - 1
        
        tool: Tool = self.item
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
  
  def __post_init__(self):
    self.array = [[Slot() for _ in range(self.cols)] for _ in range(self.rows)]
    
  def __getitem__(self, i: int) -> list[Slot]:
    return self.array[i]
  
  def draw(self, transparent=False) -> None:
    for r in range(self.rows):
      for c in range(self.cols):
        self[r][c].draw(self.x+c*self.slotSize, self.y+r*self.slotSize, size = self.slotSize, transparent=transparent)
        
class Menu:
  '''A menu is effectively a list of Sections. One section is an array of Slots.'''
  def __init__(self, *args: Section, isActive: bool = False):
    self.isActive = isActive
    self.sections = [args[i] for i in range(len(args))]
  
  def draw(self, transparent=False) -> None:
    for section in self.sections:
      section.draw(transparent)


@dataclass
class Inventory:
  """Inventory class"""
  rows: int
  cols: int
  menux: int
  menuy: int
  
  def __post_init__(self):
    self.inventory = [[Slot() for _ in range(self.cols)]
                      for _ in range(self.rows)]
    self.menu = Menu(Section(self.rows, self.cols, self.menux, self.menuy))

  def addItem(self, item: Item) -> bool:
    """Attempts to add an item to the inventory"""
    #add item to stack with existing items
    for r in range(self.rows):
        for c in range(self.cols):
            slot = self.inventory[r][c]
            if slot.item and slot.item == item and slot.count < slot.item.stackSize:
                slot.count += 1
                self.menu.draw()
                return True
                
    #find first empty slot if there isn't an existing slot
    for r in range(self.rows):
        for c in range(self.cols):
            slot = self.inventory[r][c]
            if slot.item is None:
                slot.item = item
                slot.count = 1
                #print('added to inventory')
                self.menu.draw()
                return True
                
    return False  #inventory full

  def isPlaceable(self) -> bool:
    return isinstance(self, PlaceableItem)

  def __getitem__(self, row: int):
    return self.inventory[row]


@dataclass
class Tool(Item):
  speed: float
  startingDurability: int
  blockType: BlockType
  
  def __post_init__(self):
    self.durability = self.startingDurability

class Shears(Tool):
  shearsTexture = pg.transform.scale(
    pg.image.load("shears.png"), (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Shears", self.shearsTexture, 1, 1.5, 238, BlockType.SHEARS)
    
'''Wooden'''
class WoodenPickaxe(Tool):
  def __init__(self):
    super().__init__("Wooden Pickaxe", sprites["woodenPickaxe"], 1, 1.5, 59, BlockType.PICKAXE)  
class WoodenAxe(Tool):
  def __init__(self):
    super().__init__("Wooden Axe", sprites["woodenAxe"], 1, 1.5, 59, BlockType.AXE)
class WoodenShovel(Tool):
  def __init__(self):
    super().__init__("Wooden Shovel", sprites["woodenShovel"], 1, 1.5, 59, BlockType.SHOVEL)
class WoodenSword(Tool):
  def __init__(self):
    super().__init__("Wooden Sword", sprites["woodenSword"], 1, 1, 59, BlockType.SWORD)
    
'''Stone'''
class StonePickaxe(Tool):
  def __init__(self):
    super().__init__("Stone Pickaxe", sprites["stonePickaxe"], 1, 3, 131, BlockType.PICKAXE)
class StoneAxe(Tool):
  def __init__(self):
    super().__init__("Stone Axe", sprites["stoneAxe"], 1, 2.5, 131, BlockType.AXE)
class StoneShovel(Tool):
  def __init__(self):
    super().__init__("Stone Shovel", sprites["stoneShovel"], 1, 2.5, 131, BlockType.SHOVEL)
class StoneSword(Tool):
  def __init__(self):
    super().__init__("Stone Sword", sprites["stoneSword"], 1, 1, 131, BlockType.SWORD)
    
'''Iron'''
class IronPickaxe(Tool):
  def __init__(self):
    super().__init__("Iron Pickaxe", sprites["ironPickaxe"], 1, 5, 250, BlockType.PICKAXE)
class IronAxe(Tool):
  def __init__(self):
    super().__init__("Iron Axe", sprites["ironAxe"], 1, 3.5, 250, BlockType.AXE)
class IronShovel(Tool):
  def __init__(self):
    super().__init__("Iron Shovel", sprites["ironShovel"], 1, 3.5, 250, BlockType.SHOVEL)
    
'''Diamond'''
class DiamondPickaxe(Tool):
  pass
  

class HasInventory:
  """Parent class for classes than have an inventory"""

  def __init__(self, rows: int, cols: int, menux: int, menuy: int):
    self.inventory = Inventory(rows=rows, cols=cols, menux=menux, menuy=menuy)


class Entity:
  """Base entity class. Contains methods for moving, drawing, and gravity"""

  hvelo = 0
  vvelo = 0
  gravityvelo = 0
  previousDirection = True
  isOnBlock = False
  animations = {}

  def __init__(
      self,
      x: float,
      y: float,
      width: float,
      height: float,
      texture: pg.surface.Surface,
      health: float,
      speed: float,
      jumpHeight: float,
  ):
    self.rect = pg.rect.Rect(x, y, width, height)
    self.texture = texture
    self.reversedTexture = pg.transform.flip(texture, True, False).convert_alpha()
    self.mask = pg.mask.from_surface(texture)
    self.health = health
    self.speed = speed
    self.jumpHeight = jumpHeight
    
    # kinematic vectors
    self.position = Vector2(x, y)
    self.velocity = Vector2()
    self.accel = Vector2()
    
    # kinematic constants
    self.HORIZONTAL_ACCEL = 1
    self.HORIZONTAL_FRICTION = 0.2

  def moveLeft(self) -> None:
    if self.hvelo > -5:
      self.hvelo -= self.speed

  def moveRight(self) -> None:
    if self.hvelo < 5:
      self.hvelo += self.speed

  def jump(self) -> None:
    if self.vvelo > 4 and self.isOnBlock:
      self.vvelo -= self.jumpHeight

  def checkCollisionH(self) -> int:
    newrect = self.rect.copy()
    newrect.x += self.hvelo - 1
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
      return self.hvelo

  def checkCollisionV(self) -> int:
    newrect = self.rect.copy()
    newrect.y += self.vvelo
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
    if self.vvelo < 0:
      # print("attepmting to move up!")
      if (
        blockTopRight.collides(*newrect.topleft)
        or blockTopLeft.collides(*newrect.topleft)
        ):
        # print("top collides! not moving!")
        self.vvelo = 0
        return 0
      else:
        return self.vvelo
    elif self.vvelo > 0:
      if (
        blockBotRight.collides(*newrect.topleft)
        or blockBotLeft.collides(*newrect.topleft)
      ):
        # print("bot collides! not moving!")
        self.isOnBlock = True
        return 0
      else:
        self.isOnBlock = False
        return self.vvelo
    else:
      return 0

  def move(self) -> None:
    if self.hvelo < 0:
      self.hvelo += min(1, abs(self.hvelo))  # reduce horizontal velocity constantly to 0
    elif self.hvelo > 0:
      self.hvelo -= min(1, self.hvelo)
    self.rect.x += self.checkCollisionH()
    self.rect.y += self.checkCollisionV()
    if self.vvelo < 5:
      self.vvelo += gravity

  def draw(self) -> None:
    if self.hvelo < 0:
      SURF.blit(self.reversedTexture, relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.reversedTexture)
      self.previousDirection = 0
    elif self.hvelo > 0:
      SURF.blit(self.texture, relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.texture)
      self.previousDirection = 1
    elif self.previousDirection:
      SURF.blit(self.texture, relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.texture)
    else:
      SURF.blit(self.reversedTexture, relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.reversedTexture)

  def update(self) -> None:
    self.move()
    self.draw()


class Player(Entity, HasInventory, Light):
  texture = sprites["cat"]["walk"][0]
  selfSprites = sprites["cat"]
  blockFacing = None
  reach = 4 * BLOCK_SIZE
  
  full_heart_texture = pg.transform.scale(pg.image.load("full_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))
  half_heart_texture = pg.transform.scale(pg.image.load("half_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))
  empty_heart_texture = pg.transform.scale(pg.image.load("empty_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))

  def __init__(self):
    Light.__init__(self, BLOCK_SIZE//2, *FRAME.center, relative=False)
    self.camera = FRAME.copy()
    self.camera.center = (
      BLOCK_SIZE * (WORLD_WIDTH // 2),
      BLOCK_SIZE * round(WORLD_HEIGHT * 0.55),
    )
    
    Entity.__init__(
        self,
        self.camera.centerx - BLOCK_SIZE // 2,
        self.camera.centery - BLOCK_SIZE // 2,
        BLOCK_SIZE,
        BLOCK_SIZE,
        self.texture,
        10,
        2,
        18,
    )
    self.mask = pg.mask.Mask((20, 20), True)

    HasInventory.__init__(self, 4, 10, 15, 80)
    
    self.heldSlotIndex = 0  # number from 0 to 9
    self.rect.center = self.camera.center
    self.centerRect = self.rect.copy()
    self.centerRect.center = FRAME.center
    self.max_health = 20
    self.health = self.max_health

    self.falling = False
    self.fall_start_y = None
    self.fall_damage_threshold = 10 * BLOCK_SIZE
    self.is_initial_spawn = True
    self.spawn_protection_timer = 120

    self.usingItem = False
    self.placingBlock = False

    #Add items at the beginning of the game to the player
    for item in defaultItems: self.inventory.addItem(item)

    # beginning tick, tick length
    self.animations["usingItem"] = pg.time.get_ticks() + 200
    self.animations["placingBlock"] = 250

  def draw_health(self):
    """Draw health as hearts on the screen"""
    HEART_SPACING = 25
    HEART_X_START = 10
    HEART_Y = 10

    full_hearts = self.health // 2
    half_hearts = self.health % 2
    empty_hearts = (self.max_health - self.health) // 2

    #Full hearts
    for i in range(full_hearts):
      SURF.blit(self.full_heart_texture, (HEART_X_START + i * HEART_SPACING, HEART_Y))   
    #Half hearts
    if half_hearts:
      SURF.blit(self.half_heart_texture,(HEART_X_START + full_hearts * HEART_SPACING, HEART_Y))     
    #Empty hearts
    for i in range(empty_hearts):
      SURF.blit(self.empty_heart_texture,(HEART_X_START +(full_hearts + half_hearts + i) * HEART_SPACING,HEART_Y))

  def draw(self):
    # print(self.vvelo)
    if self.hvelo < 0:
      if self.vvelo < -4:
        self.selfSprites["jump"].drawFrame(*relativeRect(self.rect).topleft, 2, flipped=True)
      else:
        self.selfSprites["walk"].drawAnimated(*relativeRect(self.rect).topleft, flipped=True)
      self.previousDirection = 0
    elif self.hvelo > 0:
      if self.vvelo < -4:
        self.selfSprites["jump"].drawFrame(*relativeRect(self.rect).topleft, 2)
      else:
        self.selfSprites["walk"].drawAnimated(*relativeRect(self.rect).topleft)
      self.previousDirection = 1
    elif self.previousDirection:
      self.selfSprites["sit"].drawAnimated(*relativeRect(self.rect).topleft)
    else:
      self.selfSprites["sit"].drawAnimated(*relativeRect(self.rect).topleft, flipped=True)

  def hotbar(self) -> list[Slot]:
    '''Returns the first row of the player's inventory'''
    return self.inventory[0]

  def heldSlot(self) -> Slot:
    '''Returns the held slot, or None if the slot is empty'''
    slot = self.hotbar()[self.heldSlotIndex]
    if slot:
      return slot
    else:
      return None

  def executeHeldSlotEffect(self):
    '''do whatever the heldslot says needs to be done'''
    if self.heldSlot().item and self.heldSlot().item.isExecutable():
      self.heldSlot().item.execute()
  
  def changeSlot(self, index: int):
    self.heldSlot().isActive = False
    if self.heldSlot().item and self.heldSlot().item.isExecutable():
      self.heldSlot().item.unexecute()
    self.heldSlotIndex = index
    self.heldSlot().isActive = True

  def drawHeldItem(self):
    slot = self.heldSlot()
    if slot.item:
      texture = slot.item.slotTexture()
      if self.usingItem and pg.time.get_ticks() % 200 < 100:
        texture = pg.transform.rotozoom(texture, -35, 1)
      elif self.animations["placingBlock"] < 100:
        texture = pg.transform.rotozoom(
          texture, -self.animations["placingBlock"] / 3.8, 1)
        self.animations["placingBlock"] += 1000 / FPS
        self.placingBlock = False
      if self.previousDirection == False:
        texture = pg.transform.flip(texture, True, False)
      
      SURF.blit(texture, FRAME.center)

  def drawHotbar(self):
    """Draws the first row of the inventory on the screen"""
    HOTBAR_X = (WIDTH - (self.inventory.cols * Slot.size)) // 2
    HOTBAR_Y = HEIGHT - Slot.size - 10

    for col in range(self.inventory.cols):
      slot_x = HOTBAR_X + col * Slot.size
      slot_y = HOTBAR_Y
      slot = self.hotbar()[col]
      slot.draw(slot_x, slot_y)
      
  def drawInventory(self) -> None:
    """Draw the inventory in the top left corner"""
    for r in range(self.inventory.rows):
      for c in range(self.inventory.cols):
          slot = self.inventory.inventory[r][c]

          slot_x = self.inventory.menux + (c * Slot.size)
          slot_y = self.inventory.menuy + (r * Slot.size)
          slot.draw(slot_x, slot_y, Slot.size, True)

  def move(self):
    if self.is_initial_spawn:
      self.falling = False
      self.fall_start_y = None

      self.spawn_protection_timer -= 1
      if self.spawn_protection_timer <= 0:
        self.is_initial_spawn = False

    if self.vvelo > 0:
      if not self.falling:
        self.falling = True
        self.fall_start_y = self.rect.bottom

    super().move()
    self.camera.center = self.rect.center

    if self.falling and self.isOnBlock and not self.is_initial_spawn:
      fall_distance = abs(self.fall_start_y - self.rect.bottom)

      if fall_distance > self.fall_damage_threshold:
        # damage based on fall distance
        damage = int(
          (fall_distance - self.fall_damage_threshold) / BLOCK_SIZE)
        self.health = max(0, self.health - damage)

      self.falling = False
      self.fall_start_y = None

  def mine(self):
    if self.blockFacing:
      if self.blockFacing.amountBroken < self.blockFacing.hardness:
        miningSpeed = 1
        
        if self.heldSlot().item and self.heldSlot().item.isTool():
          #Checks if durability is 0
          if self.heldSlot().item.blockType == self.blockFacing.blockType:
            miningSpeed = self.heldSlot().item.speed
          if self.heldSlot().item.durability == 0:
            self.heldSlot().item = None
            self.heldSlot().count = 0
            
        self.usingItem = True
        self.blockFacing.amountBroken += miningSpeed / FPS
      else:
        # print("mined", self.blockFacing.name,
        #       "got", self.blockFacing.item().name)
        # world.mask.erase(world[self.blockFacing.y][self.blockFacing.x].mask, self.blockFacing.rect.topleft)
        world[self.blockFacing.y][self.blockFacing.x] = AirBlock(
            self.blockFacing.x, self.blockFacing.y
        )
        if world.back[self.blockFacing.y][self.blockFacing.x].isAir: world.generateLight(self.blockFacing.y, self.blockFacing.x)
        item = self.blockFacing.item()
        
        if self.heldSlot().item and self.heldSlot().item.isTool():
          if self.heldSlot().item.blockType == self.blockFacing.blockType:
            miningSpeed = self.heldSlot().item.speed
            
          self.heldSlot().item.durability -= 1
        
        if item:
          self.inventory.addItem(item())

  def place(self):
    if self.heldSlot().item and self.heldSlot().count > 0 and self.heldSlot().item.isPlaceable():
      x, y = pixelToCoord(*pg.mouse.get_pos())
      if world.blockAt(x, y).isAir:
        self.animations["placingBlock"] = 0
        self.heldSlot().item.place(x, y)
        self.heldSlot().count -= 1
        if self.heldSlot().count == 0:
          self.heldSlot().item = None
        if world.back[y][x].isAir: world.generateLight(y, x)

  def drawCircle(self):
    pg.draw.circle(ASURF, (0, 0, 0, 120), FRAME.center, BLOCK_SIZE * 4)

  def getBlockFacing(self):
    """Returns the block that the player is facing, if it is in range"""
    blockPixel = bresenham(*pg.mouse.get_pos(), *FRAME.center)
    if blockPixel:
      block = world.blockAt(*pixelToCoord(*bresenham(*pg.mouse.get_pos(), *FRAME.center)))
      for vertex in block.vertices:
        if math.dist(relativeCoord(*vertex), FRAME.center) < self.reach:
          return block
    return None

  def drawBlockFacing(self):
    if self.blockFacing:
      self.blockFacing.drawBlockOutline((0, 0, 0, 200))

  def update(self):
    super().update()
    
    self.blockFacing = self.getBlockFacing()
    self.drawBlockFacing()
    self.drawHeldItem()
    self.drawHUD()
    if not pg.mouse.get_pressed()[0]:
      self.usingItem = False
    self.executeHeldSlotEffect()
  
  def drawHUD(self):
    self.draw_health()
    self.drawHotbar()
    self.drawInventory()

class Sun:
  size = BLOCK_SIZE * 5
  sunTexture = pg.transform.scale(pg.image.load("sun.png"), (size, size))
  # pg.transform.threshold(sunTexture, sunTexture, (0,0,0,255), (120,120,120,0), (0,0,0,0), 1, inverse_set=True)
  def __init__(self):
    self.pos = (FRAME.centerx, 0)
  def draw(self):
    ASURF.blit(self.sunTexture, (HEIGHT * 0.1, HEIGHT * 0.1, self.size, self.size))

@dataclass
class Edge:
  x: int
  y: int
  ex: int
  ey: int
  
  def draw(self):
    # if self.x != self.ex and self.y != self.ey: print("diagonal wtf")
    pg.draw.line(SURF,(0,0,0),relativeCoord(self.x*BLOCK_SIZE, self.y*BLOCK_SIZE),relativeCoord(self.ex*BLOCK_SIZE, self.ey*BLOCK_SIZE), 3)
    # pg.draw.circle(SURF,(0,255,0),relativeCoord(self.x*BLOCK_SIZE,self.y*BLOCK_SIZE), 3)
    # pg.draw.circle(SURF,(0,255,0),relativeCoord(self.ex*BLOCK_SIZE,self.ey*BLOCK_SIZE), 3)
  def __repr__(self):
    return str((self.x, self.y, self.ex, self.ey))

class World:
  litVertices = list()
  vertices = set()
  edgePool: List[Edge] = list()
  def __init__(self):
    self.array = [
        [AirBlock(x, y) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    # cannot deepcopy pygame surface so I have to loop over it again
    self.back = [
        [AirBlock(x, y, isBack=True) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    
    self.mask = pg.mask.Mask((WORLD_WIDTH*BLOCK_SIZE, WORLD_HEIGHT*BLOCK_SIZE))
    self.lightmap = [ # generate fully lit light map at the beginning
      [0 for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)]
    self.generateWorld()
    # self.generateMask()
    self.generateLight()

  class SimplexNoise:
    def __init__(self, scale: float, dimension: int, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT):
      if dimension == 1:
        self.noise = self.__noise1d(width, scale)
      elif dimension == 2:
        self.noise = self.__noise2d(width, height, scale)
      else:
        return None

    def __getitem__(self, x: int):
      return self.noise[x]

    @staticmethod
    def __fade(t):
      return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def __generatePermutation():
      random.seed(random.randint(0, BIG))
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

    def __noise1d(self, width, scale=1.0):
      perm = self.__generatePermutation()
      noise = []

      for i in range(width):
        x = i / scale
        x0 = math.floor(x)
        x1 = x0 + 1

        dx0 = x - x0
        dx1 = x - x1

        u = self.__fade(dx0)

        g0 = self.__gradient1d(perm[x0 % 256])
        g1 = self.__gradient1d(perm[x1 % 256])

        n0 = g0 * dx0
        n1 = g1 * dx1

        value = pg.math.lerp(n0, n1, u)
        noise.append(value)

      return noise

    def __noise2d(self, width, height, scale=1.0):
      perm = self.__generatePermutation()
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

          u = self.__fade(dx0)
          v = self.__fade(dy0)

          g00 = self.__gradient2d(perm[(x0 + perm[y0 % 256]) % 256])
          g10 = self.__gradient2d(perm[(x1 + perm[y0 % 256]) % 256])
          g01 = self.__gradient2d(perm[(x0 + perm[y1 % 256]) % 256])
          g11 = self.__gradient2d(perm[(x1 + perm[y1 % 256]) % 256])

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

  def generateWorld(self):
    # Precompute noise
    grassHeightNoise = self.SimplexNoise(19, 1)
    stoneHeightNoise = self.SimplexNoise(30, 1)
    cavesNoise = self.SimplexNoise(9, 2)

    oresNoise = {
      ore.__name__: (self.SimplexNoise(ore.veinSize, 2), ore)
      for ore in ores
    }

    # Generate terrain in batch
    for x in range(WORLD_WIDTH):
      grassHeight = round(WORLD_HEIGHT * 0.58 + 9 * grassHeightNoise[x])
      stoneHeight = round(grassHeight + 5 + 5 * stoneHeightNoise[x])

      # Stone and Dirt pass in batch
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, -1):
          if y > stoneHeight:
              self.array[y][x] = StoneBlock(x, y)
              self.back[y][x] = StoneBlock(x, y, isBack=True)
          else:
              self.array[y][x] = DirtBlock(x, y)
              self.back[y][x] = DirtBlock(x, y, isBack=True)

      # Grass block
      self[grassHeight][x] = DirtBlock(
          x, grassHeight, DirtVariantGrass()
      )

      # Cave pass
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, -1):
          if cavesNoise[y][x] > 0.1:
              self.array[y][x] = AirBlock(x, y)

      # Ore pass
      for ore_name, (oreNoise, ore) in oresNoise.items():
          for y in range(WORLD_HEIGHT - 1, stoneHeight, -1):
              if oreNoise[y][x] > ore.rarity and not self[y][x].isAir:
                  self.array[y][x] = ore(x, y)
      
      # Tree pass
      if isinstance(self[grassHeight][x], DirtBlock) and self[grassHeight][x].variant == "grass block":
          if random.random() > 0.8:  # Simplified tree placement
              self.__generateTree(x, grassHeight - 1)

  def generateMask(self):
    for row in self.array:
      for block in row:
        self.mask.draw(block.mask, block.rect.topleft)
        
  def __generateTree(self, x, y):
    if x < 3: return
    if x > WORLD_WIDTH - 3: return
    height = random.randint(3, 7)
    for r in range(y-height-1, y+1):
      for c in range(x-2, x+3):
        if not self[r][c].isAir: return
    for i in range(height):
      self[y-i][x] = OakLogBlock(x, y-i)
    self[y-height][x-2] = LeavesBlock(x-2, y-height)
    self[y-height][x-1] = LeavesBlock(x-1, y-height)
    self[y-height][x] = LeavesBlock(x, y-height)
    self[y-height][x+1] = LeavesBlock(x+1, y-height)
    self[y-height][x+2] = LeavesBlock(x+2, y-height)
    self[y-height-1][x-1] = LeavesBlock(x-1, y-height-1)
    self[y-height-1][x] = LeavesBlock(x, y-height-1)
    self[y-height-1][x+1] = LeavesBlock(x+1, y-height-1)
    self[y+1][x] = DirtBlock(x, y+1)
    
  
  def hoveredBlock(self) -> Block:
    mousepos = pg.mouse.get_pos()
    return self.blockAt(*pixelToCoord(*mousepos))

  def blockAt(self, x, y) -> Block:
    return self[y][x]

  def __getitem__(self, x: int):
    return self.array[x]
  
  def topBlock(self, x) -> Block:
    for i in range(0, WORLD_HEIGHT-1):
      if not self[i][x].isAir:
        return self[i][x]
  
  def getVisibleBlocks(self):
    self.visibleBlocks = [
      [(self[y][x], self.back[y][x], self.lightmap[y][x]) for x in range(player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1)]
            for y in range(player.camera.top // BLOCK_SIZE,
              (player.camera.bottom // BLOCK_SIZE) + 1)
    ]

  def draw(self):
    for row in self.visibleBlocks:
      for blockTuple in row:
        block, backBlock, light = blockTuple
        if not backBlock.isAir and block.isEmpty:
          backBlock.drawBlock()
        if not block.isAir:
          block.drawBlock()
        pg.draw.rect(SUNLIGHTSURF, (0,0,0,light), relativeRect(block.rect))
  
  def buildEdgePool(self):
    self.edgePool.clear()
    self.vertices.clear()
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
          self[y][x].edgeExist[j] = False
    
    for y in range(
        player.camera.top // BLOCK_SIZE,
        (player.camera.bottom // BLOCK_SIZE) + 1
    ):
      for x in range(
          player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1,
      ):
        cur = self[y][x]
        if not cur.isAir:
          # west
          if x-1 >= 0 and self[y][x-1].isAir:
            if y-1 >= 0 and self[y-1][x].edgeExist[Direction.WEST] and self[y-1][x].edgeId[Direction.WEST]<len(self.edgePool):
              # print("edge exists")
              self.edgePool[self[y-1][x].edgeId[Direction.WEST]].ey += 1
              # print(self.edgePool[self[y-1][x].edgeId[Direction.WEST]])
              cur.edgeId[Direction.WEST] = self[y-1][x].edgeId[Direction.WEST]
              cur.edgeExist[Direction.WEST] = True
            else:
              edge = Edge(x, y, x, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[Direction.WEST] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[Direction.WEST] = True
          # east
          if x+1 < (player.camera.right // BLOCK_SIZE) + 1 and self[y][x+1].isAir and self[y-1][x].edgeId[Direction.EAST]<len(self.edgePool):
            if y-1 >= 0 and self[y-1][x].edgeExist[Direction.EAST]:
              self.edgePool[self[y-1][x].edgeId[Direction.EAST]].ey += 1
              cur.edgeId[Direction.EAST] = self[y-1][x].edgeId[Direction.EAST]
              cur.edgeExist[Direction.EAST] = True
            else:
              edge = Edge(x+1, y, x+1, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[Direction.EAST] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[Direction.EAST] = True
          # north
          if y-1 >= 0 and self[y-1][x].isAir:
            if x-1 >= 0 and self[y][x-1].edgeExist[Direction.NORTH] and self[y][x-1].edgeId[Direction.NORTH]<len(self.edgePool):
              self.edgePool[self[y][x-1].edgeId[Direction.NORTH]].ex += 1
              cur.edgeId[Direction.NORTH] = self[y][x-1].edgeId[Direction.NORTH]
              cur.edgeExist[Direction.NORTH] = True
            else:
              edge = Edge(x, y, x+1, y)
              edgeId = len(self.edgePool)
              cur.edgeId[Direction.NORTH] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[Direction.NORTH] = True
          # south
          if y+1 < player.camera.bottom // BLOCK_SIZE + 1 and self[y+1][x].isAir and self[y][x-1].edgeId[Direction.SOUTH]<len(self.edgePool):
            if x-1 >= 0 and self[y][x-1].edgeExist[Direction.SOUTH]:
              self.edgePool[self[y][x-1].edgeId[Direction.SOUTH]].ex += 1
              cur.edgeId[Direction.SOUTH] = self[y][x-1].edgeId[Direction.SOUTH]
              cur.edgeExist[Direction.SOUTH] = True
            else:
              edge = Edge(x, y+1, x+1, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[Direction.SOUTH] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[Direction.SOUTH] = True
    for i in range(len(self.edgePool)):
      self.vertices.add(relativeCoord(self.edgePool[i].x*BLOCK_SIZE,self.edgePool[i].y*BLOCK_SIZE))
      self.vertices.add(relativeCoord(self.edgePool[i].ex*BLOCK_SIZE,self.edgePool[i].ey*BLOCK_SIZE))
      self.edgePool[i].draw()

  def generateLight(self, originr=None, originc=None):
    '''Generate lightmap for the entire world or specific part of world'''
    if originr is None and originc is None: startTime = time.time()
    blockMap = [
      [False if not self[y][x].isEmpty or not self.back[y][x].isEmpty else True for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)]
    
    if originr is None and originc is None:
      startr = startc = 0
      stopr = WORLD_HEIGHT
      stopc = WORLD_WIDTH
    else:
      startr = max(originr - 6, 0)
      startc = max(originc - 6, 0)
      stopr = min(originr + 7, WORLD_HEIGHT)
      stopc = min(originc + 7, WORLD_WIDTH)
    
    # loop over every block in the world
    for r in range(startr, stopr):
      for c in range(startc, stopc):
        # make queue to perform breadth first search to calculate the light at the block at row r and col c
        bfs = Queue()
        bfs.add((c, r)) # c is x and r is y
        bfs.add(None) # use Nones to track the level of the bfs
        level = 0 # keep track of level of bfs
        # set to store visited coordinates
        visited = set()
        visited.add((c, r))
        
        while bfs:
          
          if level > 6:
            self.lightmap[r][c] = 255
            break # exit after traversing 5 levels
          
          cur = bfs.poll()
          if cur is None:
            level += 1
            bfs.add(None)
            if bfs.peek is None: break
            else: continue
          
          x, y = cur
          
          if blockMap[y][x]:
            self.lightmap[r][c] = max(0, (level - 1) * 51)
            break
          
          # left block
          if x - 1 >= 0: # if block is inside world bounds
            new = (x - 1, y)
            if new not in visited: # if block has not been checked
              visited.add(new)
              bfs.add(new)

          # right block
          if x + 1 < WORLD_WIDTH: # if block is inside world bounds
            new = (x + 1, y)
            if new not in visited: # if block has not been checked
              visited.add(new)
              bfs.add(new)

          # upper block
          if y - 1 >= 0: # if block is inside world bounds
            new = (x, y - 1)
            if new not in visited: # if block has not been checked
              visited.add(new)
              bfs.add(new)
          
          # lower block
          if y + 1 < WORLD_HEIGHT: # if block is inside world bounds
            new = (x, y + 1)
            if new not in visited: # if block has not been checked
              visited.add(new)
              bfs.add(new)
    
    if originr is None and originc is None:
      endTime = time.time()
      print("lightmap time:", round(endTime - startTime, 2))
    
  def update(self):
    self.getVisibleBlocks()
    self.draw()
    # self.buildEdgePool()
    
    self.visibleBlocks.clear()
    
    
'''Menu stuff'''
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        
        self.hover_animation = 0
        self.press_animation = 0
        self.is_pressed = False
        
        self.base_colour = (45, 45, 45)
        self.hover_colour = (75, 75, 75)
        
        #Corner roundness
        self.corner_radius = 15
        
    def update(self, mouse_pos):
        #Hover animation
        target_hover = 1 if self.rect.collidepoint(mouse_pos) else 0
        self.hover_animation += (target_hover - self.hover_animation) * 0.15
        
        #Click animation
        if self.is_pressed:
            self.press_animation += (1 - self.press_animation) * 0.2
        else:
            self.press_animation += (0 - self.press_animation) * 0.2
        
    def handle_event(self, event, mouse_pos):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.is_pressed = False
        
    def draw(self, font, text_colour, shadow_colour):
        current_color = [int(self.base_colour[i] + (self.hover_colour[i] - self.base_colour[i]) * self.hover_animation) for i in range(3)]
        
        hover_offset = int(self.hover_animation * 3)
        press_offset = int(self.press_animation * 2)
        button_rect = self.rect.copy()
        button_rect.y -= hover_offset - press_offset
        
        self._draw_button(button_rect, current_color)
        self._draw_text(font, text_colour, shadow_colour, button_rect)
        
    def _draw_button(self, button_rect, colour):
        # Draw shadow first
        shadow_rect = button_rect.copy()
        shadow_rect.y += 4
        pg.draw.rect(SURF, (0, 0, 0, 64), shadow_rect, border_radius=self.corner_radius)
        
        #Base button
        button_surface = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        pg.draw.rect(button_surface, colour, button_surface.get_rect(), border_radius=self.corner_radius)
        
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
        
    def _draw_text(self, font, text_colour, shadow_color, button_rect):
        #Scale text with the hover animation
        scale_factor = 1 + self.hover_animation * 0.05
        
        text_surf = font.render(self.text, True, text_colour)
        text_surf = pg.transform.scale(text_surf, (int(text_surf.get_width() * scale_factor), int(text_surf.get_height() * scale_factor)))
        text_rect = text_surf.get_rect(center=button_rect.center)
        
        #Text shadow
        shadow_surf = font.render(self.text, True, shadow_color)
        shadow_surf = pg.transform.scale(shadow_surf, (int(shadow_surf.get_width() * scale_factor), int(shadow_surf.get_height() * scale_factor)))
        shadow_rect = shadow_surf.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        
        SURF.blit(shadow_surf, shadow_rect)
        SURF.blit(text_surf, text_rect)

class MainMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        
        self._createButtons()

        self.buttonFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 36)
        self.splashFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 28)
        
        self.buttonTextColour = (240, 240, 240)
        self.textShadow = (20, 20, 20, 160)
        
        #Background
        self.bgPanorama = pg.image.load("title screen background animation.jpg").convert()
        
        self.overlay = pg.Surface((self.width, self.height))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(40)
        
        self.bgScrollSpeed = 20
        self.bgOffset = 0
        
        #Title
        self.titleImage = pg.image.load("title screen title.png").convert_alpha()
        self.titleImageRect = self.titleImage.get_rect(center=(self.width // 2, self.height // 4))
        
        #Splash text stuff
        self.splashTexts = [
            "Dont sue us Minecraft!",
            "Made with Pygame!",
            "Lorem ipsum!",
            "Pygame >",
        ]
        
        self.currentSplash = random.choice(self.splashTexts)
        self.splashAngle = -15
        self.splashWaveOffset = 0
        self.splashScale = 1.0
        
    def _createButtons(self):
        buttonWidth, buttonHeight = 400, 50
        buttonX = (self.width - buttonWidth) // 2
        spacing = 24  #space between buttons
        startY = self.height // 2
        
        self.buttons = {
            'play': Button(buttonX, startY, buttonWidth, buttonHeight, "Play"),
            'instructions': Button(buttonX, startY + buttonHeight + spacing, buttonWidth, buttonHeight, "Instructions"),
            'options': Button(buttonX, startY + (buttonHeight + spacing) * 2, buttonWidth, buttonHeight, "Options"),
            'quit': Button(buttonX, startY + (buttonHeight + spacing) * 3, buttonWidth, buttonHeight, "Quit")
        }
        
    def _updateBackground(self, time):
        self.bgOffset = (self.bgOffset + self.bgScrollSpeed * time / 1000.0) % self.bgPanorama.get_width()

    def _draw(self):
        #Draw background
        self.screen.blit(self.bgPanorama, (-self.bgOffset, 0))
        self.screen.blit(self.bgPanorama, (self.bgPanorama.get_width() - self.bgOffset, 0))
        self.screen.blit(self.overlay, (0, 0))
        
        #Title
        self.screen.blit(self.titleImage, self.titleImageRect)
        
        #Splash text
        self.splashWaveOffset += 0.03
        self.splashScale = 1.0 + math.sin(self.splashWaveOffset * 0.5) * 0.03  #subtle pulse
        
        splashSurf = self.splashFont.render(self.currentSplash, True, (255, 255, 0))
        splashSurf = pg.transform.rotate(splashSurf, self.splashAngle)
        splashSurf = pg.transform.scale(splashSurf, 
                                       (int(splashSurf.get_width() * self.splashScale),
                                        int(splashSurf.get_height() * self.splashScale)))
        
        splashYOffset = math.sin(self.splashWaveOffset) * 6
        splashPos = (self.width // 2 + 180, self.height // 4 + splashYOffset)
        self.screen.blit(splashSurf, splashPos)
        
        for button in self.buttons.values():
            button.draw(self.buttonFont, self.buttonTextColour, self.textShadow)

    def run(self):
        clock = pg.time.Clock()
        
        while True:
            mousePos = pg.mouse.get_pos()           
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sysexit()
                    
                if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                    for button in self.buttons.values():
                        button.handle_event(event, mousePos)

                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if self.buttons['play'].rect.collidepoint(mousePos):
                        return
                    elif self.buttons['instructions'].rect.collidepoint(mousePos):
                        pass
                    elif self.buttons['options'].rect.collidepoint(mousePos):
                        pass
                    elif self.buttons['quit'].rect.collidepoint(mousePos):
                        sysexit()

            for button in self.buttons.values():
                button.update(mousePos)
            
            self._updateBackground(clock.get_time())
            self._draw()
            
            pg.display.flip()
            clock.tick(FPS)
    
#TODO work on these later hopefully        
def instructionsScreen():
  pass
          
def changeKeybinds():
    pass
  
class PauseScreen:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.screen = pg.display.set_mode((width, height))

    self.buttonFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 36)
   
    self.buttonTextColour = (240, 240, 240)
    self.textShadow = (20, 20, 20, 160)
    
    resumeButton = Button((self.width - 400) // 2, self.height // 2,  400, 50, "Back to Game")
    quitButton = Button((self.width - 400) // 2, (self.height // 2) + 100, 400, 50, "Save and Quit") 

  
  def run(self):
    clock = pg.time.Clock()
    white = (255, 255, 255)
    SURF.fill(white)
    
    while True:
      mousePos = pg.mouse.get_pos()           
      for event in pg.event.get():
          if event.type == pg.QUIT:
              sysexit()
              
      pg.display.flip()
      clock.tick(FPS)

class LoadingScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        
        self.font = pg.font.Font("MinecraftRegular-Bmg3.otf", 20)
        self.titleFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 40)

        self.current_step = "Initializing world..."
        
        self.currentMessage = 0
        self.messageChangeTimer = time.time()
        self.messageChangeInterval = 1.5    #seconds
        self.progress = 0.0
        self.startTime = time.time()

        self.barWidth = 400
        self.barHeight = 20
        self.barX = (width - self.barWidth) // 2
        self.bar_y = height // 2 + 30
        
    def update(self, progress, current_step):
        self.progress = progress
        self.current_step = current_step

    def draw(self):
        self.screen.fill((25, 25, 25))

        title = self.titleFont.render("Loading world...", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title, title_rect)

        #Loading message
        message = self.font.render(self.current_step, True, (200, 200, 200))
        message_rect = message.get_rect(center=(self.width // 2, self.height // 2 - 20))
        self.screen.blit(message, message_rect)

        #Progress bar
        pg.draw.rect(self.screen, (50, 50, 50), (self.barX, self.bar_y, self.barWidth, self.barHeight))
        fill_width = int(self.barWidth * self.progress)
        pg.draw.rect(self.screen, (106, 176, 76), (self.barX, self.bar_y, fill_width, self.barHeight))

        #Percentage
        percentage = f"{int(self.progress * 100)}%"
        percent_text = self.font.render(percentage, True, (255, 255, 255))
        percent_rect = percent_text.get_rect(center=(self.width // 2, self.bar_y + 40))
        self.screen.blit(percent_text, percent_rect)

        #Elapsed load time
        elapsed_time = time.time() - self.startTime
        elapsed_text = self.font.render(f"Time elapsed: {elapsed_time:.1f} seconds", True, (200, 200, 200))
        elapsed_rect = elapsed_text.get_rect(center=(self.width // 2, self.bar_y + 120))
        self.screen.blit(elapsed_text, elapsed_rect)

        pg.display.flip()
        clock.tick(FPS)

class ThreadedWorldLoader:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.loading_screen = LoadingScreen(width, height)
        self.world = None
        self.progress = 0.0
        self.progress_updates = Queue()
        self.generation_complete_event = threading.Event()
        self.generation_thread = None

        self.generation_steps = [
            ("Initializing world", 0.1),
            ("Generating terrain", 0.3),
            ("Creating caves", 0.2),
            ("Growing trees", 0.2),
            ("Placing ores", 0.2)
        ]
        self.current_step = ""
        
    def _update_progress(self, step, step_progress):
        step_index = next((i for i, (s, _) in enumerate(self.generation_steps) if s == step), -1)
        if step_index == -1:
            return
        
        completed_progress = sum(weight for _, weight in self.generation_steps[:step_index])
        current_step_progress = self.generation_steps[step_index][1] * step_progress
        total_progress = completed_progress + current_step_progress
        
        self.progress_updates.add(total_progress)
        self.current_step = step

    def _generate_world(self):
        try:
            self._update_progress("Initializing world", 0.0)
            # time.sleep(0.5)
            self._update_progress("Initializing world", 1.0)
            
            self.world = World()
            
            for step, _ in self.generation_steps[1:]:
                self._update_progress(step, 0.0)
                # time.sleep(1.0)
                self._update_progress(step, 1.0)
            
            self.generation_complete_event.set()
        except Exception as e:
            print(f"Error during world generation: {e}")
            self.generation_complete_event.set()

    def start_generation(self):
        """Starts the world generation in a background thread"""
        self.generation_thread = threading.Thread(target=self._generate_world, daemon=True)
        self.generation_thread.start()

    def update(self):
      while self.progress_updates:
          self.progress = self.progress_updates.poll()
      
      self.loading_screen.update(self.progress, self.current_step)
      self.loading_screen.draw()
      
      return self.generation_complete_event.is_set()
        

'''Main Loop'''
if __name__ == "__main__":
  SUNLIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  LIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  FRAME = SURF.get_rect()
  ASURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  ASURF.fill((0, 0, 0, 0))
  
  #Give player items at the beginning of the game
  defaultItems = [IronPickaxe(), IronAxe(), StoneAxe(), WoodenShovel(), CraftingTableItem()] + [CobbleStoneItem() for _ in range(192)] + [TorchItem() for _ in range(64)]
  
  MainMenu(WIDTH, HEIGHT).run()
  
  loader = ThreadedWorldLoader(WIDTH, HEIGHT)
  loader.start_generation()
  start_time = time.time()

  while True:
      for event in pg.event.get():
          if event.type == pg.QUIT:
              sysexit()
      
      if loader.update():
          if not loader.generation_thread.is_alive():
              break
  
  world = loader.world
  end_time = time.time()
  print(f"World generation time: {end_time - start_time:.2f} seconds")
  
  font = pg.font.Font(None, 15)
  font20 = pg.font.Font(None, 20)
  
  player = Player()
  world = loader.world
  sun = Sun()

  
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
        sysexit()
      elif event.type == 101:
        print("fps: ", round(clock.get_fps(), 2))    
        
      elif event.type == KEYDOWN and event.key == pg.K_ESCAPE:
        PauseScreen(WIDTH, HEIGHT).run()
        
      elif event.type == KEYDOWN and event.key == pg.K_e:
        check_for_interaction()
      elif event.type == KEYDOWN and event.key == pg.K_m:
        pixel = tuple(map(lambda a: BLOCK_SIZE*a,pixelToCoord(*pg.mouse.get_pos())))
        # print(pixel, world.mask.get_at(pixel), world.blockAt(*pixelToCoord(*pg.mouse.get_pos())).rect.topleft)
        
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