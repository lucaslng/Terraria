from game.model.entity.entity import Entity
from game.model.world import World
import numpy as np
from random import choice
import pygame as pg

from utils.constants import BIG

_messageGroups = (
	(
		"Hold space near a wall to negate fall damage!",
		"Don't die!",
	),
	(
		"Good luck!",
		"Bye!",
	),
	(
		"Have fun!",
		"See you soon!",
	),
	(
		"Meow",
		"Meoww",
		"Meowww",
	),
)

class Npc(Entity):
	'''non player character entity'''

	def __init__(self, x: float, y: float, world: World, customMessage: tuple[str] | None=None):
		super().__init__(x, y, 5, 1, 1, 20000, 4, 20, 10, 0.99, 18, world)
		self.npcColor: tuple[int, int, int] = tuple(np.random.choice(range(256), size=3))
		if customMessage:
			self.messages = customMessage
		else:
			self.messages = choice(_messageGroups)
		self.currentMessageIndex = 0
		self.interactTime = -BIG
	
	@property
	def currentMessage(self) -> str:
		return self.messages[self.currentMessageIndex % len(self.messages)]
	
	@property
	def isTalking(self) -> bool:
		return pg.time.get_ticks() - self.interactTime <= 3500
	
	def interact(self) -> bool:
		self.currentMessageIndex += 1
		self.interactTime = pg.time.get_ticks() # extend window time
		return super().interact()
	
	def update(self, goal: tuple[float, float]) -> None:
		self.updateFallDamage()
		self.updateVerticalVelocityTime()