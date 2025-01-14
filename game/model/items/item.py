from dataclasses import dataclass
from typing import Self

from game.model.items.utils.itemsenum import Items


@dataclass
class Item:
	'''Base item class'''

	enum: Items
	stackSize: int = 64

	def __eq__(self, other: Self) -> bool:
		'''Override == operator to check for item enum'''
		
		if other is None:
			return False
		return self.enum == other.enum