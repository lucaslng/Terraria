import pygame as pg

from game.model.blocks.block import Block
from game.textures.sprites import sprites
from game.utils.backtint import BACK_TINT
from game.view import conversions, surfaces


def drawBlock(block: Block, x: int, y: int, camera: pg.Rect, isBack: bool = False) -> None:
	'''Draw a singular block'''

	texture = sprites[block.enum].copy()

	if isBack:
		texture.blit(BACK_TINT, (0, 0))

	surfaces.blocks.blit(texture, conversions.coordinate2Pixel(x, y, camera))