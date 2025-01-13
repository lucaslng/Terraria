from collections import defaultdict
from game.model.blocks.cobblestoneblock import CobblestoneBlock
from game.model.blocks.craftingtableblock import CraftingTableBlock
from game.model.blocks.dirtblock import DirtBlock
from game.model.blocks.grassblock import GrassBlock
from game.model.blocks.oaklogblock import LogBlock
from game.model.blocks.planksblock import PlanksBlock
from game.model.blocks.stoneblock import StoneBlock
from game.model.blocks.torchblock import TorchBlock
from game.model.items.utils.itemsenum import Items


item2Block = defaultdict(lambda: None)

item2Block[Items.Dirt] = DirtBlock
item2Block[Items.Grass] = GrassBlock
item2Block[Items.Stone] = StoneBlock
item2Block[Items.Cobblestone] = CobblestoneBlock
item2Block[Items.CraftingTable] = CraftingTableBlock
item2Block[Items.Torch] = TorchBlock
item2Block[Items.Log] = LogBlock
item2Block[Items.Planks] = PlanksBlock