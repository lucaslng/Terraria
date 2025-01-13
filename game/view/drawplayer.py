from constants import FRAME
from game.model.entity.entities.player import Player
from game.textures.animation import Animation
from game.textures.sprites import sprites
from game.view import surfaces


def drawPlayer(player: Player):
	'''Draw player with animations'''
	
	# print(round(player.velocity.x, 2), round(player.velocity.y, 2))
	textures: dict[str, Animation] = sprites["cat"]

	if -0.05 < player.velocity.x < 0.05:
		textures["sit"].drawAnimated(surfaces.world, FRAME.center)
	else:
		flipped: bool = player.velocity.x < 0
		if player.velocity.y < -0.5:
			textures["jump"].drawFrame(surfaces.world, FRAME.center, 2, flipped)
		elif player.velocity.y > 0.5:
			textures["jump"].drawFrame(surfaces.world, FRAME.center, 4, flipped)
		else:
			textures["walk"].drawAnimated(surfaces.world, FRAME.center, flipped)