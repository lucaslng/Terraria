from constants import ASURF, SUNLIGHTSURF, SURF, OVERLAY, LIGHTSURF
from game.view import surfaces
import utils.colours as colours

def clearScreen():
	SURF.fill(colours.WHITE)
	ASURF.fill(colours.CLEAR)
	OVERLAY.fill(colours.CLEAR)
	SUNLIGHTSURF.fill(colours.CLEAR)
	LIGHTSURF.fill(colours.CLEAR)
	surfaces.sunlight.fill(colours.CLEAR)
	surfaces.blocks.fill(colours.CLEAR)
	surfaces.hud.fill(colours.CLEAR)
