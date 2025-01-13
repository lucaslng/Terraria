from pygame import Rect
from constants import SURF
from game.model.items.inventory.inventory import Inventory
from game.model.model import Model
from game.view import surfaces
from game.view.drawblocks.drawblocks import drawBlocks
from game.view.drawhud.drawhud import drawHUD
from game.view.drawplayer import drawPlayer
from game.view.drawsunlight import drawSunlight

def draw(model: Model, camera: Rect, inventories: dict[str, tuple[Inventory, int, int, int]]):
	'''Draw everything'''

	drawBlocks(model.world, model.blockFacingCoord, camera)
	drawSunlight(model.lightmap, camera)
	drawPlayer(model.player)
	drawHUD(model, inventories)


	SURF.blits((
		(surfaces.world, (0, 0)),
		(surfaces.blockBreak, (0, 0)),
		(surfaces.sunlight, (0, 0)),
		(surfaces.hud, (0, 0))
	))