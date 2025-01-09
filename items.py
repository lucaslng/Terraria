import pygame as pg

from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

from constants import SURF, WIDTH, HEIGHT
from sprites import sprites
from world import WorldLoader
from utils import Executable
from blocks import BlockItemRegistry

loader = WorldLoader(WIDTH, HEIGHT)
world = loader.world

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

@dataclass
class PlaceableItem(Item):
  '''Items that have a corresponding block and can be placed.'''
  @classmethod
  def block(cls):
    return BlockItemRegistry.getBlock(cls)
  
  def place(self, x: int, y: int) -> None:
    world[y][x] = self.block()(x, y)
    # world.mask.draw(world[y][x].mask, world[y][x].rect.topleft)

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