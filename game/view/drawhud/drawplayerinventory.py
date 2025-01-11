from functools import partial
from constants import BLOCK_SIZE
from game.view.inventory.drawinventory import drawInventory


drawPlayerInventory = partial(drawInventory, inventoryx=15, inventoryy=80, slotSize=BLOCK_SIZE+2)