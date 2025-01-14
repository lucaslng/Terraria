from utils.constants import SURF
from game.view import surfaces
import utils.colours as colours

def clearScreen():
	SURF.fill(colours.WHITE)
	surfaces.world.fill(colours.CLEAR)
	surfaces.blockBreak.fill(colours.CLEAR)
	surfaces.sunlight.fill(colours.CLEAR)
	surfaces.hud.fill(colours.CLEAR)
