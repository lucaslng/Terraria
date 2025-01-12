from game.model.model import Model
from game.view.drawhud.drawhealth import drawHealth
from game.view.drawhud.drawhotbar import drawHotbar
from game.view.drawhud.drawplayerinventory import drawPlayerInventory


def drawHUD(model: Model):
	'''Draw HUD'''

	drawHealth(model.player.health, model.player.maxHealth)
	drawPlayerInventory(model.player.inventory)  # noqa: F821
	drawHotbar(model.player.hotbar, model.player.heldSlotIndex)