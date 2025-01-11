from constants import BLOCK_SIZE
from game.model.items.inventory.inventory import Inventory
from game.view.inventory.drawinventory import drawInventory


def drawPlayerInventory(inventory: Inventory):
	drawInventory(inventory, 15, 80, BLOCK_SIZE + 2)