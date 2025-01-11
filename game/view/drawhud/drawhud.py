from constants import SURF
from game.model.model import Model
from game.view import surfaces
from game.view.drawhud.drawhealth import drawHealth
from game.view.drawhud.drawhotbar import drawHotbar
from game.view.drawhud.drawplayerinventory import drawPlayerInventory


def drawHUD(model: Model):
	'''Draw hud'''
	drawHealth(model.player.health)
	drawPlayerInventory(model.player.inventory)  # noqa: F821
	drawHotbar(model.player.hotbar, model.player.heldSlotIndex)
	SURF.blit(surfaces.hud, (0,0))