import pygame as pg
from dataclasses import dataclass
from enum import Enum
from abc import *

from constants import *
from sprites import *
from tools import *

@dataclass
class Item:
  '''Base item class'''
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
    return isinstance(this, ExecutableItem)


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
    if this.isAir: this.mask.clear()
    this.edgeExist = [False for _ in range(4)]
    this.edgeId = [0 for _ in range(4)]

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
class ExecutableItem(Item, ABC):
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
  def __init__(this, x=-1, y=-1):
    super().__init__("Air", this.texture, x, y, 0, BlockType.NONE, isAir=True)

class CraftingTableBlock(Block, Interactable):
  craftingTableTexture = pg.transform.scale(
    pg.image.load("crafting_table.png"), (BLOCK_SIZE, BLOCK_SIZE))
  
  def __init__(this, x, y):
    Block.__init__(this, name="Crafting Table", texture=this.craftingTableTexture,
                   x=x, y=y, hardness=2.5, blockType=BlockType.AXE)

  def interact(this):
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
    super().__init__(variant.name, variant.texture, x, y, 1.5, BlockType.SHOVEL)
    
    this.variant = variant.name.lower()
class DirtItem(PlaceableItem):
  dirtItemTexture = pg.transform.scale(pg.image.load("dirt.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Dirt", this.dirtItemTexture, 64)
    
class OakLogBlock(Block):
    oakLogTexture = pg.transform.scale(pg.image.load("oak_log.png"), (BLOCK_SIZE, BLOCK_SIZE))  
    def __init__(this, x, y):
        super().__init__("Oak Log", this.oakLogTexture, x, y, 2.5, BlockType.AXE)
class OakLogItem(PlaceableItem):
    oakLogItemTexture = pg.transform.scale(pg.image.load("oak_log.png"), (Item.SIZE, Item.SIZE))
    def __init__(this):
        super().__init__("Oak Log", this.oakLogItemTexture, 64)

class LeavesBlock(Block):
    leavesTexture = pg.transform.scale(pg.image.load("leaves.png"), (BLOCK_SIZE, BLOCK_SIZE))  
    def __init__(this, x, y):
        super().__init__("Leaves", this.leavesTexture, x, y, 1, BlockType.SHEARS)

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
    super().__init__("Cobblestone", this.cobblestoneTexture, x, y, 5.5, BlockType.PICKAXE)
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

class TorchItem(ExecutableItem):
  torchItemTexture = pg.transform.scale(pg.image.load("torch.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Torch", this.torchItemTexture, 64)
  def execute(this):
    player.light.radius = 100
  def unexecute(this):
    player.light.radius = BLOCK_SIZE//2

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