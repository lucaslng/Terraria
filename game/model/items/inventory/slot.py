from collections.abc import Callable
from dataclasses import dataclass
from game.model.items.item import Item

@dataclass
class Slot:
	'''Slot class, something used to store items'''

	item: Item | None = None
	count: int = 0
	condition: Callable[[Item | None], bool] = lambda item: True

	def clear(self):
		'''reset/clear the slot'''

		self.item = None
		self.count = 0
	
	def __repr__(self):
		if self.item:
			return f'{self.item.enum.name} x {self.count}'
		else:
			return 'empty slot'