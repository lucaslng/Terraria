from game.model.blocks.airblock import AirBlock
from game.model.blocks.block import Block
import math
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
	
	def topy(self, x: float) -> int:
		'''returns the y of the top block at x'''
		ceil = math.ceil(x)
		floor = math.floor(x)
		for y in range(1, self.height):
			if not self[y][ceil].isEmpty or not self[y][floor].isEmpty:
				return y
		return self.height - 1
	
	def __getitem__(self, i: int):
		return self.array[i]