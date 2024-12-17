import sys, math, random, time, pickle          #pickle stores game data onto system
import pygame as pg
from pygame.locals import *
from pygame import Vector2
from abc import *
from dataclasses import dataclass
from typing import List, TypedDict
from enum import Enum


WIDTH = 1000
HEIGHT = 600
FPS = 60

BLOCK_SIZE = 25
WORLD_HEIGHT = 256
WORLD_WIDTH = 1000
SHADOW_QUALITY = 3
gravity = 1

SEED = time.time()
random.seed(SEED)
start = time.time()
pg.init()
clock = pg.time.Clock()

pg.time.set_timer(101,500)

SURF = pg.display.set_mode((WIDTH, HEIGHT), vsync=1)
pg.display.set_caption("Terraria")

class Direction:
  NORTH=0
  SOUTH=1
  WEST=2
  EAST=3

class SpriteSheet:
  '''sprite sheet class'''
  def __init__(this, imageName: str):
    this.sheet = pg.image.load(imageName).convert_alpha()
  def get(this, x, y, width, height, scale=BLOCK_SIZE, colour=(0,0,0)):
    image = pg.Surface((width, height)).convert_alpha()
    image.blit(this.sheet, (0, 0), (x, y, width, height))
    image = pg.transform.scale(image, (scale, scale))
    image.set_colorkey(colour)
    return image

class Animation:
  '''list of frames to cycle between for an animation. unit of duration is in frames'''
  def __init__(this, *args, duration: int=10, startFrame: int = 0):
    this.arr: List[pg.surface.Surface] = list(args)
    this.duration = duration
    this.frame = startFrame * duration
  
  def __getitem__(this, i: int) -> pg.surface.Surface:
    return this.arr[i]
  
  def drawAnimated(this, x: int, y: int, flipped=False):
    '''draws the the animation, takes a pixel relative to camera'''
    index = this.frame//this.duration
    this.frame += 1
    if this.frame > len(this.arr) * this.duration - 1: this.frame = 0
    return this.drawFrame(x, y, index, flipped)

  def drawFrame(this, x: int, y: int, index=0, flipped=False):
    '''draws the frame of the given index, takes a pixel relative to camera'''
    texture = this[index]
    if flipped: texture = pg.transform.flip(texture, True, False).convert_alpha()
    return SURF.blit(texture, (x, y))

catSheet = SpriteSheet("cat.png")
sprites = {
  "cat": {
    "walk": Animation(
      catSheet.get(9, 144, 16, 16),
      catSheet.get(40, 144, 16, 16),
      catSheet.get(71, 144, 16, 16),
      catSheet.get(103, 144, 16, 16),
      catSheet.get(135, 144, 16, 16),
      catSheet.get(167, 144, 16, 16),
      catSheet.get(200, 144, 16, 16),
      catSheet.get(232, 144, 16, 16),
    ),
    "run": Animation(
      catSheet.get(9, 176, 16, 16),
      catSheet.get(40, 176, 16, 16),
      catSheet.get(71, 176, 16, 16),
      catSheet.get(103, 176, 16, 16),
      catSheet.get(135, 176, 16, 16),
      catSheet.get(167, 176, 16, 16),
      catSheet.get(200, 176, 16, 16),
      catSheet.get(232, 176, 16, 16),
    ),
    "jump": Animation(
      catSheet.get(9, 272, 16, 16),
      catSheet.get(40, 272, 16, 16),
      catSheet.get(71, 272, 16, 16),
      catSheet.get(103, 272, 16, 16),
      catSheet.get(135, 272, 16, 16),
      catSheet.get(167, 272, 16, 16),
      catSheet.get(200, 272, 16, 16),
    ),
    "sit": Animation(
      catSheet.get(8, 16, 16, 16),
      catSheet.get(40, 16, 16, 16),
      catSheet.get(72, 16, 16, 16),
      catSheet.get(104, 16, 16, 16),
    ),
  },
}



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
    
    this.variant = variant.name.lower()
