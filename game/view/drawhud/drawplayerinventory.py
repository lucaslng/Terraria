from functools import partial
from collections.abc import Callable
from constants import BLOCK_SIZE
from game.model.items.inventory.inventory import Inventory
from game.view.inventory.drawinventory import drawInventory


drawPlayerInventory: Callable[[Inventory], None] = partial(drawInventory, inventoryx=15, inventoryy=80, slotSize=BLOCK_SIZE+2)