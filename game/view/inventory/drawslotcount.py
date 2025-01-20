from pygame import Surface
from utils.constants import font12
from game.view import surfaces
from utils import colours


def drawSlotCount(surface: Surface, count: int, slotCenter: tuple[int, int]) -> None:
	countText = font12.render(str(count), True, colours.WHITE)
	surface.blit(countText, slotCenter)