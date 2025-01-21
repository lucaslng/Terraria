from pymunk import Space, Vec2d
from game.model.entity.hasphysics import HasPhysics
from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items
import pygame.mouse as mouse

from utils.constants import FRAME


class Rpg(Item):
	'''RPG gun requested by Rain Li'''

	enum = Items.Rpg
	magSize = 1

	def __init__(self):
		self.ammo = self.magSize
	
	def reload(self):
		self.ammo = self.magSize

class Rocket(HasPhysics):
	'''RPG rocket'''

	def __init__(self, x: float, y: float, space: Space):
		direction = (Vec2d(*mouse.get_pos()) - Vec2d(*FRAME.center)).normalized()
		super().__init__(*(Vec2d(x, y) + direction * 1.4), 3, 1, 1, 0.3, space)
		self.body.apply_impulse_at_local_point(direction * 150)
	
	@property
	def stationary(self) -> bool:
		return -20 < self.body.velocity.x < 20 and -30 < self.body.velocity.y < 20