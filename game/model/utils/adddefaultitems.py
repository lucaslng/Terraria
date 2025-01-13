from game.model.entity.entities.player import Player
from game.model.items.craftingtableitem import CraftingTableItem
from game.model.items.dirtitem import DirtItem
from game.model.items.tools import WoodenAxe
from game.model.items.torchitem import TorchItem


def addDefaultItems(player: Player) -> None:
	'''Add default items to the player'''
	for _ in range (128):
		player.inventory.addItem(DirtItem())
	player.inventory.addItems(*[TorchItem() for _ in range(64)], CraftingTableItem(), WoodenAxe())