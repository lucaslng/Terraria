from game.model.blocks.airblock import AirBlock
from game.model.blocks.block import Block
class World:
	'''World object, an array of blocks'''
	def __init__(self, width: int, height: int) -> None:
		self.array: list[list[Block]] = [
			[AirBlock() for x in range(width)] for y in range(height)
		]
		self.back: list[list[Block]] = [
			[AirBlock() for x in range(width)] for y in range(height)
		]
		self.width = width
		self.height = height
	
	def __getitem__(self, i: int):
		return self.array[i]