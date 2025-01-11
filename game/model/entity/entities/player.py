from game.model.entity.entity import Entity
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.slot import Slot
from game.model.world import World

class Player(Entity):
	'''Player entity class'''
	
	def __init__(self, x: float, y: float, world: World):
		super().__init__(x, y, 4, 1, 1, 10000, 8, 60, 20, 0.8, 18, world)
		self.inventory = Inventory(4, 9)
		self._heldSlotIndex = 0
	
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
	
	def heldSlot(self) -> Slot:
		'''returns the held slot'''
		
		return self.hotbar[self._heldSlotIndex]