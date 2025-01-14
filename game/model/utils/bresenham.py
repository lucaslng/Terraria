from pygame import Rect
from utils.constants import FRAME
from game.model.blocks.airblock import AirBlock
from game.model.blocks.block import Block
from game.view.conversions import pixel2Coordinate


def bresenham(blocks: list[list[Block]], x0: int, y0: int, x1: int, y1: int, camera: Rect) -> tuple[int, int] | None:
	"""Bresenham's algorithm to detect first non-air block along a line, starting from end point."""
	def plotLineLow(x0, y0, x1, y1):
		dx = abs(x1 - x0)
		dy = abs(y1 - y0)
		xi = -1 if x0 < x1 else 1
		yi = -1 if y0 < y1 else 1
		xii = -1 if x0 < x1 else 1
		yii = -1 if y0 < y1 else 1
		d = (2 * dy) - dx
		y = y1
		x = x1
		while x != x0 - xi:
			coordx, coordy = pixel2Coordinate(x, y, camera)
			blockTouched = blocks[coordy][coordx]
			if not isinstance(blockTouched, AirBlock):
				return coordx, coordy
			if d > 0:
				y += yi
				d += 2 * (dy - dx)
			else:
				d += 2 * dy
			x += xi
			if not 0 <= x < FRAME.width or not 0 <= y < FRAME.height:
				return None
			coordx, coordy = pixel2Coordinate(x, y, camera)
			nextBlock = blocks[coordy][coordx]
			if not isinstance(nextBlock, AirBlock):
				xi = xii
				yi = yii
		return None

	def plotLineHigh(x0: int, y0: int, x1: int, y1: int) -> tuple[int, int] | None:
		dx = abs(x1 - x0)
		dy = abs(y1 - y0)
		xi = -1 if x0 < x1 else 1
		yi = -1 if y0 < y1 else 1
		xii = -1 if x0 < x1 else 1
		yii = -1 if y0 < y1 else 1
		d = (2 * dx) - dy
		x = x1
		y = y1
		while y != y0 - yi:
			coordx, coordy = pixel2Coordinate(x, y, camera)
			blockTouched = blocks[coordy][coordx]
			if not isinstance(blockTouched, AirBlock):
				return coordx, coordy
			if d > 0:
				x += xi
				d += 2 * (dx - dy)
			else:
				d += 2 * dx
			y += yi
			if not 0 <= x < FRAME.width or not 0 <= y < FRAME.height:
				return None
			coordx, coordy = pixel2Coordinate(x, y, camera)
			nextBlock = blocks[coordy][coordx]
			if not isinstance(nextBlock, AirBlock):
				xi = xii
				yi = yii
		return None

	if abs(y1 - y0) < abs(x1 - x0):
		return plotLineLow(x0, y0, x1, y1)
	else:
		return plotLineHigh(x0, y0, x1, y1)