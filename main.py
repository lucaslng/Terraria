import math
import random
import time
import threading          #pickle stores game data onto system
import pygame as pg
from pygame.locals import QUIT, KEYDOWN
from pygame.math import Vector2

#Import code from other files
# from blocks import *
# from block_item_registry import *
from blocks.executable import Executable
from blocks.interactable import Interactable
from constants import WIDTH, HEIGHT, BLOCK_SIZE, WORLD_HEIGHT, WORLD_WIDTH, SURF, SUNLIGHTSURF, FPS, font20, gravity, BIG, SEED, clock
from customqueue import Queue
# from entities import *
# from inventory import *
# from items import *
# from light import *
# from menus import *
from sprites import sprites
# from utils import *
# from world import *
from utils.direction import NORTH, EAST, SOUTH, WEST
from utils.utils import sysexit
from abc import ABC
from dataclasses import dataclass
# from typing import 
from enum import Enum


start = time.time()

pg.init()
pg.font.init()

def coordWorld2Pixel(x: int, y: int) -> tuple[int, int]:
  '''convert world coordinates to pixel'''
  return x * BLOCK_SIZE, y * BLOCK_SIZE

def rectWorld2Pixel(rect: pg.rect.Rect) -> pg.rect.Rect:
  '''convert world rect to pixel rect'''
  return pg.rect.Rect(rect.left * BLOCK_SIZE, rect.top * BLOCK_SIZE, rect.width * BLOCK_SIZE, rect.height * BLOCK_SIZE)

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

def bresenham(x0: int, y0: int, x1: int, y1: int, quality: int=1):
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
      blockTouched = world.blockAt(*player.pixelToCoord(x, y))
      if not blockTouched.isAir:
        return x, y
      if d > 0:
        y += yi
        d += 2 * (dy - dx)
      else:
        d += 2 * dy
      x += xi
      if not 0 <= x < WIDTH or not 0 <= y < HEIGHT:
        return pointsTouched
      nextBlock = world.blockAt(*player.pixelToCoord(x, y))
      if not nextBlock.isAir:
        xi = xii
        yi = yii
    return None

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
      blockTouched = world.blockAt(*player.pixelToCoord(x, y))
      if not blockTouched.isAir:
        return x, y
      if d > 0:
        x += xi
        d += 2 * (dx - dy)
      else:
        d += 2 * dx
      y += yi
      if not 0 <= x < WIDTH or not 0 <= y < HEIGHT:
        return pointsTouched
      nextBlock = world.blockAt(*player.pixelToCoord(x, y))
      if not nextBlock.isAir:
        xi = xii
        yi = yii
    return None

  if abs(y1 - y0) < abs(x1 - x0):
    return plotLineLow(x0, y0, x1, y1)
  else:
    return plotLineHigh(x0, y0, x1, y1)

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
      # print(self.x, self.y, self.x*20, self.y*20, player.coordWorld2Relative(self.x, self.y))
      pg.draw.circle(SUNLIGHTSURF, (0,0,0,0), player.coordWorld2Relative(self.x,self.y), self.lightRadius)
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
    if self.isAir:
      self.mask.clear()
    self.edgeExist = [False for _ in range(4)]
    self.edgeId = [0 for _ in range(4)]
    
    if self.isBack and not self.isAir:
      self.texture.blit(self.BACK_TINT, (0,0))

  def drawBlockOutline(self, color: pg.color.Color):
    pg.draw.rect(ASURF, color, player.relativeRect(self.rect), 2)

  def drawBlock(self):
    SURF.blit(self.texture, player.relativeRect(self.rect))
    breakingRect = player.relativeRect(self.rect.copy())
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
      # pg.draw.rect(SURF, (255, 0, 0), player.relativeRect(self.rect), width=3)
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
    Block.__init__(self, name="Crafting Table", texture=self.craftingTableTexture, x=x, y=y, hardness=2.5, blockType=BlockType.AXE, isBack=isBack)
  
  def interact(self):
    pass
