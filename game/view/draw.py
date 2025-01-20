from time import perf_counter
from pygame import Rect
from game.view.drawentities import drawEntities
from utils.constants import FRAME, SURF, WIDTH, clock, font16
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

	# time = perf_counter()
	drawSunlight(model.lightmap, camera)
	drawLights(model.lights, camera)
	drawPlayerLight(model.player.lightRadius)
	surfaces.sunlight = transform.smoothscale(surfaces.sunlight, (FRAME.width // 20, FRAME.height // 20))
	surfaces.sunlight = transform.smoothscale(surfaces.sunlight, FRAME.size)
	drawBlocks(model.world, model.blockFacingCoord, camera)
	# print(f'1: {round(perf_counter() - time, 4)}')
	# time = perf_counter()
	drawPlayer(model.player)
	drawEntities(model.entities, camera)
	
	drawMinimap(model.world, model.lightmap, model.lights, camera, (200, 200))
	drawHUD(model, inventories)

	surfaces.minimapLight = transform.smoothscale(surfaces.minimapLight, (surfaces.minimapLight.get_width() // 10, surfaces.minimapLight.get_height() // 10))
	surfaces.minimapLight = transform.smoothscale(surfaces.minimapLight, surfaces.minimap.get_size())
	# print(f'2: {round(perf_counter() - time, 4)}')
	fpsText = f"FPS: {round(clock.get_fps(), 1)}"
	fpsSurf = font16.render(fpsText, True, (255, 0, 0))
	# time = perf_counter()
	SURF.blits((
		(surfaces.world, (0, 0)),
		(surfaces.blockBreak, (0, 0)),
		(surfaces.sunlight, (0, 0)),
		(surfaces.dialogue, (0, 0)),
		(surfaces.hud, (0, 0)),
  	(fpsSurf, (WIDTH - 300, 20)),
		(surfaces.minimap, (WIDTH - 220, 20)),
		(surfaces.minimapLight, (WIDTH - 220, 20)),
	))
	# print(f'3: {round(perf_counter() - time, 4)}')