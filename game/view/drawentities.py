from pygame import Rect, Surface
from game.model.entity.entities.npc import Npc
from game.model.entity.entities.rabbit import Rabbit
from game.model.entity.entity import Entity
from game.textures.animation import Animation
from game.textures.sprites import sprites
from game.view import conversions, surfaces
import pygame as pg

from game.view.wraptext import drawText
from utils import colours
from utils.constants import BLOCK_SIZE, font12

def drawNpc(npc: Npc, pos: tuple[int, int]) -> None:
	textures: dict[str, Animation] = sprites["cat"]
	
	if -0.05 < npc.velocity.x < 0.05:
		textures["sit"].drawAnimated(surfaces.world, pos)
	else:
		flipped: bool = npc.velocity.x < 0
		if npc.velocity.y < -0.5:
			textures["jump"].drawFrame(surfaces.world, pos, 2, flipped)
		elif npc.velocity.y > 0.5:
			textures["jump"].drawFrame(surfaces.world, pos, 4, flipped)
		else:
			textures["walk"].drawAnimated(surfaces.world, pos, flipped)
	x, y = pos
	pg.draw.circle(surfaces.world, npc.npcColor, (x + 3, y + 5), 3)

	if npc.isTalking:
		dialogueRect = Rect(x - 0.5 * BLOCK_SIZE, y - 1.8 * BLOCK_SIZE, BLOCK_SIZE * 2.8, BLOCK_SIZE * 1.5)
		pg.draw.rect(surfaces.dialogue, (240, 240, 240, 210), dialogueRect, border_radius=4)
		pg.draw.rect(surfaces.dialogue, colours.BLACK, dialogueRect, width=1, border_radius=4)
		textRect = dialogueRect.scale_by(0.9, 0.9)
		drawText(surfaces.dialogue, npc.currentMessage, textRect, font12)

def drawRabbit(rabbit: Rabbit, pos: tuple[int, int]) -> None:
	texture: Surface = sprites["rabbit"]
	texture = pg.transform.scale(texture, (rabbit.width * BLOCK_SIZE, rabbit.height * BLOCK_SIZE))
	if rabbit.velocity.x < 0.05:
		texture = pg.transform.flip(texture, True, False)
	surfaces.world.blit(texture, texture.get_rect(center=pos))

def drawEntities(entities: list[Entity], camera: Rect):
	'''Draw entities'''
	
	for entity in entities:
		pos = conversions.coordinate2Pixel(*entity.position, camera)
		if isinstance(entity, Npc):
			drawNpc(entity, pos)
		elif isinstance(entity, Rabbit):
			drawRabbit(entity, pos)