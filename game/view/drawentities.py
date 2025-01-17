from pygame import Rect, Surface
from game.model.entity.entities.npc import Npc
from game.model.entity.entity import Entity
from game.textures.animation import Animation
from game.textures.sprites import sprites
from game.view import conversions, surfaces
import pygame as pg


def drawEntities(entities: list[Entity], camera: Rect):
	'''Draw player with animations'''
	# print(round(player.velocity.x, 2), round(player.velocity.y, 2))
	textures: dict[str, Animation] = sprites["cat"]
	# print(type(player.velocity))
	for entity in entities:
		pos = conversions.coordinate2Pixel(*entity.position, camera)
		if -0.05 < entity.velocity.x < 0.05:
			textures["sit"].drawAnimated(surfaces.world, pos)
		else:
			flipped: bool = entity.velocity.x < 0
			if entity.velocity.y < -0.5:
				textures["jump"].drawFrame(surfaces.world, pos, 2, flipped)
			elif entity.velocity.y > 0.5:
				textures["jump"].drawFrame(surfaces.world, pos, 4, flipped)
			else:
				textures["walk"].drawAnimated(surfaces.world, pos, flipped)
		if isinstance(entity, Npc):
			cx, cy = pos
			cx += 3
			cy += 5
			pg.draw.circle(surfaces.world, entity.npcColor, (cx, cy), 3)