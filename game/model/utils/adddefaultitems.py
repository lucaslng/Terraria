from game.model.entity.entities.player import Player
from game.model.items.dirtitem import DirtItem
from game.model.items.tools import WoodenAxe


def addDefaultItems(player: Player) -> None:
	'''Add default items to the player'''
	for _ in range (67):
		player.inventory.addItem(DirtItem())
	player.inventory.addItem(WoodenAxe())