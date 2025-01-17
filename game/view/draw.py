from pygame import Rect
from game.view.drawentities import drawEntities
from utils.constants import FRAME, SURF, WIDTH
from game.model.items.inventory.inventory import Inventory
from game.model.model import Model
from game.view import surfaces
from game.view.drawblocks.drawblocks import drawBlocks
from game.view.drawhud.drawhud import drawHUD
from game.view.drawhud.drawminimap import drawMinimap
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
	drawEntities(model.entities, camera)
	
	drawMinimap(model.world, model.lightmap, model.lights, camera, (200, 200))
	drawHUD(model, inventories)

	surfaces.sunlight = transform.smoothscale(surfaces.sunlight, (FRAME.width // 15, FRAME.height // 20))
	surfaces.sunlight = transform.smoothscale(surfaces.sunlight, FRAME.size)

	SURF.blits((
		(surfaces.world, (0, 0)),
		(surfaces.blockBreak, (0, 0)),
		(surfaces.sunlight, (0, 0)),
		(surfaces.hud, (0, 0)),
		(surfaces.minimap, (WIDTH - 220, 20)),
		(surfaces.minimapLight, (WIDTH - 220, 20))
	))