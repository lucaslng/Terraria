from pygame import Rect
from game.model.model import Model
from game.view.drawblocks.drawblocks import drawBlocks
from game.view.drawhud.drawhud import drawHUD
from game.view.drawplayer import drawPlayer
from game.view.drawsunlight import drawSunlight

def draw(model: Model, camera: Rect):
	'''Draw everything'''

	drawBlocks(model.world, model.blockFacingCoord, camera)
	drawSunlight(model.lightmap, camera)
	drawPlayer(model.player)
	drawHUD(model)