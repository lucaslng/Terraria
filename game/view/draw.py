from pygame import Rect
from utils.constants import FRAME, SURF
from game.model.items.inventory.inventory import Inventory
from game.model.model import Model
from game.view import surfaces
from game.view.drawblocks.drawblocks import drawBlocks
from game.view.drawhud.drawhud import drawHUD
from game.view.drawlights import drawLights, drawPlayerLight
from game.view.drawplayer import drawPlayer
from game.view.drawsunlight import drawSunlight
from pygame import transform

def draw(model: Model, camera: Rect, inventories: dict[str, tuple[Inventory, int, int, int]]):
	'''Draw everything'''

	drawBlocks(model.world, model.blockFacingCoord, camera)
	drawSunlight(model.lightmap, camera)
	drawLights(model.lights, camera)
	drawPlayerLight(model.player.lightRadius)
	drawPlayer(model.player)
	drawHUD(model, inventories)

	surfaces.sunlight = transform.smoothscale(surfaces.sunlight, (FRAME.width // 15, FRAME.height // 20))
	surfaces.sunlight = transform.smoothscale(surfaces.sunlight, FRAME.size)

	SURF.blits((
		(surfaces.world, (0, 0)),
		(surfaces.blockBreak, (0, 0)),
		(surfaces.sunlight, (0, 0)),
		(surfaces.hud, (0, 0))
	))