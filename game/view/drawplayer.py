from utils.constants import FRAME
from game.model.entity.entities.player import Player
from game.textures.animation import Animation
from game.textures.sprites import sprites
from game.view import surfaces


def drawPlayer(player: Player):
	'''Draw player with animations'''
	
	# print(round(player.body.velocity.x, 2), round(player.body.velocity.y, 2))
	textures: dict[str, Animation] = sprites["cat"]
	hurt = player.invulnerabilityFrames > 0
	if -0.05 < player.body.velocity.x < 0.05:
		textures["sit"].drawAnimated(surfaces.world, FRAME.center, hurt)
	else:
		flipped: bool = player.body.velocity.x < 0
		if player.body.velocity.y < -0.5:
			textures["jump"].drawFrame(surfaces.world, FRAME.center, 2, flipped, hurt)
		elif player.body.velocity.y > 0.5:
			textures["jump"].drawFrame(surfaces.world, FRAME.center, 4, flipped, hurt)
		else:
			textures["walk"].drawAnimated(surfaces.world, FRAME.center, flipped, hurt)