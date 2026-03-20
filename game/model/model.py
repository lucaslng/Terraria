from math import dist
import pygame as pg
import math
import random
import pymunk as pm
import numpy as np
import time
from pymunk import Space
from typing import Optional, Type
from scipy.ndimage import distance_transform_cdt

from game.events import DRAWEXPLOSION, REMOVEINVENTORYTYPE
from game.model.blocks.diamondoreblock import DiamondOreBlock
from game.model.blocks.flowerblocks import AlliumBlock, CornflowerBlock, DandelionBlock, PoppyBlock
from game.model.blocks.goldoreblock import GoldOreBlock
from game.model.entity.entities.dog import Dog
from game.model.entity.entities.npc import Npc
from game.model.entity.entities.rabbit import Rabbit
from game.model.entity.entitylike import EntityLike
from game.model.entity.hasphysics import HasPhysics
from game.model.items.bucket import Bucket
from game.model.items.rpg import Rocket, Rpg
from game.model.liquids.liquid import Liquid
from game.model.utils.biomesenum import Biome
from sound.sounds import sounds
from utils.constants import DOG_RARITY, FIRST_MESSAGE, FPS, NPC_RARITY, RABBIT_RARITY, ENTITY_WAKE_RADIUS, CHUNK_SIZE, CHUNK_LOAD_RADIUS
from game.model.blocks.utils.blocksenum import Blocks 
from game.model.blocks.airblock import AirBlock
from game.model.blocks.coaloreblock import CoalOreBlock
from game.model.blocks.dirtblock import DirtBlock
from game.model.blocks.grassblock import GrassBlock
from game.model.blocks.ironoreblock import IronOreBlock
from game.model.blocks.leavesblock import LeavesBlock
from game.model.blocks.oaklogblock import LogBlock
from game.model.blocks.stoneblock import StoneBlock
from game.model.blocks.utils.block2item import block2Item
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.entity.entities.player import Player
from game.model.items.specialitems.placeable import Placeable
from game.model.items.specialitems.tool import Tool
from game.model.light import Light
from game.model.physics.keepupright import keepUpright
from game.model.utils.adddefaultitems import add_default_items
from game.model.utils.noisesenum import Noises
from game.model.world import World
from game.model.entity.entity import Entity
from utils.simplexnoise import SimplexNoise


