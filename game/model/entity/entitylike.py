from typing import Protocol

from pymunk import Space

from game.model.world import World


class EntityLike(Protocol):
	def __init__(self, x: float, y: float, world: World, space: Space):
		...

	def interact(self, damage: float) -> bool:
		...
	
	def takeDamage(self, damage: float) -> bool:
		...
	
	def update(self, goal: tuple[float, float]) -> None:
		...