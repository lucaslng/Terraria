from utils.constants import BLOCK_SIZE
from game.textures.sprites import sprites
from game.view import surfaces


def drawHealth(health: float, maxHealth: int) -> None:
	'''Draw player hearts on screen'''

	spacing = BLOCK_SIZE
	x = y = 10

	fullHearts = int(health // 2)
	halfHeart = int(health % 2)
	emptyHearts = maxHealth // 2 - fullHearts - halfHeart

	#Full hearts
	for i in range(fullHearts):
		surfaces.hud.blit(sprites["full heart"], (x + i * spacing, y))
	
	#Half hearts
	if halfHeart:
		surfaces.hud.blit(sprites["half heart"], (x + fullHearts * spacing, y))

	#Empty hearts
	for i in range(emptyHearts):
		surfaces.hud.blit(sprites["empty heart"], (x + (fullHearts + halfHeart + i) * spacing, y))
