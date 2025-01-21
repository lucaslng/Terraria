from game.model.items.utils.itemsenum import Items


class Item:
	'''Base item class'''

	enum: Items
	stackSize: int = 64
	damage: float = 1

	def __eq__(self, other: 'Item') -> bool:
		'''Override == operator to check for item enum'''
		
		if other is None:
			return False
		return self.enum == other.enum