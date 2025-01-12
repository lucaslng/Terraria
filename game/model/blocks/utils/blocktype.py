from enum import Enum, auto


class BlockType(Enum):
  '''Possible block types corresponding to the tool that they are mined with.'''
  NONE = auto()
  PICKAXE = auto()
  AXE = auto()
  SHOVEL = auto()
  SWORD = auto()
  SHEARS = auto()
  FLINTANDSTEEL = auto()