from game.model.blocks.airblock import AirBlock

class World:
	'''World object, an array of blocks'''
	def __init__(self, width: int, height: int) -> None:
		self.array = [
			[AirBlock() for x in range(width)] for y in range(height)
		]
		self.back = [
			[AirBlock() for x in range(width)] for y in range(height)
		]
		self.width = width
		self.height = height