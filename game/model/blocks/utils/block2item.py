from collections import defaultdict

from game.model.blocks.utils.blocksenum import Blocks
from game.model.items.chestitem import ChestItem
from game.model.items.cobblestoneitem import CobblestoneItem
from game.model.items.craftingtableitem import CraftingTableItem
from game.model.items.dirtitem import DirtItem
from game.model.items.flowers import AlliumItem, CornflowerItem, DandelionItem, PoppyItem
from game.model.items.furnaceitem import FurnaceItem
from game.model.items.ingots import CoalItem, DiamondItem
from game.model.items.logitem import LogItem
from game.model.items.ores import GoldOreItem, IronOreItem
from game.model.items.planksitem import PlanksItem
from game.model.items.torchitem import TorchItem


block2Item = defaultdict(lambda: None)

block2Item[Blocks.Dirt] = DirtItem
block2Item[Blocks.Grass] = DirtItem
block2Item[Blocks.Stone] = CobblestoneItem
block2Item[Blocks.Cobblestone] = CobblestoneItem
block2Item[Blocks.CraftingTable] = CraftingTableItem
block2Item[Blocks.Furnace] = FurnaceItem
block2Item[Blocks.Chest] = ChestItem
block2Item[Blocks.Torch] = TorchItem
block2Item[Blocks.Log] = LogItem
block2Item[Blocks.Planks] = PlanksItem

block2Item[Blocks.CoalOre] = CoalItem
block2Item[Blocks.IronOre] = IronOreItem
block2Item[Blocks.GoldOre] = GoldOreItem
block2Item[Blocks.DiamondOre] = DiamondItem

block2Item[Blocks.Poppy] = PoppyItem
block2Item[Blocks.Dandelion] = DandelionItem
block2Item[Blocks.Cornflower] = CornflowerItem
block2Item[Blocks.Allium] = AlliumItem