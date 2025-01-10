from constants import ASURF, SUNLIGHTSURF, SURF, OVERLAY, LIGHTSURF
import utils.colors as colors

def clearScreen():
	SURF.fill(colors.WHITE)
	ASURF.fill(colors.CLEAR)
	OVERLAY.fill(colors.CLEAR)
	SUNLIGHTSURF.fill(colors.CLEAR)
	LIGHTSURF.fill(colors.CLEAR)