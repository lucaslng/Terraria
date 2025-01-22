from pygame import Rect
from utils.constants import FRAME
from game.model.blocks.airblock import AirBlock
from game.model.blocks.block import Block
from game.view.conversions import pixel2Coordinate


def bresenham(blocks: list[list[Block]], x0: int, y0: int, x1: int, y1: int, camera: Rect) -> tuple[int, int] | None:
	'''Bresenham's algorithm to detect first non-air block along a line, starting from (x0, y0) and ending at (x1, y1).'''
	
	dx = abs(x1 - x0)
	dy = -abs(y1 - y0)
	xi = 1 if x0 < x1 else -1 # x step direction
	yi = 1 if y0 < y1 else -1 # y step direction
	d = dx + dy
	# d is the decision variable
	while x0 != x1 or y0 != y1: # loop, iterates backward from the endpoint

		# check for collision with a block / if the position is out of the frame
		coordx, coordy = pixel2Coordinate(x0, y0, camera)
		if not 0 <= x0 < FRAME.width or not 0 <= y0 < FRAME.height or not 0 <= coordy < len(blocks) or not 0 <= coordx < len(blocks[0]):
			return None
		if not isinstance(blocks[coordy][coordx], AirBlock):
			return coordx, coordy
		
		# is the next ideal point closer to the current row or column?
		if 2 * d - dy > dx - 2 * d: # only adjusting x
			d += dy
			x0 += xi
		else: # only adjusting y
			d += dx
			y0 += yi
	return None