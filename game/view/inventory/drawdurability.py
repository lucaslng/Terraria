from pygame import Surface
import pygame as pg


def drawDurability(surface: Surface, durability: int, startingDurability: int, slotSize: int, slotCenter: tuple[int, int]) -> None:
	'''draw durability bar for items'''

	if durability == startingDurability:
		return
	
	# print(durability, startingDurability)
	
	height = slotSize // 11
	width = int(slotSize * 0.88)
	
	y = slotCenter[1] + int(slotSize * 0.38)
	x = slotCenter[0] - int(slotSize * 0.44)

	percent = durability / startingDurability

	if percent > 0.6:
		colour = (0, 255, 0)
	elif percent > 0.3:
		colour = (255, 165, 0)
	else:
		colour = (255, 0, 0)
	
	pg.draw.rect(surface, (50, 50, 50), (x, y, width, height))
	pg.draw.rect(surface, colour, (x, y, int(width * percent), height))