import pygame as pg
from abc import ABC
from dataclasses import dataclass
from enum import Enum

from constants import *
from items import PlaceableItem, Item
from utils import relativeRect, Executable
from inventory import Interactable
from entities import Player
from world import WorldLoader
from sprites import sprites
from light import Light, lights
from items import Executable

player = Player()

loader = WorldLoader(WIDTH, HEIGHT)
world = loader.world


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