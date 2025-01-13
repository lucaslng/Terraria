from constants import FRAME
from game.model.entity.entities.player import Player
from game.textures.animation import Animation
from game.textures.sprites import sprites
from game.view import surfaces


def drawPlayer(player: Player):
	# texture: pg.Surface = sprites["cat"]["walk"][0]
	textures: dict[str, Animation] = sprites["cat"]
	# texture = pg.transform.scale2x(texture)
	# surfaces.world.blit(texture, texture.get_rect(center=FRAME.center))

	if -0.1 < player.velocity.x < 0.1:
		textures["sit"].drawAnimated(surfaces.world, FRAME.center)
	else:
		flipped: bool = player.velocity.x < 0
		
		if player.velocity.y < -0.9:
			textures["jump"].drawFrame(surfaces.world, FRAME.center, 2, flipped)
		elif player.velocity.y > 0.9:
			textures["jump"].drawFrame(surfaces.world, FRAME.center, 4, flipped)
		else:
			textures["walk"].drawAnimated(surfaces.world, FRAME.center, flipped)
	

	# flipped = player.velocity.x < 0

	# if player.velocity.y < -4:
	# 	sprites["cat"]["jump"].drawFrame(FRAME.center, 2, flipped)
	# el