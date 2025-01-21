from math import dist
import math
import random
import pymunk as pm
import numpy as np
import time
from pymunk import Space
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from typing import Optional, Type

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
from game.model.items.inventory.inventorytype import InventoryType
from game.model.items.rpg import Rocket, Rpg
from game.model.liquids.liquid import Liquid
from game.model.utils.biomesenum import Biome
from utils.constants import DOG_RARITY, FIRST_MESSAGE, FPS, NPC_RARITY, RABBIT_RARITY
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
from game.model.utils.adddefaultitems import addDefaultItems
from game.model.utils.noisesenum import Noises
from game.model.world import World
from game.model.entity.entity import Entity
from utils.customqueue import Queue
from utils.simplexnoise import SimplexNoise
import pygame as pg


class Model:
	'''All game logic happens in this class'''
	def __init__(self, worldWidth: int, worldHeight: int):
		'''initialize the game'''
		self.space = Space()
		self.space.sleep_time_threshold = 2
		self.world = World(worldWidth, worldHeight)
		self.player = Player(0, 0, self.world, self.space)
		
		self.lightmap = [
			[0 for x in range(worldWidth)] for y in range(worldHeight)
		]
		self.liquids: list[Liquid] = []
		self.entities: list[HasPhysics] = [] # list of the entities in the world except the player
		self.entityCounter: dict[Type[Entity], int] = {
			Rabbit: 0,
			Dog: 0,
		}
		self.lights: list[tuple[Light, int, int]] = []
		self.space.gravity = 0, 20 # earth's gravity is 9.81 m/s
		self.worldBody = pm.Body(body_type=pm.Body.STATIC)
		self.space.add(self.worldBody)
		self._generateBoundaryShapes()
		self.blockFacingCoord: tuple[int, int] | None = None
		self._generate()
		addDefaultItems(self.player)

	def update(self, steps=4) -> bool:
		'''Update the model, should be called every frame. steps increases the accuracy of the physics simulation but sacrifices performance. returns whether the player is alive'''
		self.player.update()
  
		#if player is dead
		if not self.player.isAlive:
			return False
		for i, entity in enumerate(self.entities):
			if isinstance(entity, Entity):
				entity.update(self.player.body.position)
				if isinstance(entity, Dog) and dist(entity.body.position, self.player.body.position) < 1.5:
					if self.player.takeDamage(1):
						self.player.body.apply_impulse_at_local_point((self.player.body.position - entity.body.position) * 30, (0, 0.5))
				if not entity.isAlive:
					self.deleteEntity(i, entity)
					continue
			elif isinstance(entity, Rocket):
				if entity.stationary:
					pg.event.post(pg.event.Event(DRAWEXPLOSION, pos=entity.body.position, radius=0.5, width=8))
					ex, ey = list(map(int, entity.body.position)) # source of explosion
					for y in range(max(0, ey - 3), min(self.world.height, ey + 4)):
						for x in range(max(0, ex - 3), min(self.world.width, ex + 4)):
							self.removeBlock(x, y)
					for otherEntity in self.entities:
						if isinstance(otherEntity, Entity) and dist(otherEntity.body.position, entity.body.position) <= 3:
							otherEntity.takeDamage(10)
					self.deleteEntity(i, entity)
					continue
			if not 0 < entity.body.position.x < self.world.width or not 0 < entity.body.position.y < self.world.height:
				self.deleteEntity(i, entity)
		
		if isinstance(self.player.heldSlot.item, Bucket) and self.player.heldSlot.item.filledAmount < 1:
			for i, liquid in enumerate(self.liquids):
				for p, liquidParticle in enumerate(liquid.particles):
					if dist(liquidParticle.body.position, self.player.body.position) < 1.5:
						if self.player.heldSlot.item.liquid is None:
							self.player.heldSlot.item.liquid = liquidParticle.liquid
						if self.player.heldSlot.item.liquid == liquidParticle.liquid and self.player.heldSlot.item.filledAmount < 1:
							self.player.heldSlot.item.fill(1 / self.player.heldSlot.item.liquid.particleCount)
							del self.liquids[i].particles[p]
					
    
		for i in range(steps):
			self.space.step((1/FPS)/steps) # step the simulation in 1/60 seconds
			keepUpright(self.player.body)
			for entity in self.entities:
				if isinstance(entity, Entity):
					keepUpright(entity.body)
				else:
					entity.body.angle = math.atan2(-entity.body.velocity.y, entity.body.velocity.x)
    
		return True

	def _generate(self):
		'''generate game'''
		startTime = time.perf_counter()
		self._generateWorld()
		self._generateWorldShapes()
		self._generateEntities()
		print(f'World generation time: {round(time.perf_counter() - startTime, 2)} seconds')
		self.player.body.position = self.world.width * 0.5, self.world.topy(self.world.width * 0.5) - 1
	
	def _generateEntities(self) -> None:
		px = self.player.body.position.x
		self.spawnEntity(Npc, px + 1, self.world.topy(px + 1) - 1, customMessage=FIRST_MESSAGE)
		for _ in range(self.world.width // RABBIT_RARITY):
			x = random.randint(0, self.world.width - 1)
			self.spawnEntity(Rabbit, x, self.world.topy(x) - 1)
		for _ in range(self.world.width // NPC_RARITY):
			x = random.randint(0, self.world.width - 1)
			self.spawnEntity(Npc, x, self.world.topy(x) - 1)
		for _ in range(self.world.width // DOG_RARITY):
			x = random.randint(0, self.world.width - 1)
			self.spawnEntity(Dog, x, self.world.topy(x) - 1)

	def spawnEntitiesRandom(self) -> None:
		for _ in range(self.world.width // RABBIT_RARITY - self.entityCounter[Rabbit]):
			x = random.randint(0, self.world.width - 1)
			self.spawnEntity(Rabbit, x, self.world.topy(x) - 1)
		for _ in range(self.world.width // DOG_RARITY - self.entityCounter[Dog]):
			x = random.randint(0, self.world.width - 1)
			self.spawnEntity(Dog, x, self.world.topy(x) - 1)

	def spawnEntity(self, entityType: Type[EntityLike], x: float, y: float, **kwargs) -> None:
		'''Spawn a new entity into the game'''
		entity = entityType(x, y, self.world, self.space, **kwargs)
		self.entities.append(entity)
		if type(entity) in self.entityCounter:
			self.entityCounter[type(entity)] += 1
	
	def deleteEntity(self, i: int, entity: HasPhysics) -> None:
		if type(entity) in self.entityCounter:
			self.entityCounter[type(entity)] -= 1
		self.space.remove(entity.body, entity.shape)
		del self.entities[i]
	
	def placeBlock(self, x: int, y: int) -> None:
		'''place a block at coordinates (x, y)'''
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
					if not self.player.heldSlot.count:
						self.player.heldSlot.clear()
					if isinstance(self.world[y][x], Light):
						self.lights.append((self.world[y][x], x, y))
					if not self.world[y][x].isEmpty:
						vertices = (
						(x, y),
						(x, y + 1),
						(x + 1, y + 1),
						(x + 1, y)
						)
						self.world[y][x].shape = pm.Poly(self.worldBody, vertices)
						self.world[y][x].shape.friction = self.world[y][x].friction
						self.space.add(self.world[y][x].shape)
						self.generateLight(y, x)
				elif isinstance(self.player.heldSlot.item, Bucket):
					if self.player.heldSlot.item.liquid and math.isclose(self.player.heldSlot.item.filledAmount, self.player.heldSlot.item.capacity):
						self.liquids.append(self.player.heldSlot.item.liquid(x, y, self.space))
						self.player.heldSlot.item.clear()
				elif isinstance(self.player.heldSlot.item, Rpg):
					if self.player.heldSlot.item.ammo > 0:
						self.player.heldSlot.item.ammo -= 1
						self.entities.append(Rocket(*self.player.body.position, self.space))

	def removeBlock(self, x: int, y: int) -> None:
		print("hi")
		if isinstance(self.world[y][x], InventoryBlock):
			pg.event.post(pg.event.Event(REMOVEINVENTORYTYPE, inventoryType=[inventoryType for _, inventoryType in self.world[y][x].inventories]))
		if hasattr(self.world[y][x], 'shape'):
			self.space.remove(self.world[y][x].shape)
		if isinstance(self.world[y][x], Light):
			self.lights.remove((self.world[y][x], x, y))
		self.world[y][x] = AirBlock()
		if isinstance(self.world.back[y][x], AirBlock):
			self.generateLight(y, x)

	def mineBlock(self) -> None:
		'''mine the block the player is facing'''
		if self.blockFacingCoord:
			x, y = self.blockFacingCoord
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


	def _generateWorld(self):
		'''Generate the random world using vectorized NumPy operations'''
		noises = self._generateAllNoise()
  
		start = time.perf_counter()
		self._placeTerrain(noises[Noises.BIOME], noises[Noises.GRASSHEIGHT], noises[Noises.STONEHEIGHT], noises[Noises.CAVES])
		print(f"Terrain time: {round(time.perf_counter() - start, 4)} seconds")
		
		self._placeOres(noises[Noises.COAL], noises[Noises.IRON], noises[Noises.GOLD], noises[Noises.DIAMOND])
		
		start = time.perf_counter()
		self.generateLight()
		print(f"Light time: {round(time.perf_counter() - start, 4)} seconds")
    
	def _placeTerrain(self, biomeNoise: SimplexNoise, grassNoise: SimplexNoise, stoneNoise: SimplexNoise, caveNoise: SimplexNoise) -> None:
		'''Place the dirt, stone, and cut out caves'''
		grassNoiseArray = np.array([grassNoise[x] for x in range(self.world.width)])
		stoneNoiseArray = np.array([stoneNoise[x] for x in range(self.world.width)])
		
		# biome
		self.biomeArray = [Biome.FOREST if noise > 0 else Biome.PLAINS for noise in biomeNoise.noise]

		# Calculate height maps using vectorized operations
		grassHeight = np.round(self.world.height * 0.35 + 9 * grassNoiseArray).astype(int)
		stoneHeight = np.round(grassHeight + 5 + 5 * stoneNoiseArray).astype(int)
		
		for x in range(self.world.width):
			# Place stone and dirt
			for y in range(self.world.height - 1, grassHeight[x], -1):
				if y > stoneHeight[x]:
					self.world[y][x] = StoneBlock()
					self.world.back[y][x] = StoneBlock()
				else:
					self.world[y][x] = DirtBlock()
					self.world.back[y][x] = DirtBlock()
			
			# Place grass block at the surface
			if 0 <= grassHeight[x] < self.world.height:
				self.world[grassHeight[x]][x] = GrassBlock()
		
		# Cut out caves
		for y in range(self.world.height):
			for x in range(self.world.width):
				if (caveNoise[y][x] > 0.1 and 
					y >= grassHeight[x] and 
					y < self.world.height):
					self.world[y][x] = AirBlock()
		
		#Generate trees / flowers depending on biome
		for x in range(self.world.width):
			if isinstance(self.world[grassHeight[x]][x], GrassBlock):
				if random.random() > 0.65:
					if self.biomeArray[x] == Biome.FOREST:
						self._generateTree(x, grassHeight[x] - 1)
					elif self.biomeArray[x] == Biome.PLAINS:
						self.world[grassHeight[x] - 1][x] = random.choice((PoppyBlock, DandelionBlock, CornflowerBlock, AlliumBlock))()

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
		self.world[y - height][x - 2] = LeavesBlock()
		self.world[y - height][x - 1] = LeavesBlock()
		self.world[y - height][x] = LeavesBlock()
		self.world[y - height][x + 1] = LeavesBlock()
		self.world[y - height][x + 2] = LeavesBlock()
		self.world[y - height - 1][x - 1] = LeavesBlock()
		self.world[y - height - 1][x] = LeavesBlock()
		self.world[y - height - 1][x + 1] = LeavesBlock()
		self.world[y + 1][x] = DirtBlock()

	def _placeOres(self, coalNoise: SimplexNoise, ironNoise: SimplexNoise, goldNoise: SimplexNoise, diamondNoise: SimplexNoise):
		'''Place ores'''
		for y in range(self.world.height):
			for x in range(self.world.width):
				if isinstance(self.world[y][x], StoneBlock):
					if coalNoise[y][x] > 0.3:
						self.world[y][x] = CoalOreBlock()
					elif ironNoise[y][x] > 0.38:
						self.world[y][x] = IronOreBlock()
					elif goldNoise[y][x] > 0.42:
						self.world[y][x] = GoldOreBlock()
					elif diamondNoise[y][x] > 0.46:
						self.world[y][x] = DiamondOreBlock()
					

	def _generateAllNoise(self) -> dict[Noises, SimplexNoise]:
		totalStartTime = time.perf_counter()

		def generateNoise(noiseType: Noises, scale: float, dimension: int, width: int = self.world.width, 
						height: int = self.world.height) -> tuple[Noises, SimplexNoise, float]:
			startTime = time.perf_counter()
			
			noise = SimplexNoise(scale=scale, dimension=dimension, width=width, height=height)
			
			# Calculate the time taken for this noise generation
			generationTime = time.perf_counter() - startTime
			return noiseType, noise, generationTime

		noiseParameters = (
			(Noises.BIOME, 200, 1),
			(Noises.GRASSHEIGHT, 19, 1),
			(Noises.STONEHEIGHT, 30, 1),
			(Noises.CAVES, 9, 2),
			(Noises.COAL, 3.9, 2),
			(Noises.IRON, 3.2, 2),
			(Noises.GOLD, 2.5, 2),
			(Noises.DIAMOND, 1.2, 2),
		)

		with ThreadPoolExecutor() as executor:
			futures = [executor.submit(partial(generateNoise, *parameter)) 
					for parameter in noiseParameters]
			

			noises = {}
			timingData = {}
			
			for future in as_completed(futures):
				noiseType, noiseObj, generationTime = future.result()
				noises[noiseType] = noiseObj
				timingData[noiseType] = generationTime
		
		totalTime = time.perf_counter() - totalStartTime
		
		#Print timing information
		print("\nNoise Generation Timing:")
		print(f"{'Noise Type':<15} | {'Time (seconds)':<10}")
		print("-" * 30)
		for noiseType, timeTaken in timingData.items():
			print(f"{noiseType.name:<15} | {timeTaken:.4f}s")
		print("-" * 30)
		print(f"{'Total':<15} | {totalTime:.4f}s\n")

		return noises
 
	def generateLight(self, originr: Optional[int] = None, originc: Optional[int] = None) -> None:
		# Calculate bounds for the light calculation region with proper clamping
		startr = max(0, (0 if originr is None else originr - 6))
		startc = max(0, (0 if originc is None else originc - 6))
		stopr = min(self.world.height, (self.world.height if originr is None else originr + 7))
		stopc = min(self.world.width, (self.world.width if originc is None else originc + 7))
		
		# Direction vectors for neighbor calculation
		DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
		
		def isDark(x: int, y: int) -> bool:
			"""Check if a block position is considered dark (both front and back are empty)."""
			return self.world[y][x].isEmpty and self.world.back[y][x].isEmpty

		# Initialize lightmap if not already created
		if not hasattr(self, 'lightmap'):
			self.lightmap = [[255 for _ in range(self.world.width)] 
							for _ in range(self.world.height)]
		
		# Reusable queue and visited set to reduce memory allocations
		bfs = Queue()
		visited = set()
		
		# Process each block in the specified region
		for r in range(startr, stopr):
			for c in range(startc, stopc):
				# Clear the queue and visited set for reuse
				while bfs.size() > 0:
					bfs.poll()
				visited.clear()
				
				# Initialize BFS for current position
				bfs.add((c, r))  # Starting position
				bfs.add(None)    # Level marker
				visited.add((c, r))
				
				level = 0
				lightFound = False
				
				# Continue BFS until we find light or reach max level
				while bfs.size() > 0 and level <= 6:
					cur = bfs.poll()
					
					if cur is None:
						level += 1
						if bfs.size() > 0:
							bfs.add(None)
						continue
					
					x, y = cur
					
					# Check if current block is dark
					if isDark(x, y):
						self.lightmap[r][c] = max(0, (level - 1) * 51)
						lightFound = True
						break
					
					# Add unvisited neighbors within bounds
					for dx, dy in DIRECTIONS:
						nx, ny = x + dx, y + dy
						if (0 <= nx < self.world.width and 
							0 <= ny < self.world.height and 
							(nx, ny) not in visited):
							visited.add((nx, ny))
							bfs.add((nx, ny))
				
				# If no dark blocks found in range, set to full brightness
				if not lightFound:
					self.lightmap[r][c] = 255
	
	def _generateBoundaryShapes(self) -> None:
		'''generate pymunk shapes for the boundary of the world'''
		self.space.add(
			pm.Poly(self.worldBody, (
				(-1, 0),
				(-1, self.world.height),
				(0, self.world.height),
				(0, 0)
			)),
			pm.Poly(self.worldBody, (
				(0, -1),
				(0, 0),
				(self.world.width, 0),
				(self.world.width, -1)
			)),
			pm.Poly(self.worldBody, (
				(self.world.width, 0),
				(self.world.width, self.world.height),
				(self.world.width + 1, self.world.height),
				(self.world.width + 1, 0)
			)),
			pm.Poly(self.worldBody, (
				(0, self.world.height),
				(0, self.world.height + 1),
				(self.world.width, self.world.height + 1),
				(self.world.width, self.world.height)
			)),
		)

	def _generateWorldShapes(self) -> None:
		'''generate pymunk shapes using numpy to identify solid blocks'''
		# Create mask for non-empty blocks
		solidMask = ~np.vectorize(lambda x: x.isEmpty)(self.world.array)
		
		# Get coordinates of solid blocks
		solidCoords = np.where(solidMask)
		
		# Generate shapes for all solid blocks at once
		for y, x in zip(*solidCoords):
			vertices = (
				(x, y),
				(x, y + 1),
				(x + 1, y + 1),
				(x + 1, y)
			)
			self.world[y][x].shape = pm.Poly(self.worldBody, vertices)
			self.world[y][x].shape.friction = self.world[y][x].friction
			self.space.add(self.world[y][x].shape)
