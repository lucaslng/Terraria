from game.model.blocks.utils.blocksenum import Blocks
from game.model.items.cobblestoneitem import CobblestoneItem
from game.model.items.dirtitem import DirtItem


block2Item = {
  Blocks.Dirt: DirtItem,
  Blocks.Grass: DirtItem,
	Blocks.Stone: CobblestoneItem,
	Blocks.Cobblestone: CobblestoneItem,
}