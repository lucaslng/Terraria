import pygame as pg

from constants import FRAME
from game.model.entity.entities.player import Player
from game.textures.sprites import sprites
from game.view import surfaces


def drawPlayer(player: Player):
	texture: pg.Surface = sprites["cat"]["walk"][0]
	texture = pg.transform.scale2x(texture)
	surfaces.world.blit(texture, (FRAME.centerx - texture.get_width() // 2, FRAME.centery - texture.get_height()//2))