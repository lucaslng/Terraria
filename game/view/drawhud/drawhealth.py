import math
from utils.constants import BLOCK_SIZE
from game.textures.sprites import sprites
from game.view import surfaces

spacing = BLOCK_SIZE

def drawHealth(health: float, maxHealth: int) -> None:
	'''Draw player hearts on screen'''

	fullHearts = int(health // 2)
	halfHeart = int(health % 2)
	emptyHearts = maxHealth // 2 - fullHearts - halfHeart

	#Full hearts
	for i in range(fullHearts):
		surfaces.health.blit(sprites["full heart"], (i * spacing, 0))
	
	#Half hearts
	if halfHeart:
		surfaces.health.blit(sprites["half heart"], (fullHearts * spacing, 0))

	#Empty hearts
	for i in range(emptyHearts):
		surfaces.health.blit(sprites["empty heart"], ((fullHearts + halfHeart + i) * spacing, 0))
