from collections import defaultdict
from game.model.blocks.cobblestoneblock import CobblestoneBlock
from game.model.blocks.dirtblock import DirtBlock
from game.model.blocks.grassblock import GrassBlock
from game.model.blocks.stoneblock import StoneBlock
from game.model.items.utils.itemsenum import Items


item2Block = defaultdict(None)

item2Block[Items.Dirt] = DirtBlock
item2Block[Items.Grass] = GrassBlock
item2Block[Items.Stone] = StoneBlock
item2Block[Items.Cobblestone] = CobblestoneBlock