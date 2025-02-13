from collections.abc import Callable
from game.model.items.inventory.slot import Slot
from game.model.items.item import Item


class Inventory:
	'''Inventory class, 2d array of slots'''

	def __init__(self, rows: int, cols: int, condition: Callable[[Slot], bool] = lambda other: True):
		self.rows = rows
		self.cols = cols
		self.array = [
			[Slot(condition=condition) for _ in range(cols)]
			for _ in range(rows)]
	
	def __getitem__(self, i: int):
		return self.array[i]


	def addItem(self, item: Item) -> bool:
		'''Attempt to add an item to the end of the inventory. Returns bool based on success or failure'''

		# first attemps to add the item to a stack with existing items
		for row in self.array:
			for slot in row:
				if slot.item and slot.item == item and slot.count < slot.item.stackSize:
					slot.count += 1
					return True
		
		# then attempts to find an empty slot if there isn't an existing stack with taht item
		for row in self.array:
			for slot in row:
				if slot.item is None:
					slot.item = item
					slot.count = 1
					return True

		return False

	def addItems(self, *items: Item) -> bool:
		'''Add multiple items to the inventory at once'''

		for item in items:
			self.addItem(item)
	
	def __repr__(self) -> str:
		out = ""
		for r, row in enumerate(self.array):
			for c, slot in enumerate(row):
				out += f'[{r}][{c}] {slot.__repr__()}'
		return out