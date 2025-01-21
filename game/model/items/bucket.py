from typing import Type
from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items
from game.model.liquids.liquid import Liquid, Water


class Bucket(Item):
	'''Item for a bucket that can hold liquids'''

	stackSize = 1

	def __init__(self, liquid: Type[Liquid] | None=None, capacity: float=1, filledAmount: float=0):
		self.liquid = liquid
		self.capacity = capacity
		self.filledAmount = filledAmount
	
	def clear(self) -> None:
		'''clear the bucket'''
		
		self.liquid = None
		self.filledAmount = 0
	
	def fill(self, amount: float=1) -> None:
		'''fill the bucket by a certain amount (defaults to fully filling the bucket)'''

		if self.liquid:
			self.filledAmount = min(self.capacity, amount + self.filledAmount)
	
	@property
	def enum(self) -> Items:
		match self.liquid:
			case None:
				return Items.BucketEmpty
			case Water:
				return Items.BucketWater