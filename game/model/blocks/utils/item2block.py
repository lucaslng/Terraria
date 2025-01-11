from game.model.blocks.cobblestoneblock import CobblestoneBlock
from game.model.blocks.dirtblock import DirtBlock
from game.model.blocks.grassblock import GrassBlock
from game.model.blocks.stoneblock import StoneBlock
from game.model.items.utils.itemsenum import Items



item2Block = {
	Items.Dirt: DirtBlock,
	Items.Grass: GrassBlock,
	Items.Stone: StoneBlock,
	Items.Cobblestone: CobblestoneBlock,
}