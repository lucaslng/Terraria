from game.model.blocks.airblock import AirBlock
from game.model.blocks.block import Block
import math

class World:
	'''World object, an array of blocks'''
	def __init__(self, width: int, height: int) -> None:
		self.array: list[list[Block]] = [[AirBlock() for x in range(width)] for y in range(height)]
		self.back: list[list[Block]] = [[AirBlock() for x in range(width)] for y in range(height)]
		self.width = width
		self.height = height
	
	def top_y(self, x: float) -> int:
		'''Returns the y value of the top block at x'''
		floor = math.floor(x)
		ceil = math.ceil(x)

		for y in range(self.height):
			if not self.array[y][floor].isEmpty or not self.array[y][ceil].isEmpty:
				return y

		return self.height
	
	def __getitem__(self, i: int):
		return self.array[i]