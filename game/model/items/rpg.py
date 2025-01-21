from pymunk import Space
from game.model.entity.hasphysics import HasPhysics
from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items


class Rpg(Item):
	'''RPG gun requested by Rain Li'''

	enum = Items.Rpg
	magSize = 1

	def __init__(self):
		self.reload()
	
	def reload(self):
		self.ammo = self.magSize

class Rocket(HasPhysics):
	'''RPG rocket'''

	def __init__(self, x: float, y: float, space: Space):
		super().__init__(x, y, 2, 1, 1, 0.3, space)
		self.body.apply_impulse_at_local_point((120, 0))
	
	@property
	def stationary(self) -> bool:
		return -20 < self.body.velocity.x < 20 and -20 < self.body.velocity.y < 20