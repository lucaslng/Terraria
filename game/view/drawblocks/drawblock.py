import pygame as pg

from constants import BLOCK_RECT
from game.model.blocks.block import Block
from game.textures.sprites import sprites
from game.utils.backtint import BACK_TINT
from game.view import conversions, surfaces


def drawBlock(block: Block, x: int, y: int, camera: pg.Rect, isBack: bool = False) -> None:
	'''Draw a singular block'''

	texture = sprites[block.enum].copy()

	if isBack:
		texture.blit(BACK_TINT, (0, 0))
	
	rect = BLOCK_RECT.copy()
	rect.topleft = conversions.coordinate2Pixel(x, y, camera)

	surfaces.world.blit(texture, rect)

	breakingRect = rect.copy().scale_by(
		block.amountBroken / block.hardness, block.amountBroken / block.hardness
	)

	pg.draw.rect(surfaces.blockBreak, (0, 0, 0, 100), breakingRect)

	