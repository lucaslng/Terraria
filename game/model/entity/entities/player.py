from game.model.entity.entity import Entity
from game.textures.sprites import sprites

class Player(Entity):
	'''Player entity class'''
	
	def __init__(self, x: float, y: float):
		super().__init__(x=x, y=y, mass=4, width=1, height=1)