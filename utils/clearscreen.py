from constants import SURF
from game.view import surfaces
import utils.colours as colours

def clearScreen():
	SURF.fill(colours.WHITE)
	surfaces.sunlight.fill(colours.CLEAR)
	surfaces.blocks.fill(colours.CLEAR)
	surfaces.hud.fill(colours.CLEAR)
