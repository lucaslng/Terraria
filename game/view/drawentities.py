from math import degrees
from pygame import BLEND_MULT, Rect, Surface
from game.model.entity.entities.dog import Dog
from game.model.entity.entities.npc import Npc
from game.model.entity.entities.rabbit import Rabbit
from game.model.entity.hasphysics import HasPhysics
from game.model.items.rpg import Rocket
from game.textures.animation import Animation
from game.textures.sprites import sprites
from game.view import conversions, surfaces
import pygame as pg

from game.view.wraptext import drawText
from utils import colours
from utils.constants import BLOCK_SIZE, FRAME, font12

def drawNpc(npc: Npc, pos: tuple[int, int]) -> None:
	textures: dict[str, Animation] = sprites["cat"]
	hurt = npc.invulnerabilityFrames > 0
	if -0.05 < npc.body.velocity.x < 0.05:
		textures["sit"].drawAnimated(surfaces.world, pos, hurt)
	else:
		flipped: bool = npc.body.velocity.x < 0
		if npc.body.velocity.y < -0.5:
			textures["jump"].drawFrame(surfaces.world, pos, 2, flipped, hurt)
		elif npc.body.velocity.y > 0.5:
			textures["jump"].drawFrame(surfaces.world, pos, 4, flipped, hurt)
		else:
			textures["walk"].drawAnimated(surfaces.world, pos, flipped, hurt)
	x, y = pos
	pg.draw.circle(surfaces.world, npc.npcColor, (x + 3, y + 5), 3)

	if npc.isTalking:
		dialogueRect = Rect(x - 0.5 * BLOCK_SIZE, y - 1.8 * BLOCK_SIZE, BLOCK_SIZE * 2.8, BLOCK_SIZE * 1.5)
		pg.draw.rect(surfaces.world, (240, 240, 240), dialogueRect, border_radius=4)
		pg.draw.rect(surfaces.world, colours.BLACK, dialogueRect, width=1, border_radius=4)
		textRect = dialogueRect.scale_by(0.9, 0.9)
		drawText(surfaces.world, npc.currentMessage, textRect, font12)

def drawRabbit(rabbit: Rabbit, pos: tuple[int, int]) -> None:
	hurt = rabbit.invulnerabilityFrames > 0
	texture: Surface = sprites["rabbit"]
	texture = pg.transform.scale(texture, (rabbit.width * BLOCK_SIZE, rabbit.height * BLOCK_SIZE))
	if rabbit.body.velocity.x < 0.05:
		texture = pg.transform.flip(texture, True, False)
	if hurt:
		texture.fill((colours.HURT), special_flags=BLEND_MULT)
	surfaces.world.blit(texture, texture.get_rect(center=pos))

def drawDog(dog: Dog, pos: tuple[int, int]) -> None:
	texture: Animation = sprites["dog"]
	hurt = dog.invulnerabilityFrames > 0
	if -0.05 < dog.body.velocity.x < 0.05:
		texture.drawFrame(surfaces.world, pos, 1, pos[0] > FRAME.centerx, hurt)
	else:
		texture.drawAnimated(surfaces.world, pos, pos[0] > FRAME.centerx, hurt)

def drawRocket(rocket: Rocket, pos: tuple[int, int]):
	texture = sprites["rocket"]
	texture = pg.transform.rotate(texture, degrees(rocket.body.angle))
	surfaces.world.blit(texture, texture.get_rect(center=pos))


def drawEntities(entities: list[HasPhysics], camera: Rect):
	'''Draw entities'''
	
	for entity in entities:
		pos = conversions.coordinate2Pixel(*entity.body.position, camera)
		if isinstance(entity, Npc):
			drawNpc(entity, pos)
		elif isinstance(entity, Rabbit):
			drawRabbit(entity, pos)
		elif isinstance(entity, Dog):
			drawDog(entity, pos)
		elif isinstance(entity, Rocket):
			drawRocket(entity, pos)