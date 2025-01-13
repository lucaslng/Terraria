from dataclasses import dataclass
from game.model.items.item import Item


@dataclass
class Slot:
	'''Slot class, something used to store items'''

	item: Item | None = None
	count: int = 0

	def clear(self):
		'''reset/clear the slot'''

		self.item = None
		self.count = 0
	
	def __repr__(self):
		if self.item:
			return f'{self.item.enum.name} x {self.count}'
		else:
			return 'empty slot'