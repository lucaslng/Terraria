from game.model.items.item import Item
from game.textures.sprites import sprites
from game.view import surfaces

import pygame as pg


def drawSlotItem(item: Item, slotSize: int, slotCenter: tuple[int, int]):
	texture = pg.transform.scale(sprites[item.enum], (slotSize - 6, slotSize - 6))
	textureRect = texture.get_rect(center=slotCenter)
	surfaces.hud.blit(texture, textureRect.topleft)