class DirtItem(PlaceableItem):
  dirtItemTexture = pg.transform.scale(pg.image.load("dirt.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Dirt", this.dirtItemTexture, 64)
    
class OakLogBlock(Block):
    oakLogTexture = pg.transform.scale(pg.image.load("oak_log.png"), (BLOCK_SIZE, BLOCK_SIZE))  
    def __init__(self, x, y):
        super().__init__("Oak Log", self.oakLogTexture, x, y, 2, BlockType.AXE)
class OakLogItem(PlaceableItem):
    oakLogItemTexture = pg.transform.scale(pg.image.load("oak_log.png"), (Item.SIZE, Item.SIZE))
    def __init__(self):
        super().__init__("Oak Log", self.oakLogItemTexture, 64)

class LeavesBlock(Block):
    leavesTexture = pg.transform.scale(pg.image.load("leaves.png"), (BLOCK_SIZE, BLOCK_SIZE))  
    def __init__(self, x, y):
        super().__init__("Leaves", self.leavesTexture, x, y, 1, BlockType.SHEARS)

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
BlockItemRegistry.register(OakLogBlock, OakLogItem)
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
  startingDurability: int
  blockType: BlockType
  
  def __post_init__(self):
    self.durability = self.startingDurability

class Shears(Tool):
  shearsTexture = pg.transform.scale(
    pg.image.load("shears.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Shears", this.shearsTexture, 1, 1.5, 238, BlockType.SHEARS)
    
'''Wooden'''
class WoodenPickaxe(Tool):
  woodenPickaxeTexture = pg.transform.scale(
    pg.image.load("wooden_pickaxe.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Wooden Pickaxe", this.woodenPickaxeTexture, 1, 1.5, 59, BlockType.PICKAXE)  
class WoodenAxe(Tool):
  woodenAxeTexture = pg.transform.scale(
    pg.image.load("wooden_axe.png"), (Item.SIZE, Item.SIZE)
  )
  def __init__(this):
    super().__init__("Wooden Axe", this.woodenAxeTexture, 1, 1.5, 59, BlockType.AXE)
class WoodenShovel(Tool):
  woodenShovelTexture = pg.transform.scale(
    pg.image.load("wooden_shovel.png"), (Item.SIZE, Item.SIZE)
  )
  def __init__(this):
    super().__init__("Wooden Shovel", this.woodenShovelTexture, 1, 1.5, 59, BlockType.SHOVEL)
class WoodenSword(Tool):
  woodenSwordTexture = pg.transform.scale(
    pg.image.load("wooden_sword.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Wooden Sword", this.woodenSwordTexture, 1, 1.5, 59, BlockType.SWORD)
    
'''Stone'''
class StonePickaxe(Tool):
  stonePickaxeTexture = pg.transform.scale(
    pg.image.load("stone_pickaxe.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Stone Pickaxe", this.stonePickaxeTexture, 1, 2.5, 131, BlockType.PICKAXE)
class StoneAxe(Tool):
  stoneAxeTexture = pg.transform.scale(
    pg.image.load("stone_axe.png"), (Item.SIZE, Item.SIZE))
  def __init__(this):
    super().__init__("Stone Axe", this.stoneAxeTexture, 1, 2.5, 131, BlockType.AXE)
    
'''Gold'''


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
    this.reversedTexture = pg.transform.flip(texture, True, False).convert_alpha()
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
  texture = sprites["cat"]["walk"][0]
  thisSprites = sprites["cat"]
  reach = 4 * BLOCK_SIZE
  full_heart_texture = pg.transform.scale(
      pg.image.load("full_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))
  half_heart_texture = pg.transform.scale(
      pg.image.load("half_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))
  empty_heart_texture = pg.transform.scale(
      pg.image.load("empty_heart.png"), (BLOCK_SIZE, BLOCK_SIZE))
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
        this.camera.centery - BLOCK_SIZE // 2,
        BLOCK_SIZE,
        BLOCK_SIZE,
        this.texture,
        10,
        2,
        18,
    )
    this.mask = pg.mask.Mask((20, 20), True)

    HasInventory.__init__(this, 4, 10)
    
    this.heldSlotIndex = 0  # number from 0 to 9
    this.rect.center = this.camera.center
    this.centerRect = this.rect.copy()
    this.centerRect.center = FRAME.center
    this.max_health = 20
    this.health = this.max_health

    this.falling = False
    this.fall_start_y = None
    this.fall_damage_threshold = 6 * BLOCK_SIZE
    this.is_initial_spawn = True
    this.spawn_protection_timer = 120

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
        
        if this.heldSlot().item and this.heldSlot().item.isTool():
          #Checks if durability is 0
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

  def update(this):
    super().update()
    this.blockFacing = this.getBlockFacing()
    this.drawBlockFacing()
    this.drawHeldItem()
    if not pg.mouse.get_pressed()[0]:
      this.usingItem = False
  
  def drawHUD(this):
    this.draw_health()
    this.drawHotbar()

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
    pg.draw.circle(SURF,(0,255,0),relativeCoord(this.x*BLOCK_SIZE,this.y*BLOCK_SIZE), 3)
    pg.draw.circle(SURF,(0,255,0),relativeCoord(this.ex*BLOCK_SIZE,this.ey*BLOCK_SIZE), 3)
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
    this.mask = pg.mask.Mask((WORLD_WIDTH*BLOCK_SIZE, WORLD_HEIGHT*BLOCK_SIZE))
    this.__generateWorld()
    this.generateMask()

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
    treeNoise = this.SimplexNoise(19, 1)
    
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

      # Cave pass
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, - 1):
        if cavesNoise[y][x] > 0.1:
          this.array[y][x] = AirBlock(x, y)
          
      #Tree pass
      if isinstance(this[y][x], DirtBlock):
        # if random.randint(0, 10) > 8:
        this.__generateTree(x, y-1)

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
          block.drawBlock()
  
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
      # this.edgePool[i].draw()
  
  def castRays(this):
    this.litVertices.clear()
    for vertex in this.vertices:
      bres = bresenham(*vertex, *sun.pos, True, SHADOW_QUALITY)
      if bres: 
        this.litVertices.extend(bres)
    this.litVertices.extend((FRAME.topleft, FRAME.topright, relativeCoord(*this.topBlock(WORLD_WIDTH-1).rect.topleft), relativeCoord(*this.topBlock(0).rect.topright)))
    if len(this.litVertices) > 2:
      this.litVertices.sort(key=lambda a: math.atan2(sun.pos[1]-a[1], sun.pos[0]-a[0]))
      pg.draw.polygon(LIGHTSURF, (255,255,255,0), [sun.pos] + this.litVertices)
  
  def update(this):
    this.draw()
    this.buildEdgePool()
    this.castRays()

if __name__ == "__main__":
  LIGHTSURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  FRAME = SURF.get_rect()
  ASURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
  ASURF.fill((0, 0, 0, 0))
  
  #Give player items at the beginning of the game
  defaultItems = [StonePickaxe(), WoodenAxe(), WoodenShovel(), WoodenSword(), Shears(), CraftingTableItem()] + [CobbleStoneItem() for _ in range(192)]
  
  player = Player()
  craftingMenu = CraftingMenu()
  
  font = pg.font.Font(None, 15)
  font20 = pg.font.Font(None, 20)
  
  world = World()
  sun = Sun()
  
  end = time.time()
  print("Load time:", round(end-start, 2), "seconds")
  
  
  while True:
    SURF.fill((255, 255, 255))
    ASURF.fill((0, 0, 0, 0))
    LIGHTSURF.fill((0, 0, 0, 240))
    keys = pg.key.get_pressed()
    
    sun.draw()
    world.update()
    player.update()
    
    #Temporarily game over logic
    if player.health <= 0:
      print("The skbidi has died")
      pg.quit()
      sys.exit()

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
      elif event.type == KEYDOWN and event.key == pg.K_e:
        check_for_interaction()
      elif event.type == KEYDOWN and event.key == pg.K_m:
        pixel = tuple(map(lambda a: BLOCK_SIZE*a,pixelToCoord(*pg.mouse.get_pos())))
        print(pixel, world.mask.get_at(pixel), world.blockAt(*pixelToCoord(*pg.mouse.get_pos())).rect.topleft)
        
        # print(world.mask.get_at())

    SURF.blit(ASURF, (0, 0))
    # LIGHTSURF = pg.transform.smoothscale(LIGHTSURF, (WIDTH//15, HEIGHT//15))
    # LIGHTSURF = pg.transform.smoothscale(LIGHTSURF, (WIDTH, HEIGHT))
    # SURF.blit(LIGHTSURF, ((0,0)))
    player.drawHUD()
    SURF.blit(font20.render(str(pixelToCoord(*player.camera.center)), True, (0,0,0)), (20, 50))
    if craftingMenu.isActive: craftingMenu.draw()

    pg.display.flip()
    clock.tick(FPS)