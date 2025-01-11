from math import ceil, floor
import math
import time
from game.model.blocks.block import Block
from game.model.entity.hasphysics import HasPhysics
from game.model.world import World


class Entity(HasPhysics):
	'''Base class for all entities'''

	def __init__(self,
							x: float,
							y: float,
							mass: float,
							width: float,
							height: float,
							walkForce: float,
							walkSpeed: float,
							jumpImpulse: float,
							jumpSpeed: float,
							friction: float,
							world: World,
							):
		super().__init__(x, y, mass, width, height)
		self.walkForce = walkForce
		self.walkSpeed = walkSpeed
		self.jumpImpulse = jumpImpulse
		self.jumpSpeed = jumpSpeed
		self.previousJumpTime = 0
		self.friction = friction
		self.world = world
		self.minyvelo = 100
	
	def walkLeft(self) -> None:
		'''Walk the entity to the left using walkForce'''
		if -self.velocity.x < self.walkSpeed:
			self.apply_force_at_local_point((-self.walkForce, 0))
	
	def walkRight(self) -> None:
		'''Walk the entity to the right using walkForce'''
		if self.velocity.x < self.walkSpeed:
			self.apply_force_at_local_point((self.walkForce, 0))
	
	def jump(self) -> None:
		'''Jump the entity using jumpForce'''
		if self.isOnGround() and time.time() - self.previousJumpTime > 0.1:
			self.apply_impulse_at_local_point((0, -self.jumpImpulse))
			self.previousJumpTime = time.time()

	def isOnGround(self) -> bool:
		if (self.position.y - self.height / 2) % 1 < 0.05:
			return not (self.world[ceil(self.position.y)][floor(self.position.x)].isEmpty and self.world[ceil(self.position.y)][ceil(self.position.x)].isEmpty)
		return False

	def update(self) -> None:
		print((self.position.y - self.height / 2) % 1)
		pass