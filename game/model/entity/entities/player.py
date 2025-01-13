from game.model.entity.entity import Entity
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.slot import Slot
from game.model.light import Light
from game.model.world import World

class Player(Entity, Light):
	'''Player entity class'''

	_heldSlotIndex = 0
	reach = 4
	inventory = Inventory(4, 9)
	cursorSlot = Slot()
	lightRadius = 0.8
	
	def __init__(self, x: float, y: float, world: World):
		super().__init__(x, y, 4, 1, 1, 20000, 7, 60, 20, 0.99, 18, world)
	
	@property
	def hotbar(self) -> list[Slot]:
		'''Returns the hotbar, the first row of the player's inventory'''
		return self.inventory[0]
	
	@property
	def heldSlotIndex(self) -> int:
		return self._heldSlotIndex
	
	@heldSlotIndex.setter
	def heldSlotIndex(self, index: int) -> None:
		assert 0 <= index < self.inventory.cols # raise error if index is not relevant
		if index != self._heldSlotIndex:
			self._heldSlotIndex = index
	
	@property
	def heldSlot(self) -> Slot:
		'''returns the held slot'''
		return self.hotbar[self._heldSlotIndex]