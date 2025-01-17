from pygame import Rect
from utils.constants import FRAME
from game.model.blocks.airblock import AirBlock
from game.model.blocks.block import Block
from game.view.conversions import pixel2Coordinate


def bresenham(blocks: list[list[Block]], x0: int, y0: int, x1: int, y1: int, camera: Rect) -> tuple[int, int] | None:
	'''Bresenham's algorithm to detect first non-air block along a line, starting from end point.'''
	def plotLineLow(x0: int, y0: int, x1: int, y1: int) -> tuple[int, int] | None: # shallow line
		dx = abs(x1 - x0)
		dy = abs(y1 - y0)
		xi = -1 if x0 < x1 else 1 # x step direction
		yi = -1 if y0 < y1 else 1 # y step direction
		d = (2 * dy) - dx # decision variable 2dy - dx
		y = y1 # start at the endpoint
		x = x1
		while x != x0 - xi: # loop, iterates backward from the endpoint
			coordx, coordy = pixel2Coordinate(x, y, camera)
			if not 0 <= x < FRAME.width or not 0 <= y < FRAME.height or not 0 <= coordy < len(blocks) or not 0 <= coordx < len(blocks[0]):
				return None
			if not isinstance(blocks[coordy][coordx], AirBlock):
				return coordx, coordy
			# is the next ideal point closer to the current row/column, or should we move diagonally to stay closer to the real line?
			if d > 0: # take a diagonal step, adjusting both x and y
				y += yi
				d += 2 * (dy - dx)
			else: # take a straight step by only adjusting x
				d += 2 * dy
			x += xi # iterates in steps of xi
		return None

	def plotLineHigh(x0: int, y0: int, x1: int, y1: int) -> tuple[int, int] | None: # steep line, same as the plotLineLow function but x and y are swapped
		dx = abs(x1 - x0)
		dy = abs(y1 - y0)
		xi = -1 if x0 < x1 else 1
		yi = -1 if y0 < y1 else 1
		d = (2 * dx) - dy
		x = x1
		y = y1
		while y != y0 - yi:
			coordx, coordy = pixel2Coordinate(x, y, camera)
			if not 0 <= x < FRAME.width or not 0 <= y < FRAME.height or not 0 <= coordy < len(blocks) or not 0 <= coordx < len(blocks[0]):
				return None
			if not isinstance(blocks[coordy][coordx], AirBlock):
				return coordx, coordy
			if d > 0:
				x += xi
				d += 2 * (dx - dy)
			else:
				d += 2 * dx
			y += yi
		return None

	if abs(y1 - y0) < abs(x1 - x0):
		return plotLineLow(x0, y0, x1, y1) # shallow line, if dy < dx
	else:
		return plotLineHigh(x0, y0, x1, y1) # steep line, if dy > dx