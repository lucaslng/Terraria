from game.model.entity.entities.player import Player
from game.model.items.dirtitem import DirtItem


def addDefaultItems(player: Player) -> None:
	'''Add default items to the player'''
	for _ in range (67):
		player.inventory.addItem(DirtItem())