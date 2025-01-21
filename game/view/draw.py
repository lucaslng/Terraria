from pygame import Rect
from game.events import DRAWEXPLOSION
from game.view.drawentities import drawEntities
from game.view.drawexplosion import drawExplosion
from game.view.drawliquids import drawLiquids
from utils.constants import BLOCK_SIZE, FRAME, SURF, clock, font16
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
from pygame.event import Event

def draw(events: list[Event], model: Model, camera: Rect, inventories: dict[str, tuple[Inventory, int, int, int]]):
	'''Draw everything'''

	drawBlocks(model.world, model.blockFacingCoord, camera)
	drawLiquids(model.liquids, camera)
	drawSunlight(model.lightmap, camera)
	drawLights(model.lights, camera)
	drawPlayerLight(model.player.lightRadius)
	drawPlayer(model.player)
	drawEntities(model.entities, camera)

	for event in events:
		if event.type == DRAWEXPLOSION:
			drawExplosion(event.pos, event.radius, event.width, camera)
	
	drawMinimap(model.world, model.lightmap, model.lights, camera, (200, 200))
	drawHUD(model, inventories)

	surfaces.sunlight = transform.smoothscale(surfaces.sunlight, (FRAME.width // 20, FRAME.height // 20))
	surfaces.sunlight = transform.smoothscale(surfaces.sunlight, FRAME.size)

	surfaces.minimapLight = transform.smoothscale(surfaces.minimapLight, (surfaces.minimapLight.get_width() // 10, surfaces.minimapLight.get_height() // 10))
	surfaces.minimapLight = transform.smoothscale(surfaces.minimapLight, surfaces.minimap.get_size())
 
	fpsText = f"FPS: {round(clock.get_fps(), 1)}"
	fpsSurf = font16.render(fpsText, True, (255, 0, 0))

	surfaces.everything.blits((
		(surfaces.world, (0, 0)),
		(surfaces.blockBreak, (0, 0)),
		(surfaces.sunlight, (0, 0)),
		(surfaces.hud, (0, 0)),
		(surfaces.hotbar, (FRAME.centerx - (13.5 * BLOCK_SIZE) // 2, FRAME.height - int(2.25 * BLOCK_SIZE))),
  		(fpsSurf, (FRAME.width - 300, 20)),
		(surfaces.minimap, (FRAME.width - 220, 20)),
		(surfaces.minimapLight, (FRAME.width - 220, 20)),
	))
 
	SURF.blit(surfaces.everything, (0, 0))