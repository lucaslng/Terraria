from enum import Enum
from utils.constants import BLOCK_SIZE, FRAME


class InventoryType(Enum):
	Player = (BLOCK_SIZE + 2, 15, 80)
	HelmetSlot = (BLOCK_SIZE + 2, 15, 220)
 
	CraftingIn = (BLOCK_SIZE * 2, FRAME.centerx - BLOCK_SIZE * 7, int(FRAME.height * 0.4 - BLOCK_SIZE * 3))
	CraftingOut = (BLOCK_SIZE * 2, FRAME.centerx + BLOCK_SIZE, int(FRAME.height * 0.4 - BLOCK_SIZE))
	
	FurnaceIn = (BLOCK_SIZE * 2, FRAME.centerx - BLOCK_SIZE * 2, int(FRAME.height * 0.4 - BLOCK_SIZE) - 50)
	FuelIn = (BLOCK_SIZE * 2, FRAME.centerx - BLOCK_SIZE * 2, int(FRAME.height * 0.4))
	FurnaceOut = (BLOCK_SIZE * 2, FRAME.centerx + BLOCK_SIZE * 2, int(FRAME.height * 0.4 - BLOCK_SIZE))
 
	Chest = (BLOCK_SIZE * 2, FRAME.centerx - BLOCK_SIZE * 9, int(FRAME.height * 0.4 - BLOCK_SIZE))