class CraftingTableItem(PlaceableItem):
  texture = pg.transform.scale(pg.image.load("crafting_table.png"), (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Crafting Table", self.texture, 64)

class DirtVariant:
  def __init__(self, name: str, texture):
    self.name = name
    self.texture = texture
class DirtVariantDirt(DirtVariant):
  dirtTexture = pg.transform.scale(sprites["dirt"], (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(self):
    super().__init__("Dirt", self.dirtTexture)
class DirtVariantGrass(DirtVariant):
  grassTexture = pg.transform.scale(sprites["grass"], (BLOCK_SIZE, BLOCK_SIZE))
  grassItemTexture = pg.transform.scale(sprites["grass"], (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Grass Block", self.grassTexture)
class DirtBlock(Block):
  def __init__(self, x, y, variant: DirtVariant = DirtVariantDirt(), isBack=False):
    super().__init__(variant.name, variant.texture, x, y, 1.5, BlockType.SHOVEL, isBack=isBack) 
    self.variant = variant.name.lower()
class DirtItem(PlaceableItem):
  dirtItemTexture = pg.transform.scale(sprites["dirt"], (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Dirt", self.dirtItemTexture, 64)
    
class OakLogBlock(Block):
    oakLogTexture = pg.transform.scale(sprites["oak log"], (BLOCK_SIZE, BLOCK_SIZE))
    def __init__(self, x, y, isBack=False):
        super().__init__("Oak Log", self.oakLogTexture, x, y, 2.5, BlockType.AXE, isBack=isBack)
class OakLogItem(PlaceableItem):
    oakLogItemTexture = pg.transform.scale(sprites["oak log"], (Item.SIZE, Item.SIZE))
    def __init__(self):
        super().__init__("Oak Log", self.oakLogItemTexture, 64)

class LeavesBlock(Block):
    oakLeavesTexture = pg.transform.scale(sprites["oak leaves"], (BLOCK_SIZE, BLOCK_SIZE))
    def __init__(self, x, y, isBack=False):
        super().__init__("Leaves", self.oakLeavesTexture, x, y, 1, BlockType.SHEARS, isBack=isBack)

class StoneBlock(Block):
  stoneTexture = pg.transform.scale(sprites["stone"], (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(self, x, y, isBack=False):
    super().__init__("Stone", self.stoneTexture, x, y, 5, BlockType.PICKAXE, isBack=isBack)
class CobblestoneBlock(Block):
  cobblestoneTexture = pg.transform.scale(sprites["cobblestone"], (BLOCK_SIZE, BLOCK_SIZE))
  def __init__(self, x, y, isBack=False):
    super().__init__("Cobblestone", self.cobblestoneTexture, x, y, 5.5, BlockType.PICKAXE, isBack=isBack)
class CobbleStoneItem(PlaceableItem):
  cobblestoneItemTexture = pg.transform.scale(sprites["cobblestone"], (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Cobblestone", self.cobblestoneItemTexture, 64)


class Generated(ABC):
  '''Things that can be generated by simplex noise'''
  veinSize: int
  rarity: int
  
class IronOreBlock(Block, Generated):
  ironOreTexture = pg.transform.scale(sprites["ironOre"], (BLOCK_SIZE, BLOCK_SIZE))
  veinSize = 3.2
  rarity = 0.38
  def __init__(self, x, y, isBack=False):
    Block.__init__(self, "Iron Ore", self.ironOreTexture, x, y, 6, BlockType.PICKAXE, isBack=isBack)
class IronOreItem(PlaceableItem):
  ironOreItemTexture = pg.transform.scale(sprites["ironOre"], (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Iron Ore", self.ironOreItemTexture, 64)

class CoalOreBlock(Block, Generated):
  coalTexture = pg.transform.scale(sprites["coalOre"], (BLOCK_SIZE, BLOCK_SIZE))
  veinSize = 3.9
  rarity = 0.3
  def __init__(self, x, y, isBack=False):
    Block.__init__(self, "Coal Ore", self.coalTexture, x, y, 3, BlockType.PICKAXE, isBack=isBack)
class CoalItem(Item):
  coalItemTexture = pg.transform.scale(sprites["coal"], (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Coal", self.coalItemTexture, 64)

ores = {CoalOreBlock, IronOreBlock}

class TorchBlock(Block, Light):
  torchTexture = pg.transform.scale(sprites["torch"].convert_alpha(), (BLOCK_SIZE,BLOCK_SIZE))
  def __init__(self, x, y, isBack=False):
    Block.__init__(self, "Torch", self.torchTexture, x, y, 1, BlockType.NONE, isEmpty=True, isBack=isBack)
    Light.__init__(self, 100, x, y)
    lights.append(self)
class TorchItem(PlaceableItem, Executable):
  torchItemTexture = pg.transform.scale(sprites["torch"].convert_alpha(), (Item.SIZE, Item.SIZE))
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
  item: Item | None = None
  count: int = 0
  isActive = False
  size = 40
  
  def clear(self):
    '''reset/clear the slot'''
    self.item = None
    self.count = 0

  def draw(self, x: float, y: float, size: float = size, transparent=False) -> None:
    if not transparent:
      pg.draw.rect(OVERLAY, (200, 200, 200), (x, y, size, size))
    else:
      pg.draw.rect(OVERLAY, (200, 200, 200, 160), (x, y, size, size))
      
    if self.isActive:
      pg.draw.rect(OVERLAY, (0, 0, 0), (x, y, size, size), 2)
    else:
      pg.draw.rect(OVERLAY, (90, 90, 90), (x, y, size, size), 2)

    if self.item:
      texture = pg.transform.scale(self.item.texture, (size - 6, size - 6))
      
      #center texture in the slot
      textureRect = texture.get_rect()
      textureRect.center = (x + size / 2, y + size / 2)
      OVERLAY.blit(texture, textureRect.topleft)

      if self.count > 1:
        count_text = font20.render(str(self.count), True, (255, 255, 255))
        
        #item counter in the bottom right of the slot
        text_rect = count_text.get_rect(topleft=textureRect.center)
        OVERLAY.blit(count_text, text_rect.topleft)
        
      #Draw durability bar
      if self.item.isTool() and self.item.durability != self.item.startingDurability:
        barHeight = 3
        barWidth = size - 4
        barx = x + 2
        bary = y + size - barHeight - 1
        
        tool: Tool = self.item
        durabilityPercent = tool.durability / tool.startingDurability
        
        if durabilityPercent > 0.6:
          colour = (0, 255, 0)
        elif durabilityPercent > 0.3:
          colour = (255, 165, 0)
        else:
          colour = (255, 0, 0)
        
        pg.draw.rect(OVERLAY, (50, 50, 50), (barx, bary, barWidth, barHeight))
        pg.draw.rect(OVERLAY, colour, (barx, bary, int(barWidth * durabilityPercent), barHeight))

  def drawBare(self, x: float, y: float, size: float = size):
    '''draw without the box around it, just the item and the number, location is the center instead of topleft'''
    if self.item:
      texture = pg.transform.scale(self.item.texture, (size - 6, size - 6))
    
      #center texture in the slot
      textureRect = texture.get_rect()
      textureRect.center = x, y
      OVERLAY.blit(texture, textureRect.topleft)

      if self.count > 1:
        count_text = font20.render(str(self.count), True, (255, 255, 255))
        
        #item counter in the bottom right of the slot
        text_rect = count_text.get_rect(topleft=textureRect.center)
        OVERLAY.blit(count_text, text_rect.topleft)       
        
        
@dataclass
class Section:
  rows: int
  cols: int
  x: float
  y: float
  slotSize: int = 40
  
  def __post_init__(self):
    self.array = [[Slot() for _ in range(self.cols)] for _ in range(self.rows)]
    self.rect = pg.Rect(self.x, self.y, self.x + self.cols * self.slotSize, self.y + self.rows * self.slotSize)
    
  def __getitem__(self, i: int) -> list[Slot]:
    return self.array[i]
  
  def isHovered(self) -> bool:
    return self.rect.collidepoint(*pg.mouse.get_pos())
  
  def hoveredSlot(self):
    '''returns the location of the slot that is hovered in a tuple (r, c)'''
    for r in range(self.rows):
      for c in range(self.cols):
        slotRect = pg.Rect(self.x + c * self.slotSize, self.y + r * self.slotSize, self.slotSize, self.slotSize)
        if slotRect.collidepoint(*pg.mouse.get_pos()):
          pg.draw.rect(SURF, (0,0,0), slotRect, 4)
          return r, c
    return None
  
  def draw(self, transparent=False) -> None:
    for r in range(self.rows):
      for c in range(self.cols):
        self[r][c].draw(self.x+c*self.slotSize, self.y+r*self.slotSize, size = self.slotSize, transparent=transparent)
        
class Menu:
  '''A menu is effectively a list of Sections. One section is an array of Slots.'''
  def __init__(self, *args: Section, isActive: bool = False):
    self.isActive = isActive
    self.sections = [args[i] for i in range(len(args))]
    minx = miny = BIG
    maxx = maxy = 0
    for section in self.sections:
      minx = min(minx, section.x)
      miny = min(miny, section.y)
      maxx = max(maxx, section.x + section.cols * section.slotSize)
      maxy = max(maxy, section.y + section.rows * section.slotSize)
    self.rect = pg.Rect(minx, miny, maxx - minx, maxy - miny)
    self.hoveredSlot: None | tuple[int, tuple[int, int] | None] = None
  
  def draw(self, transparent=False) -> None:
    for section in self.sections:
      section.draw(transparent=transparent)
  
  def isHovered(self) -> bool:
    return self.rect.collidepoint(*pg.mouse.get_pos())
  
  def getHoveredSlot(self):
    '''
    returns the location of the hovered slot in a tuple \n
    the 0th index is the section index within the menu \n
    the 1st index is the location of the slot in the section in a tuple (r, c)
    '''
    
    if self.isHovered():
      for i in range(len(self.sections)):
        section = self.sections[i]
        if section.isHovered():
          self.hoveredSlot = i, section.hoveredSlot()
          return
    self.hoveredSlot = None
  
  def pickUpItem(self):
    if self.hoveredSlot:
      sectionid, location = self.hoveredSlot
      r, c = location
      player.cursorSlot, self.sections[sectionid][r][c] = self.sections[sectionid][r][c], player.cursorSlot
  
  def __getitem__(self, i: int):
    return self.sections[i]
  
  def __len__(self):
    return len(self.sections)
      

@dataclass
class Inventory:
  """Inventory class"""
  rows: int
  cols: int
  menux: int
  menuy: int
  
  def __post_init__(self):
    self.menu = Menu(Section(self.rows, self.cols, self.menux, self.menuy))

  def addItem(self, item: Item) -> bool:
    """Attempts to add an item to the inventory"""
    #add item to stack with existing items
    for r in range(self.rows):
        for c in range(self.cols):
            slot = self.menu[0][r][c]
            if slot.item and slot.item == item and slot.count < slot.item.stackSize:
                slot.count += 1
                self.menu.draw()
                return True
                
    #find first empty slot if there isn't an existing slot
    for r in range(self.rows):
        for c in range(self.cols):
            slot = self.menu[0][r][c]
            if slot.item is None:
                slot.item = item
                slot.count = 1
                #print('added to inventory')
                self.menu.draw()
                return True
                
    return False  #inventory full

  def isPlaceable(self) -> bool:
    return isinstance(self, PlaceableItem)
  
  def draw(self, transparent=True): # notice that default is True here for transparency
    self.menu.draw(transparent=transparent)

  def __getitem__(self, row: int):
    return self.menu[0][row]


@dataclass
class Tool(Item):
  speed: float
  startingDurability: int
  blockType: BlockType
  
  def __post_init__(self):
    self.durability = self.startingDurability

class Shears(Tool):
  shearsTexture = pg.transform.scale(sprites["shears"], (Item.SIZE, Item.SIZE))
  def __init__(self):
    super().__init__("Shears", self.shearsTexture, 1, 1.5, 238, BlockType.SHEARS)
    
'''Wooden'''
class WoodenPickaxe(Tool):
  woodenPickaxeTexture = pg.transform.scale(sprites["woodenPickaxe"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Wooden Pickaxe", self.woodenPickaxeTexture, 1, 1.5, 59, BlockType.PICKAXE)  
class WoodenAxe(Tool):
  woodenAxeTexture = pg.transform.scale(sprites["woodenAxe"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Wooden Axe", self.woodenAxeTexture, 1, 1.5, 59, BlockType.AXE)
class WoodenShovel(Tool):
  woodenShovelTexture = pg.transform.scale(sprites["woodenShovel"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Wooden Shovel", self.woodenShovelTexture, 1, 1.5, 59, BlockType.SHOVEL)
class WoodenSword(Tool):
  woodenSwordTexture = pg.transform.scale(sprites["woodenSword"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Wooden Sword", self.woodenSwordTexture, 1, 1, 59, BlockType.SWORD)
    
'''Stone'''
class StonePickaxe(Tool):
  stonePickaxeTexture = pg.transform.scale(sprites["stonePickaxe"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Stone Pickaxe", self.stonePickaxeTexture, 1, 3, 131, BlockType.PICKAXE)
class StoneAxe(Tool):
  stoneAxeTexture = pg.transform.scale(sprites["stoneAxe"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Stone Axe", self.stoneAxeTexture, 1, 2.5, 131, BlockType.AXE)
class StoneShovel(Tool):
  stoneShovelTexture = pg.transform.scale(sprites["stoneShovel"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Stone Shovel", self.stoneShovelTexture, 1, 2.5, 131, BlockType.SHOVEL)
class StoneSword(Tool):
  stoneSwordTexture = pg.transform.scale(sprites["stoneSword"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Stone Sword", self.stoneSwordTexture, 1, 1, 131, BlockType.SWORD)
    
'''Iron'''
class IronPickaxe(Tool):
  ironPickaxeTexture = pg.transform.scale(sprites["ironPickaxe"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Iron Pickaxe", self.ironPickaxeTexture, 1, 5, 250, BlockType.PICKAXE)
class IronAxe(Tool):
  ironAxeTexture = pg.transform.scale(sprites["ironAxe"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Iron Axe", self.ironAxeTexture, 1, 3.5, 250, BlockType.AXE)
class IronShovel(Tool):
  ironShovelTexture = pg.transform.scale(sprites["ironShovel"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Iron Shovel", self.ironShovelTexture, 1, 3.5, 250, BlockType.SHOVEL)
class IronSword(Tool):
  ironSwordTexture = pg.transform.scale(sprites["ironSword"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Iron Sword", self.ironSwordTexture, 1, 1, 250, BlockType.SWORD)  

'''Gold'''
class GoldPickaxe(Tool):
  goldPickaxeTexture = pg.transform.scale(sprites["goldPickaxe"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Gold Pickaxe", self.goldPickaxeTexture, 1, 8.5, 32, BlockType.PICKAXE)
class GoldAxe(Tool):
  goldAxeTexture = pg.transform.scale(sprites["goldAxe"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Gold Axe", self.goldAxeTexture, 1, 7.5, 32, BlockType.AXE)
class GoldShovel(Tool):
  goldShovelTexture = pg.transform.scale(sprites["goldShovel"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Gold Shovel", self.goldShovelTexture, 1, 7.5, 32, BlockType.SHOVEL)
class GoldSword(Tool):
  goldSwordTexture = pg.transform.scale(sprites["goldSword"], (Item.SIZE, Item.SIZE))
  def __init__(self):
      super().__init__("Gold Sword", self.goldSwordTexture, 1, 1, 32, BlockType.SWORD)


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
    # pg.draw.rect(SURF, (0,0,255),player.relativeRect(blockRightTop.rect),3)
    # pg.draw.rect(SURF, (255,0,255),player.relativeRect(blockRightBot.rect),3)
    # pg.draw.rect(SURF, (255,128,128),player.relativeRect(blockLeftBot.rect),3)
    # pg.draw.rect(SURF, (255,0,0),player.relativeRect(blockLeftTop.rect),3)
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
    # pg.draw.rect(SURF, (0,0,0), player.relativeRect(newrect), 2)
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
      SURF.blit(self.reversedTexture, player.relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.reversedTexture)
      self.previousDirection = 0
    elif self.hvelo > 0:
      SURF.blit(self.texture, player.relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.texture)
      self.previousDirection = 1
    elif self.previousDirection:
      SURF.blit(self.texture, player.relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.texture)
    else:
      SURF.blit(self.reversedTexture, player.relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.reversedTexture)

  def update(self) -> None:
    self.move()
    self.draw()


class Player(Entity, HasInventory, Light):
  texture = sprites["cat"]["walk"][0]
  selfSprites = sprites["cat"]
  blockFacing = None
  reach = 4 * BLOCK_SIZE
  
  full_heart_texture = sprites["full heart"]
  half_heart_texture = sprites["half heart"]
  empty_heart_texture = sprites["empty heart"]

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
    self.cursorSlot = Slot()
    
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
    for item in defaultItems:
      self.inventory.addItem(item)

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
      OVERLAY.blit(self.full_heart_texture, (HEART_X_START + i * HEART_SPACING, HEART_Y))   
    #Half hearts
    if half_hearts:
      OVERLAY.blit(self.half_heart_texture,(HEART_X_START + full_hearts * HEART_SPACING, HEART_Y))     
    #Empty hearts
    for i in range(empty_hearts):
      OVERLAY.blit(self.empty_heart_texture,(HEART_X_START +(full_hearts + half_hearts + i) * HEART_SPACING,HEART_Y))

  def draw(self):
    # print(self.vvelo)
    if self.hvelo < 0:
      if self.vvelo < -4:
        self.selfSprites["jump"].drawFrame(*player.relativeRect(self.rect).topleft, 2, flipped=True)
      else:
        self.selfSprites["walk"].drawAnimated(*player.relativeRect(self.rect).topleft, flipped=True)
      self.previousDirection = 0
    elif self.hvelo > 0:
      if self.vvelo < -4:
        self.selfSprites["jump"].drawFrame(*player.relativeRect(self.rect).topleft, 2)
      else:
        self.selfSprites["walk"].drawAnimated(*player.relativeRect(self.rect).topleft)
      self.previousDirection = 1
    elif self.previousDirection:
      self.selfSprites["sit"].drawAnimated(*player.relativeRect(self.rect).topleft)
    else:
      self.selfSprites["sit"].drawAnimated(*player.relativeRect(self.rect).topleft, flipped=True)

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
  
  def pixelToCoord(self, x: float, y: float) -> tuple[int, int]:
    """Returns coordinate based on pixel location"""
    coord = int((x + self.camera.left) // BLOCK_SIZE), int(
        (y + self.camera.top) // BLOCK_SIZE
    )
    return coord
  
  def relativeRect(self, rect: pg.rect.Rect) -> pg.rect.Rect:
    """Returns on screen rect relative to the camera"""
    return pg.rect.Rect(
        rect.x - self.camera.x, rect.y - self.camera.y, rect.width, rect.height
    )
    
  def relativeCoord(self, x: float, y: float) -> tuple[int, int]:
    '''Convert a pixel coordinate relative to the camera. Useful for drawing things and more.'''
    return x - self.camera.x, y - self.camera.y
  
  def coordWorld2Relative(self, x: int, y: int) -> tuple[int, int]:
    '''convert world coordinates to pixel on screen'''
    return self.relativeCoord(*coordWorld2Pixel(x, y))

  def rectWorld2Relative(self, rect: pg.rect.Rect) -> pg.rect.Rect:
    '''convert world rect to relative rect'''
    return self.relativeRect(rectWorld2Pixel(rect))

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
      if not self.previousDirection:
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
            self.heldSlot().clear()
            
        self.usingItem = True
        self.blockFacing.amountBroken += miningSpeed / FPS
      else:
        # print("mined", self.blockFacing.name,
        #       "got", self.blockFacing.item().name)
        # world.mask.erase(world[self.blockFacing.y][self.blockFacing.x].mask, self.blockFacing.rect.topleft)
        world[self.blockFacing.y][self.blockFacing.x] = AirBlock(
            self.blockFacing.x, self.blockFacing.y
        )
        if world.back[self.blockFacing.y][self.blockFacing.x].isAir:
          world.generateLight(self.blockFacing.y, self.blockFacing.x)
        item = self.blockFacing.item()
        
        if self.heldSlot().item and self.heldSlot().item.isTool():
          if self.heldSlot().item.blockType == self.blockFacing.blockType:
            miningSpeed = self.heldSlot().item.speed
            
          self.heldSlot().item.durability -= 1
        
        if item:
          self.inventory.addItem(item())

  def place(self):
    if self.heldSlot().item and self.heldSlot().count > 0 and self.heldSlot().item.isPlaceable():
      x, y = player.pixelToCoord(*pg.mouse.get_pos())
      if world.blockAt(x, y).isAir:
        self.animations["placingBlock"] = 0
        self.heldSlot().item.place(x, y)
        self.heldSlot().count -= 1
        if self.heldSlot().count == 0:
          self.heldSlot().item = None
        if world.back[y][x].isAir:
          world.generateLight(y, x)

  def drawCircle(self):
    pg.draw.circle(ASURF, (0, 0, 0, 120), FRAME.center, BLOCK_SIZE * 4)

  def getBlockFacing(self):
    """Returns the block that the player is facing, if it is in range"""
    blockPixel = bresenham(*pg.mouse.get_pos(), *FRAME.center)
    if blockPixel:
      block = world.blockAt(*player.pixelToCoord(*bresenham(*pg.mouse.get_pos(), *FRAME.center)))
      for vertex in block.vertices:
        if math.dist(player.relativeCoord(*vertex), FRAME.center) < self.reach:
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
    self.inventory.menu.getHoveredSlot()
    self.cursorSlot.drawBare(*pg.mouse.get_pos(), self.inventory.menu[0].slotSize)
  
  def drawHUD(self):
    self.draw_health()
    self.drawHotbar()
    self.inventory.draw()

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
    pg.draw.line(SURF,(0,0,0),player.relativeCoord(self.x*BLOCK_SIZE, self.y*BLOCK_SIZE),player.relativeCoord(self.ex*BLOCK_SIZE, self.ey*BLOCK_SIZE), 3)
    # pg.draw.circle(SURF,(0,255,0),player.relativeCoord(self.x*BLOCK_SIZE,self.y*BLOCK_SIZE), 3)
    # pg.draw.circle(SURF,(0,255,0),player.relativeCoord(self.ex*BLOCK_SIZE,self.ey*BLOCK_SIZE), 3)
  def __repr__(self):
    return str((self.x, self.y, self.ex, self.ey))


class ProgressTracker:
    def __init__(self, callback):
        self.callback = callback
        self.current_step = ""
        
    def update(self, step: str, progress: float):
        self.current_step = str(step)
        self.callback(self.current_step, progress)

class World:
  def __init__(self, progress_tracker=None):
    self.progress_tracker = progress_tracker
    self.progress_tracker.update("Generating terrain noise...", 0.0)
    
    self.array = [
        [AirBlock(x, y) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    
    #cannot deepcopy pygame surface so I have to loop over it again
    self.back = [
        [AirBlock(x, y, isBack=True) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    
    self.mask = pg.mask.Mask((WORLD_WIDTH*BLOCK_SIZE, WORLD_HEIGHT*BLOCK_SIZE))
    self.lightmap = [
        [0 for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)]

    self.generateWorld()
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
    phases = {
            'noise': 0.1,
            'terrain': 0.3,
            'caves': 0.2,
            'ores': 0.2, 
            'trees': 0.2
        }
    
    # Precompute noise
    grassHeightNoise = self.SimplexNoise(19, 1)
    stoneHeightNoise = self.SimplexNoise(30, 1)
    cavesNoise = self.SimplexNoise(9, 2)

    oresNoise = {
      ore.__name__: (self.SimplexNoise(ore.veinSize, 2), ore)
      for ore in ores
    }
    
    baseProgress = 0.0        
    if self.progress_tracker:
        baseProgress = phases['noise']
        self.progress_tracker.update("Creating base terrain...", baseProgress)

    # Generate terrain in batch
    for x in range(WORLD_WIDTH):     
      if self.progress_tracker and x % (WORLD_WIDTH // 20) == 0:
            terrain_progress = (x / WORLD_WIDTH) * phases['terrain']
            total_progress = min(baseProgress + terrain_progress, 1.0)
            self.progress_tracker.update("Creating base terrain...", total_progress)
      
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
      
      baseProgress += phases["terrain"]

      #Cave pass
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, -1):         
          if self.progress_tracker and x % (WORLD_WIDTH // 20) == 0:
            cave_progress = (x / WORLD_WIDTH) * phases['caves']
            total_progress = min(baseProgress + cave_progress, 1.0)
            self.progress_tracker.update("Carving caves...", total_progress)
          
          if cavesNoise[y][x] > 0.1:
              self.array[y][x] = AirBlock(x, y)

      baseProgress += phases['caves']
          
      #Ore pass
      total_ores = len(oresNoise)
      for ore_idx, (ore_name, (oreNoise, ore)) in enumerate(oresNoise.items()):   
        if self.progress_tracker and x % (WORLD_WIDTH // 10) == 0:
                # Calculate ore progress as a combination of current ore and position
                ore_portion = (ore_idx + (x / WORLD_WIDTH)) / total_ores
                ore_progress = ore_portion * phases['ores']
                total_progress = min(baseProgress + ore_progress, 1.0)
                self.progress_tracker.update(f"Placing {ore_name}...", total_progress)
          
        for y in range(WORLD_HEIGHT - 1, stoneHeight, -1):
              if oreNoise[y][x] > ore.rarity and not self[y][x].isAir:
                  self.array[y][x] = ore(x, y)

      baseProgress += phases['ores']
      
      # Tree pass
      if self.progress_tracker and x % (WORLD_WIDTH // 20) == 0:
            tree_progress = (x / WORLD_WIDTH) * phases['trees']
            total_progress = min(baseProgress + tree_progress, 1.0)
            self.progress_tracker.update("Growing trees...", total_progress)
      
      if isinstance(self[grassHeight][x], DirtBlock) and self[grassHeight][x].variant == "grass block":           
          if random.random() > 0.8:  # Simplified tree placement
              self.__generateTree(x, grassHeight - 1)
              
    if self.progress_tracker:
          self.progress_tracker.update("Almost", 1.0)           

  def generateMask(self):
    for row in self.array:
      for block in row:
        self.mask.draw(block.mask, block.rect.topleft)
        
  def __generateTree(self, x, y):
    if x < 3:
      return
    if x > WORLD_WIDTH - 3:
      return
    height = random.randint(3, 7)
    for r in range(y-height-1, y+1):
      for c in range(x-2, x+3):
        if not self[r][c].isAir:
          return
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
    return self.blockAt(*player.pixelToCoord(*mousepos))

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
        pg.draw.rect(SUNLIGHTSURF, (0,0,0,light), player.relativeRect(block.rect))
  
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
            if y-1 >= 0 and self[y-1][x].edgeExist[WEST] and self[y-1][x].edgeId[WEST]<len(self.edgePool):
              # print("edge exists")
              self.edgePool[self[y-1][x].edgeId[WEST]].ey += 1
              # print(self.edgePool[self[y-1][x].edgeId[Direction.WEST]])
              cur.edgeId[WEST] = self[y-1][x].edgeId[WEST]
              cur.edgeExist[WEST] = True
            else:
              edge = Edge(x, y, x, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[WEST] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[WEST] = True
          # east
          if x+1 < (player.camera.right // BLOCK_SIZE) + 1 and self[y][x+1].isAir and self[y-1][x].edgeId[EAST]<len(self.edgePool):
            if y-1 >= 0 and self[y-1][x].edgeExist[EAST]:
              self.edgePool[self[y-1][x].edgeId[EAST]].ey += 1
              cur.edgeId[EAST] = self[y-1][x].edgeId[EAST]
              cur.edgeExist[EAST] = True
            else:
              edge = Edge(x+1, y, x+1, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[EAST] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[EAST] = True
          # north
          if y-1 >= 0 and self[y-1][x].isAir:
            if x-1 >= 0 and self[y][x-1].edgeExist[NORTH] and self[y][x-1].edgeId[NORTH]<len(self.edgePool):
              self.edgePool[self[y][x-1].edgeId[NORTH]].ex += 1
              cur.edgeId[NORTH] = self[y][x-1].edgeId[NORTH]
              cur.edgeExist[NORTH] = True
            else:
              edge = Edge(x, y, x+1, y)
              edgeId = len(self.edgePool)
              cur.edgeId[NORTH] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[NORTH] = True
          # south
          if y+1 < player.camera.bottom // BLOCK_SIZE + 1 and self[y+1][x].isAir and self[y][x-1].edgeId[SOUTH]<len(self.edgePool):
            if x-1 >= 0 and self[y][x-1].edgeExist[SOUTH]:
              self.edgePool[self[y][x-1].edgeId[SOUTH]].ex += 1
              cur.edgeId[SOUTH] = self[y][x-1].edgeId[SOUTH]
              cur.edgeExist[SOUTH] = True
            else:
              edge = Edge(x, y+1, x+1, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[SOUTH] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[SOUTH] = True
    for i in range(len(self.edgePool)):
      self.vertices.add(player.relativeCoord(self.edgePool[i].x*BLOCK_SIZE,self.edgePool[i].y*BLOCK_SIZE))
      self.vertices.add(player.relativeCoord(self.edgePool[i].ex*BLOCK_SIZE,self.edgePool[i].ey*BLOCK_SIZE))
      self.edgePool[i].draw()

  def generateLight(self, originr=None, originc=None):
    '''Generate lightmap for the entire world or specific part of world'''
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
            if bfs.peek is None:
              break
            else:
              continue
          
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

def mainMenu():
    button_font = pg.font.Font("MinecraftRegular-Bmg3.otf",  36)
    splash_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 28)
    button_text_colour = (240, 240, 240)
    text_shadow = (20, 20, 20, 160)

    bg_panorama = pg.image.load("title screen background animation.jpg").convert()
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(40)

    title_image = pg.image.load("title screen title.png").convert_alpha()
    title_image_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))

    splash_texts = [
      "Dont sue us Mojang!",
      "Made with Pygame!",
      "Lorem ipsum!",
      "Pygame >",
    ]
  
    current_splash = random.choice(splash_texts)
    splash_angle = -15
    splash_wave_offset = 0
    splash_scale = 1.0

    button_width, button_height = 400, 50
    button_x = (WIDTH - button_width) // 2
    spacing = 24
    start_y = HEIGHT // 2

    buttons = {
        'play': Button(button_x, start_y, button_width, button_height, "Play"),
        'instructions': Button(button_x, start_y + button_height + spacing, button_width, button_height, "Instructions"),
        'options': Button(button_x, start_y + (button_height + spacing) * 2, button_width, button_height, "Options"),
        'quit': Button(button_x, start_y + (button_height + spacing) * 3, button_width, button_height, "Quit"),
    }

    bg_scroll_speed = 20
    bg_offset = 0
    clock = pg.time.Clock()

    while True:
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit"

            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                for button in buttons.values():
                    button.handle_event(event, mouse_pos)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if buttons['play'].rect.collidepoint(mouse_pos):
                    return
                elif buttons['instructions'].rect.collidepoint(mouse_pos):
                    instructionsScreen()
                elif buttons['options'].rect.collidepoint(mouse_pos):
                    changeKeybinds()
                elif buttons['quit'].rect.collidepoint(mouse_pos):
                    sysexit()

        for button in buttons.values():
            button.update(mouse_pos)

        bg_offset = (bg_offset + bg_scroll_speed * clock.get_time() / 1000.0) % bg_panorama.get_width()

        #Draw background
        SURF.blit(bg_panorama, (-bg_offset, 0))
        SURF.blit(bg_panorama, (bg_panorama.get_width() - bg_offset, 0))
        SURF.blit(overlay, (0, 0))

        SURF.blit(title_image, title_image_rect)

        #Draw splash text
        splash_wave_offset += 0.03
        splash_scale = 1.0 + math.sin(splash_wave_offset * 0.5) * 0.03

        splash_surf = splash_font.render(current_splash, True, (255, 255, 0))
        splash_surf = pg.transform.rotate(splash_surf, splash_angle)
        splash_surf = pg.transform.scale(splash_surf, (int(splash_surf.get_width() * splash_scale), int(splash_surf.get_height() * splash_scale)))

        splash_y_offset = math.sin(splash_wave_offset) * 6
        splash_pos = (WIDTH // 2 + 180, HEIGHT // 4 + splash_y_offset)
        SURF.blit(splash_surf, splash_pos)

        #Draw buttons
        for button in buttons.values():
            button.draw(button_font, button_text_colour, text_shadow)

        pg.display.flip()
        clock.tick(FPS)
    
#TODO work on these later hopefully        
def instructionsScreen():
  pass
          
def changeKeybinds():
    pass
  
def pauseMenu():
    button_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 36)
    button_text_colour = (240, 240, 240)
    text_shadow = (20, 20, 20, 160)

    resume_button = Button((WIDTH - 400) // 2, HEIGHT // 2, 400, 50, "Back to Game")
    quit_button = Button((WIDTH - 400) // 2, (HEIGHT // 2) + 100, 400, 50, "Save and Quit")
    
    blurScale = 0.1    #lower is blurrier
    screen_size = SURF.get_size()
    small_size = (int(screen_size[0] * blurScale), int(screen_size[1] * blurScale))
    small_surface = pg.transform.smoothscale(SURF, small_size)
    blurred_surface = pg.transform.smoothscale(small_surface, screen_size)

    buttons = {
        'resume': resume_button,
        'quit': quit_button,
    }

    clock = pg.time.Clock()
    while True:
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sysexit()

            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                for button in buttons.values():
                    button.handle_event(event, mouse_pos)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if buttons['resume'].rect.collidepoint(mouse_pos):
                    return
                elif buttons['quit'].rect.collidepoint(mouse_pos):
                    sysexit()

        for button in buttons.values():
            button.update(mouse_pos)

        SURF.blit(blurred_surface, (0, 0))
        
        for button in buttons.values():
            button.draw(button_font, button_text_colour, text_shadow)

        pg.display.flip()
        clock.tick(FPS)

class LoadingScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        
        self.font = pg.font.Font("MinecraftRegular-Bmg3.otf", 20)
        self.titleFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 40)

        self.currentStep = "Initializing world..."
        
        self.currentMessage = 0   #seconds
        self.progress = 0.0
        self.startTime = time.time()

        self.barWidth = 400
        self.barHeight = 20
        self.barX = (width - self.barWidth) // 2
        self.barY = height // 2 + 30
        
    def update(self, progress, current_step):
        self.progress = progress
        self.currentStep = current_step

    def draw(self):
        self.screen.fill((25, 25, 25))

        title = self.titleFont.render("Loading world...", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title, title_rect)

        #Loading message
        message = self.font.render(self.currentStep, True, (200, 200, 200))
        message_rect = message.get_rect(center=(self.width // 2, self.height // 2 - 20))
        self.screen.blit(message, message_rect)

        #Progress bar
        pg.draw.rect(self.screen, (50, 50, 50), (self.barX, self.barY, self.barWidth, self.barHeight))
        fill_width = int(self.barWidth * self.progress)
        pg.draw.rect(self.screen, (106, 176, 76), (self.barX, self.barY, fill_width, self.barHeight))

        #Percentage
        percentage = f"{int(self.progress * 100)}%"
        percent_text = self.font.render(percentage, True, (255, 255, 255))
        percent_rect = percent_text.get_rect(center=(self.width // 2, self.barY + 40))
        self.screen.blit(percent_text, percent_rect)

        #Elapsed load time
        elapsed_time = time.time() - self.startTime
        elapsed_text = self.font.render(f"Time elapsed: {elapsed_time:.1f} seconds", True, (200, 200, 200))
        elapsed_rect = elapsed_text.get_rect(center=(self.width // 2, self.barY + 120))
        self.screen.blit(elapsed_text, elapsed_rect)

        pg.display.flip()
        clock.tick(FPS)

class WorldLoader:
    def __init__(self, width, height):
        self.loadingScreen = LoadingScreen(width, height)
        self.world = None
        self.progress = 0.0
        self.targetProgress = 0.0
        self.progressUpdates = Queue()
        self.generationCompleteEvent = threading.Event()
        self.generationThread = None
        self.currentStep = ""
        self.lastUpdateTime = time.time()

    def _updateProgress(self, step, step_progress):
        self.progressUpdates.add((step, step_progress))

    def _generateWorld(self):
        try:
            progress_tracker = ProgressTracker(self._updateProgress)
            self.world = World(progress_tracker)
            self.generationCompleteEvent.set()
            
        except Exception as e:
            print(f"Error during world generation: {str(e)}")
            raise

    def startGeneration(self):
      self.generationCompleteEvent.clear()
      self.generationThread = threading.Thread(target=self._generateWorld, daemon=True)
      self.generationThread.start()

    def update(self):
        current_time = time.time()
        delta_time = current_time - self.lastUpdateTime
        self.lastUpdateTime = current_time

        while self.progressUpdates:
            step, progress = self.progressUpdates.poll()
            self.targetProgress = progress
            self.currentStep = step

        #Loading bar smoothing
        smoothing_speed = 5.0
        smoothing_factor = 1.0 - math.exp(-smoothing_speed * delta_time)
        self.progress += (self.targetProgress - self.progress) * smoothing_factor

        self.loadingScreen.update(self.progress, self.currentStep)
        self.loadingScreen.draw()

        progress_complete = abs(self.progress - self.targetProgress) < 0.01
        return self.generationCompleteEvent.is_set() and progress_complete
        

'''Main Loop'''
if __name__ == "__main__":
  SUNLIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  LIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  FRAME = SURF.get_rect()
  ASURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  OVERLAY = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  
  #Give player items at the beginning of the game
  defaultItems = [GoldPickaxe(), IronAxe(), StoneAxe(), WoodenShovel(), CraftingTableItem()] + [
    CobbleStoneItem() for _ in range(192)] + [TorchItem() for _ in range(64)]
  
  loader = WorldLoader(WIDTH, HEIGHT)
  loader.startGeneration()
  start_time = time.time()
  
  mainMenu()

  while True:
      for event in pg.event.get():
          if event.type == pg.QUIT:
              sysexit()
      
      if loader.update():
          if not loader.generationThread.is_alive():
              break
  
  world = loader.world
  player = Player()
  sun = Sun()

  
  while True:
    frameStartTime = time.time()
    SURF.fill((255, 255, 255))
    ASURF.fill((0, 0, 0, 0))
    OVERLAY.fill((0, 0, 0, 0))
    SUNLIGHTSURF.fill((0, 0, 0, 255))
    LIGHTSURF.fill((0, 0, 0, 0))
    keys = pg.key.get_pressed()
    
    #sun.draw()
    world.update()
    player.update()
    
    #Temporarily game over logic
    if player.health <= 0:
      print("The skbidi died")
      sysexit()

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

    if pg.mouse.get_pressed()[0] and not player.inventory.menu.hoveredSlot:
      player.mine()
    if pg.mouse.get_pressed()[2]:   #right click
      player.place()

    for event in pg.event.get():
      if event.type == QUIT:
        sysexit()
      elif event.type == 101:
        print("fps: ", round(clock.get_fps(), 2))    
      elif event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
        if player.inventory.menu.hoveredSlot:
          print(player.inventory.menu.hoveredSlot)
          player.inventory.menu.pickUpItem()
      elif event.type == KEYDOWN and event.key == pg.K_ESCAPE:
        pauseMenu()
        
      elif event.type == KEYDOWN and event.key == pg.K_e:
        check_for_interaction()
      elif event.type == KEYDOWN and event.key == pg.K_m:
        pixel = tuple(map(lambda a: BLOCK_SIZE*a,player.pixelToCoord(*pg.mouse.get_pos())))
        # print(pixel, world.mask.get_at(pixel), world.blockAt(*player.pixelToCoord(*pg.mouse.get_pos())).rect.topleft)
        
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
    SURF.blit(OVERLAY, (0,0))
    SURF.blit(font20.render(str(player.pixelToCoord(*player.camera.center)), True, (0,0,0)), (20, 50))
    
    frameEndTime = time.time()
    clock.tick(FPS)
    pg.display.flip()