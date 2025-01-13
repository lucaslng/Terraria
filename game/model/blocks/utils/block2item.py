from collections import defaultdict
from game.model.blocks.utils.blocksenum import Blocks
from game.model.items.cobblestoneitem import CobblestoneItem
from game.model.items.dirtitem import DirtItem


block2Item = defaultdict(None)

block2Item[Blocks.Dirt] = DirtItem
block2Item[Blocks.Grass] = DirtItem
block2Item[Blocks.Stone] = CobblestoneItem
block2Item[Blocks.Cobblestone] = CobblestoneItem