import pygame as pg
from constants import font20
from game.view import surfaces
from utils import colours


def drawSlotCount(count: int, slotCenter: tuple[int, int]) -> None:
	countText = font20.render(str(count), True, colours.WHITE)
	surfaces.hud.blit(countText, slotCenter)