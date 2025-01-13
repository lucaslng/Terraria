from collections import defaultdict
from game.model.blocks.utils.blocksenum import Blocks
from game.model.items.cobblestoneitem import CobblestoneItem
from game.model.items.craftingtableitem import CraftingTableItem
from game.model.items.dirtitem import DirtItem
from game.model.items.torchitem import TorchItem


block2Item = defaultdict(lambda: None)

block2Item[Blocks.Dirt] = DirtItem
block2Item[Blocks.Grass] = DirtItem
block2Item[Blocks.Stone] = CobblestoneItem
block2Item[Blocks.Cobblestone] = CobblestoneItem
block2Item[Blocks.CraftingTable] = CraftingTableItem
block2Item[Blocks.Torch] = TorchItem