class Model:
	'''Handles all game logic'''
	def __init__(self, worldWidth: int, worldHeight: int, _from_save: bool = False):
		self.space = Space()
		self.world_width = worldWidth
		self.space.sleep_time_threshold = 2
		self.world = World(worldWidth, worldHeight)
		self.player = Player(0, 0, self.world, self.space)

		self.lightmap = np.zeros((worldHeight, worldWidth), dtype=np.int16)
		self.liquids: list[Liquid] = []
		self.entities: list[HasPhysics] = []
		self.entity_counter: dict[Type[Entity], int] = {
			Rabbit: 0,
			Dog: 0,
		}

		self.pending_entities: list[tuple] = []

		self.lights: list[tuple[Light, int, int]] = []
		self.space.gravity = 0, 20
		self.world_body = pm.Body(body_type=pm.Body.STATIC)
		self.space.add(self.world_body)
		self._generate_boundary_shapes()
		self.block_facing_coord: tuple[int, int] | None = None

		if not _from_save:
			self._generate()
			add_default_items(self.player)

	def update(self, steps=4) -> bool:
		'''
		Update the model - called every frame. 
		Steps increases the accuracy of the physics simulation but sacrifices performance.
		'''

		self.updateChunkShapes()
		self._updatePendingEntities()

		self.player.update()

		if not self.player.isAlive:
			return False

		player_pos = self.player.body.position
		to_delete = []   # collect (i, entity) — process after loop

		for i, entity in enumerate(self.entities):
			if isinstance(entity, Entity):
				entity_dist = dist(entity.body.position, player_pos)

				if entity_dist > ENTITY_WAKE_RADIUS:
					if not entity.body.is_sleeping:
						entity.body.sleep()
					continue

				if entity.body.is_sleeping:
					entity.body.activate()

				entity.update(player_pos)

				if isinstance(entity, Dog) and entity_dist < 1.5:
					if self.player.takeDamage(1):
						self.player.body.apply_impulse_at_local_point(
							(player_pos - entity.body.position) * 30, (0, 0.5)
						)

				if not entity.isAlive:
					to_delete.append((i, entity))
					continue

			elif isinstance(entity, Rocket):
				if entity.stationary:
					pg.event.post(pg.event.Event(DRAWEXPLOSION, pos=entity.body.position, radius=0.5, width=8))
					sounds["rpg"]["explosion"].play()
					ex, ey = list(map(int, entity.body.position))
					for y in range(max(0, ey - 3), min(self.world.height, ey + 4)):
						for x in range(max(0, ex - 3), min(self.world.width, ex + 4)):
							self.removeBlock(x, y)
					for otherEntity in self.entities:
						if isinstance(otherEntity, Entity) and dist(otherEntity.body.position, entity.body.position) <= 3:
							otherEntity.takeDamage(10)
					to_delete.append((i, entity))
					continue

			if not 0 < entity.body.position.x < self.world.width or not 0 < entity.body.position.y < self.world.height:
				to_delete.append((i, entity))

		# Delete in reverse index order so earlier indices stay valid
		for i, entity in reversed(to_delete):
			self.deleteEntity(i, entity)

		if isinstance(self.player.heldSlot.item, Bucket) and self.player.heldSlot.item.filledAmount < 1:
			for i, liquid in enumerate(self.liquids):
				for p, liquidParticle in enumerate(liquid.particles):
					if dist(liquidParticle.body.position, player_pos) < 1.5:
						if self.player.heldSlot.item.liquid is None:
							self.player.heldSlot.item.liquid = liquidParticle.liquid
						if self.player.heldSlot.item.liquid == liquidParticle.liquid and self.player.heldSlot.item.filledAmount < 1:
							self.player.heldSlot.item.fill(1 / self.player.heldSlot.item.liquid.particleCount)
							del self.liquids[i].particles[p]

		for i in range(steps):
			self.space.step((1 / FPS) / steps)
			keepUpright(self.player.body)
			for entity in self.entities:
				if isinstance(entity, Entity):
					if not entity.body.is_sleeping:
						keepUpright(entity.body)
				else:
					entity.body.angle = math.atan2(-entity.body.velocity.y, entity.body.velocity.x)

		return True

	def _generate(self) -> None:
		print(f"\nWorld width: {self.world_width}")
		print("World Generation Time")
		print(f"{'Task':<20} | Time (seconds)")
		print("-" * 37)
		startTime = time.perf_counter()

		self._generateWorld()
		self._generateWorldShapes()

		start = time.perf_counter()
		self._generateEntities()
		print(f"{'Entities':<20} | {round(time.perf_counter() - start, 4)}s")

		print("-" * 37)
		print(f"{'Total':<20} | {round(time.perf_counter() - startTime, 4)}s")
		self.player.body.position = self.world.width * 0.5, self.world.top_y(self.world.width * 0.5) - 1
	
	def _generateEntities(self) -> None:
		px = self.player.body.position.x

		# NPC next to player — spawn immediately so the opening message works
		self.spawnEntity(Npc, px + 1, self.world.top_y(px + 1) - 1, customMessage=FIRST_MESSAGE)

		# Everything else goes into the pending pool — no pymunk objects yet
		for _ in range(self.world.width // RABBIT_RARITY):
			x = random.randint(0, self.world.width - 1)
			self._queueEntity(Rabbit, x, self.world.top_y(x) - 1)

		for _ in range(self.world.width // NPC_RARITY):
			x = random.randint(0, self.world.width - 1)
			self._queueEntity(Npc, x, self.world.top_y(x) - 1)

		for _ in range(self.world.width // DOG_RARITY):
			x = random.randint(0, self.world.width - 1)
			self._queueEntity(Dog, x, self.world.top_y(x) - 1)

	def _queueEntity(self, entityType: Type[EntityLike], x: float, y: float, **kwargs) -> None:
		'''Store a pending entity spawn — no pymunk object created yet.'''
		self.pending_entities.append((entityType, x, y, kwargs))

	def spawnEntitiesRandom(self) -> None:
		# Count live + pending per type so we don't over-spawn
		pending_counts: dict[Type, int] = {}
		for entityType, *_ in self.pending_entities:
			pending_counts[entityType] = pending_counts.get(entityType, 0) + 1

		for _ in range(self.world.width // RABBIT_RARITY
						- self.entity_counter[Rabbit]
						- pending_counts.get(Rabbit, 0)):
			x = random.randint(0, self.world.width - 1)
			self._queueEntity(Rabbit, x, self.world.top_y(x) - 1)

		for _ in range(self.world.width // DOG_RARITY
						- self.entity_counter[Dog]
						- pending_counts.get(Dog, 0)):
			x = random.randint(0, self.world.width - 1)
			self._queueEntity(Dog, x, self.world.top_y(x) - 1)

	def spawnEntity(self, entityType: Type[EntityLike], x: float, y: float, **kwargs) -> None:
		'''Immediately instantiate an entity (used for player-triggered spawns).'''
		entity = entityType(x, y, self.world, self.space, **kwargs)
		self.entities.append(entity)
		if type(entity) in self.entity_counter:
			self.entity_counter[type(entity)] += 1
		# Sleep if far from player
		if hasattr(entity, 'body'):
			try:
				if dist(entity.body.position, self.player.body.position) > ENTITY_WAKE_RADIUS:
					entity.body.sleep()
			except Exception:
				entity.body.sleep()
	
	def deleteEntity(self, i: int, entity) -> None:
		if type(entity) in self.entity_counter:
			self.entity_counter[type(entity)] -= 1
		self.space.remove(entity.body, entity.shape)
		del self.entities[i]

	def _updatePendingEntities(self) -> None:
		'''Instantiate any pending entities that are now within wake radius.'''
		if not self.pending_entities:
			return

		player_pos = self.player.body.position
		still_pending = []

		for entityType, x, y, kwargs in self.pending_entities:
			if dist((x, y), player_pos) <= ENTITY_WAKE_RADIUS:
				self.spawnEntity(entityType, x, y, **kwargs)
			else:
				still_pending.append((entityType, x, y, kwargs))

		self.pending_entities = still_pending


	def placeBlock(self, x: int, y: int) -> None:
		'''place a block or use an item at coordinates (x, y)'''
		if isinstance(self.player.heldSlot.item, Rpg):
			if self.player.heldSlot.item.ammo > 0:
				self.player.heldSlot.item.ammo -= 1
				self.entities.append(Rocket(*self.player.body.position, self.space))
				return
		if not (0 <= x < self.world.width and 0 <= y < self.world.height):
			return
		if isinstance(self.world[y][x], AirBlock):
			if self.player.heldSlot.item:
				if isinstance(self.player.heldSlot.item, Placeable):
					if self.player.heldSlot.item.getBlock().isFragile:
						if isinstance(self.world.back[y][x], AirBlock):
							if not y + 1 == self.world.height and self.world[y + 1][x].isEmpty:
								return
					self.player.heldSlot.count -= 1
					self.world[y][x] = self.player.heldSlot.item.getBlock()()
					self.world.enums[y, x] = self.world[y][x].enum.value
					if not self.player.heldSlot.count:
						self.player.heldSlot.clear()
					if isinstance(self.world[y][x], Light):
						self.lights.append((self.world[y][x], x, y))
					if not self.world[y][x].isEmpty:
						self._createBlockShape(x, y)   # << handles chunk tracking
						self.generateLight(y, x)
				elif isinstance(self.player.heldSlot.item, Bucket):
					if self.player.heldSlot.item.liquid and math.isclose(
						self.player.heldSlot.item.filledAmount,
						self.player.heldSlot.item.capacity
					):
						self.liquids.append(self.player.heldSlot.item.liquid(x, y, self.space))
						self.player.heldSlot.item.clear()


	def removeBlock(self, x: int, y: int) -> None:
		if isinstance(self.world[y][x], InventoryBlock):
			pg.event.post(pg.event.Event(
				REMOVEINVENTORYTYPE,
				inventoryType=[inventoryType for _, inventoryType in self.world[y][x].inventories]
			))

		if hasattr(self.world[y][x], 'shape'):
			shape = self.world[y][x].shape
			self.space.remove(shape)
			if hasattr(shape, '_range'):
				x_start, x_end, sy = shape._range
				for bx in range(x_start, x_end):
					if bx != x and not self.world[sy][bx].isEmpty:
						self._createBlockShape(bx, sy)

		if isinstance(self.world[y][x], Light):
			self.lights.remove((self.world[y][x], x, y))

		self.world[y][x] = AirBlock()
		self.world.enums[y, x] = Blocks.Air.value

		if isinstance(self.world.back[y][x], AirBlock):
			self.generateLight(y, x)


	def mineBlock(self) -> None:
		'''mine the block the player is facing'''
		if self.block_facing_coord:
			x, y = self.block_facing_coord
			if self.world[y][x].amountBroken < self.world[y][x].hardness:
				miningSpeed = 1
				if self.player.heldSlot.item and isinstance(self.player.heldSlot.item, Tool) and self.player.heldSlot.item.blockType == self.world[y][x].blockType:
					miningSpeed = self.player.heldSlot.item.speed
				self.world[y][x].amountBroken += miningSpeed / FPS
			else:
				if self.player.heldSlot.item and isinstance(self.player.heldSlot.item, Tool):
					self.player.heldSlot.item.durability -= 1
					if self.player.heldSlot.item.durability == 0:
						self.player.heldSlot.clear()
				itemType = block2Item[self.world[y][x].enum]
				if itemType:
					self.player.inventory.addItem(itemType())
				self.removeBlock(x, y)

    
	def _generateWorld(self) -> None:
		noises = self._generateAllNoise()

		start = time.perf_counter()
		self._placeTerrain(noises[Noises.BIOME], noises[Noises.GRASSHEIGHT], noises[Noises.STONEHEIGHT], noises[Noises.CAVES])
		print(f"{'Terrain':<20} | {round(time.perf_counter() - start, 4)}s")

		start = time.perf_counter()
		self._placeOres(noises[Noises.COAL], noises[Noises.IRON], noises[Noises.GOLD], noises[Noises.DIAMOND])
		print(f"{'Ores':<20} | {round(time.perf_counter() - start, 4)}s")

		start = time.perf_counter()
		self.generateLight()
		print(f"{'Light':<20} | {round(time.perf_counter() - start, 4)}s")
    
    
	def _placeTerrain(self, biomeNoise, grassNoise, stoneNoise, caveNoise) -> None:
		grassNoiseArray = np.array([grassNoise[x] for x in range(self.world.width)])
		stoneNoiseArray = np.array([stoneNoise[x] for x in range(self.world.width)])

		self.biomeArray = [Biome.FOREST if noise > 0 else Biome.PLAINS for noise in biomeNoise.noise]

		grassHeight = np.round(self.world.height * 0.35 + 9 * grassNoiseArray).astype(int)
		stoneHeight = np.round(grassHeight + 5 + 5 * stoneNoiseArray).astype(int)

		Y = np.arange(self.world.height)[:, np.newaxis]

		is_underground = Y > grassHeight[np.newaxis, :]
		is_stone       = Y > stoneHeight[np.newaxis, :]
		is_grass       = Y == grassHeight[np.newaxis, :]
		is_cave        = (caveNoise.noise > 0.1) & is_underground

		dirt_f  = is_underground & ~is_stone & ~is_cave
		stone_f = is_underground &  is_stone & ~is_cave
		grass_f = is_grass       & ~is_cave
		dirt_b  = is_underground & ~is_stone
		stone_b = is_underground &  is_stone

		for y, x in zip(*np.where(dirt_f)):
			self.world[y][x] = DirtBlock()
		for y, x in zip(*np.where(stone_f)):
			self.world[y][x] = StoneBlock()
		for y, x in zip(*np.where(grass_f)):
			self.world[y][x] = GrassBlock()
		for y, x in zip(*np.where(dirt_b)):
			self.world.back[y][x] = DirtBlock()
		for y, x in zip(*np.where(stone_b)):
			self.world.back[y][x] = StoneBlock()

		# << CHANGED: sync enum arrays in bulk using numpy — no per-cell overhead
		AIR   = Blocks.Air.value
		DIRT  = Blocks.Dirt.value
		STONE = Blocks.Stone.value
		GRASS = Blocks.Grass.value

		self.world.enums[dirt_f]  = DIRT
		self.world.enums[stone_f] = STONE
		self.world.enums[grass_f] = GRASS
		# air cells stay at default AIR value

		self.world.back_enums[dirt_b]  = DIRT
		self.world.back_enums[stone_b] = STONE

		for x in range(self.world.width):
			gx = int(grassHeight[x])
			if 0 <= gx < self.world.height and isinstance(self.world[gx][x], GrassBlock):
				if random.random() > 0.65:
					if self.biomeArray[x] == Biome.FOREST:
						self._generateTree(x, gx - 1)
					elif self.biomeArray[x] == Biome.PLAINS:
						block = random.choice((PoppyBlock, DandelionBlock, CornflowerBlock, AlliumBlock))()
						self.world[gx - 1][x] = block
						self.world.enums[gx - 1, x] = block.enum.value  # << CHANGED


	def _generateTree(self, x: int, y: int) -> None:
		'''Place a tree with base at coordinates (x, y) and a random height'''
		if not 3 <= x < self.world.width - 3:
			return

		height = random.randint(3, 7)

		for r in range(y - height - 1, y + 1):
			for c in range(x - 2, x + 3):
				if not isinstance(self.world[r][c], AirBlock):
					return

		for i in range(height):
			self.world[y - i][x] = LogBlock()
			self.world.enums[y - i, x] = Blocks.Log.value

		leaf_coords = [
			(y - height,     x - 2), (y - height,     x - 1),
			(y - height,     x),     (y - height,     x + 1),
			(y - height,     x + 2), (y - height - 1, x - 1),
			(y - height - 1, x),     (y - height - 1, x + 1),
		]
		for ly, lx in leaf_coords:
			self.world[ly][lx] = LeavesBlock()
			self.world.enums[ly, lx] = Blocks.Leaves.value

		self.world[y + 1][x] = DirtBlock()
		self.world.enums[y + 1, x] = Blocks.Dirt.value


	def _placeOres(self, coalNoise: SimplexNoise, ironNoise: SimplexNoise, goldNoise: SimplexNoise, diamondNoise: SimplexNoise) -> None:
		H, W = self.world.height, self.world.width

		is_stone = np.array(
			[[isinstance(self.world[y][x], StoneBlock) for x in range(W)] for y in range(H)],
			dtype=bool,
		)

		Y = np.arange(H)[:, np.newaxis]

		coal_mask    = is_stone & (coalNoise.noise    > 0.3)
		iron_mask    = is_stone & (ironNoise.noise    > 0.38) & (Y > H * 0.5)  & ~coal_mask
		gold_mask    = is_stone & (goldNoise.noise    > 0.42) & (Y > H * 0.7)  & ~coal_mask & ~iron_mask
		diamond_mask = is_stone & (diamondNoise.noise > 0.46) & (Y > H * 0.85) & ~coal_mask & ~iron_mask & ~gold_mask

		for y, x in zip(*np.where(coal_mask)):
			self.world[y][x] = CoalOreBlock()
		for y, x in zip(*np.where(iron_mask)):
			self.world[y][x] = IronOreBlock()
		for y, x in zip(*np.where(gold_mask)):
			self.world[y][x] = GoldOreBlock()
		for y, x in zip(*np.where(diamond_mask)):
			self.world[y][x] = DiamondOreBlock()

		self.world.enums[coal_mask]    = Blocks.CoalOre.value
		self.world.enums[iron_mask]    = Blocks.IronOre.value
		self.world.enums[gold_mask]    = Blocks.GoldOre.value
		self.world.enums[diamond_mask] = Blocks.DiamondOre.value

	def _generateAllNoise(self) -> dict[Noises, SimplexNoise]:
		from concurrent.futures import ThreadPoolExecutor, as_completed

		total_start = time.perf_counter()

		noise_parameters = [
			(Noises.BIOME,        200,  1),
			(Noises.GRASSHEIGHT,   19,  1),
			(Noises.STONEHEIGHT,   30,  1),
			(Noises.CAVES,          9,  2),
			(Noises.COAL,         3.9,  2),
			(Noises.IRON,         3.2,  2),
			(Noises.GOLD,         2.5,  2),
			(Noises.DIAMOND,      1.2,  2),
		]

		def generateOne(noise_type: Noises, scale: float, dimension: int) -> tuple[Noises, SimplexNoise]:
			return noise_type, SimplexNoise(
				scale=scale,
				dimension=dimension,
				width=self.world.width,
				height=self.world.height,
			)

		noises = {}
		with ThreadPoolExecutor() as executor:
			futures = {
				executor.submit(generateOne, *params): params
				for params in noise_parameters
			}
			for future in as_completed(futures):
				noise_type, noise_obj = future.result()
				noises[noise_type] = noise_obj

		print(f"{'SimplexNoise':<20} | {time.perf_counter() - total_start:.4f}s")
		return noises


	def generateLight(self, originr: Optional[int] = None, originc: Optional[int] = None) -> None:
		if not hasattr(self, 'lightmap'):
			self.lightmap = np.zeros((self.world.height, self.world.width), dtype=np.int16)

		MAX_DIST = 6
		AIR = Blocks.Air.value

		startr = 0                 if originr is None else max(0,                 originr - MAX_DIST)
		startc = 0                 if originc is None else max(0,                 originc - MAX_DIST)
		stopr  = self.world.height if originr is None else min(self.world.height, originr + MAX_DIST + 1)
		stopc  = self.world.width  if originc is None else min(self.world.width,  originc + MAX_DIST + 1)

		r0 = max(0,                 startr - MAX_DIST)
		c0 = max(0,                 startc - MAX_DIST)
		r1 = min(self.world.height, stopr  + MAX_DIST)
		c1 = min(self.world.width,  stopc  + MAX_DIST)

		front_air = self.world.enums[r0:r1, c0:c1]      == AIR
		back_air  = self.world.back_enums[r0:r1, c0:c1] == AIR
		empty_mask = ~(front_air & back_air)

		dist = distance_transform_cdt(empty_mask, metric='taxicab').clip(0, MAX_DIST)
		light_values = np.clip((dist - 1) * 51, 0, 255).astype(np.int16)

		rel_r0 = startr - r0
		rel_c0 = startc - c0
		rel_r1 = rel_r0 + (stopr - startr)
		rel_c1 = rel_c0 + (stopc - startc)

		self.lightmap[startr:stopr, startc:stopc] = light_values[rel_r0:rel_r1, rel_c0:rel_c1]
	
	def _generate_boundary_shapes(self) -> None:
		'''generate pymunk shapes for the boundary of the world'''
		self.space.add(
			pm.Poly(self.world_body, (
				(-1, 0),
				(-1, self.world.height),
				(0, self.world.height),
				(0, 0)
			)),
			pm.Poly(self.world_body, (
				(0, -1),
				(0, 0),
				(self.world.width, 0),
				(self.world.width, -1)
			)),
			pm.Poly(self.world_body, (
				(self.world.width, 0),
				(self.world.width, self.world.height),
				(self.world.width + 1, self.world.height),
				(self.world.width + 1, 0)
			)),
			pm.Poly(self.world_body, (
				(0, self.world.height),
				(0, self.world.height + 1),
				(self.world.width, self.world.height + 1),
				(self.world.width, self.world.height)
			)),
		)

	def _createBlockShape(self, x: int, y: int) -> None:
		'''Create a single block shape and mark its chunk dirty.'''
		# Remove stale shape if one exists
		block = self.world[y][x]
		if hasattr(block, 'shape') and block.shape in self.space.shapes:
			self.space.remove(block.shape)

		vertices = (
			(x,     y),
			(x,     y + 1),
			(x + 1, y + 1),
			(x + 1, y),
		)
		shape          = pm.Poly(self.world_body, vertices)
		shape.friction = block.friction
		shape._range   = (x, x + 1, y)
		block.shape    = shape
		self.space.add(shape)

		# Track in chunk_shapes so unloading the chunk removes it too
		cx = x // CHUNK_SIZE
		if self.chunk_shapes[cx] is not None:
			self.chunk_shapes[cx].append(shape)


	def removeBlock(self, x: int, y: int) -> None:
		if isinstance(self.world[y][x], InventoryBlock):
			pg.event.post(pg.event.Event(
				REMOVEINVENTORYTYPE,
				inventoryType=[inventoryType for _, inventoryType in self.world[y][x].inventories]
			))

		if hasattr(self.world[y][x], 'shape'):
			shape = self.world[y][x].shape
			# Only remove if actually in the space
			if shape in self.space.shapes:
				self.space.remove(shape)

				if hasattr(shape, '_range'):
					x_start, x_end, sy = shape._range
					for bx in range(x_start, x_end):
						if bx != x and not self.world[sy][bx].isEmpty:
							self._createBlockShape(bx, sy)

		if isinstance(self.world[y][x], Light):
			self.lights.remove((self.world[y][x], x, y))

		self.world[y][x] = AirBlock()
		self.world.enums[y, x] = Blocks.Air.value

		if isinstance(self.world.back[y][x], AirBlock):
			self.generateLight(y, x)

	
	def _buildChunkShapes(self, cx: int) -> list:
		x_start_chunk = cx * CHUNK_SIZE
		x_end_chunk   = min(self.world.width, x_start_chunk + CHUNK_SIZE)
		shapes = []

		for y in range(self.world.height):
			x = x_start_chunk
			while x < x_end_chunk:
				block = self.world[y][x]

				if block.isEmpty:
					x += 1
					continue

				# Skip blocks that already have an individually-placed shape
				if hasattr(block, 'shape') and block.shape in self.space.shapes:
					x += 1
					continue

				friction  = block.friction
				run_start = x
				while (x < x_end_chunk
					and not self.world[y][x].isEmpty
					and self.world[y][x].friction == friction
					and not (hasattr(self.world[y][x], 'shape')
								and self.world[y][x].shape in self.space.shapes)):
					x += 1
				run_end = x

				if run_end == run_start:
					x += 1
					continue

				vertices = (
					(run_start, y),
					(run_start, y + 1),
					(run_end,   y + 1),
					(run_end,   y),
				)
				shape          = pm.Poly(self.world_body, vertices)
				shape.friction = friction
				shape._range   = (run_start, run_end, y)

				for bx in range(run_start, run_end):
					self.world[y][bx].shape = shape

				shapes.append(shape)

		return shapes

	def _generateWorldShapes(self) -> None:
		num_chunks = math.ceil(self.world.width / CHUNK_SIZE)
		self.chunk_shapes:   list[list | None] = [None] * num_chunks
		self.loaded_chunks:  set[int]          = set()


	def updateChunkShapes(self) -> None:
		player_chunk = int(self.player.body.position.x) // CHUNK_SIZE
		wanted: set[int] = {
			cx for cx in range(
				max(0, player_chunk - CHUNK_LOAD_RADIUS),
				min(len(self.chunk_shapes), player_chunk + CHUNK_LOAD_RADIUS + 1),
			)
		}

		# ── Unload chunks that left the radius ────────────────────────────
		for cx in self.loaded_chunks - wanted:
			if self.chunk_shapes[cx]:
				# Only remove shapes that are still in the space
				to_remove = [s for s in self.chunk_shapes[cx] if s in self.space.shapes]
				if to_remove:
					self.space.remove(*to_remove)
				self.chunk_shapes[cx] = None

		# ── Load / reload chunks that entered the radius ──────────────────
		for cx in wanted - self.loaded_chunks:
			shapes = self._buildChunkShapes(cx)
			self.chunk_shapes[cx] = shapes
			if shapes:
				self.space.add(*shapes)

		self.loaded_chunks = wanted
