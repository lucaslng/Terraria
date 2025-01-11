from constants import BLOCK_SIZE, FRAME
from game.model.model import Model
from game.view.drawblocks import drawBlocks
from game.view.drawhud.drawhud import drawHUD
from game.view.drawplayer import drawPlayer
from game.view.drawsunlight import drawSunlight

def draw(model: Model):
	'''Draw everything'''

	camera = FRAME.copy()
	camera.center = model.player.position[0] * BLOCK_SIZE, model.player.position[1] * BLOCK_SIZE
	drawBlocks(model.world, camera)
	drawSunlight(model.lightmap, camera)
	drawPlayer(model.player)
	drawHUD(model)