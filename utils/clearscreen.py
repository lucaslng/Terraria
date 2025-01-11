from constants import ASURF, SUNLIGHTSURF, SURF, OVERLAY, LIGHTSURF
from game.view import surfaces
import utils.colors as colors

def clearScreen():
	SURF.fill(colors.WHITE)
	ASURF.fill(colors.CLEAR)
	OVERLAY.fill(colors.CLEAR)
	SUNLIGHTSURF.fill(colors.CLEAR)
	LIGHTSURF.fill(colors.CLEAR)
	surfaces.sunlight.fill(colors.CLEAR)
	surfaces.blocks.fill(colors.CLEAR)