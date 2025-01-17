from math import ceil, degrees, dist, floor, atan2, pi
import time
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
							maxHealth: int,
							world: World,
							):
		super().__init__(x, y, mass, width, height)
		self.walkForce = walkForce
		self.walkSpeed = walkSpeed
		self.jumpImpulse = jumpImpulse
		self.jumpSpeed = jumpSpeed
		self.previousJumpTime = 0
		self.friction = friction
		self.maxHealth = maxHealth
		self.health = maxHealth
		self.world = world
		self.minyvelo = 100
		self.updateDistance = 1
	
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

	def update(self, goal: tuple[float, float]) -> None:
		'''weird variation of a* algorithm'''
		# find reachable blocks
		if dist(self.position, goal) > self.updateDistance:
			x, y = map(int, self.position)
			reachables = {(x, y)}
			if self.world[y][x - 1].isEmpty:
				reachables.add((x - 1, y))
			if self.world[y][x + 1].isEmpty:
				reachables.add((x + 1, y))
			best = min(reachables, key=lambda p: dist(p, goal))
			if best != (x, y):
				if best[0] < x:
					self.walkLeft()
				else:
					self.walkRight()
		

	def interact(self) -> None:
		'''interact with the entity using keys.interactEntity'''
		pass