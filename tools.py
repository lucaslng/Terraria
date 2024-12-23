import pygame as pg
from dataclasses import dataclass

from itemsandblocks import *
from sprites import *

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