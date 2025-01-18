import random
import pymunk as pm
import numpy as np
import time
from pymunk import Space
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from typing import Optional

from game.model.entity.entities.npc import Npc
from game.model.entity.entities.rabbit import Rabbit
from utils.constants import FPS, SEED, WORLD_HEIGHT, WORLD_WIDTH
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


class Model:
	'''All game logic happens in this class'''
	def __init__(self, worldWidth: int, worldHeight: int):
		'''initialize the game'''
		self.world = World(worldWidth, worldHeight)
		self.player = Player(worldWidth * 0.5, worldHeight * 0.55, self.world)
		addDefaultItems(self.player)

		self.lightmap = [
			[0 for x in range(worldWidth)] for y in range(worldHeight)
		]
		self.lights: list[tuple[Light, int, int]] = []
		self.entities: list[Entity] = [] # list of the entities in the world except the player
		self.entityCounter = {
			Rabbit: 0,
		}
		
		self.space = Space()
		self.space.gravity = 0, 20 # earth's gravity is 9.81 m/s

		self.playerShape = pm.Poly.create_box(self.player, (self.player.width, self.player.height))
		self.playerShape.mass = self.player.mass
		self.playerShape.friction = self.player.friction
		self.space.add(self.player, self.playerShape)
		self.worldBody = pm.Body(body_type=pm.Body.STATIC)
		self.space.add(self.worldBody)
		self._generateBoundaryShapes()

		self.blockFacingCoord: tuple[int, int] | None = None

	def update(self, steps=20) -> bool:
		'''Update the model, should be called every frame. steps increases the accuracy of the physics simulation but sacrifices performance. returns whether the player is alive'''
		self.player.update()
		if not self.player.isAlive:
			return False
		for i, entity in enumerate(self.entities):
			entity.update(self.player.position)
			if not entity.isAlive or not 0 < entity.position.x < self.world.width or not 0 < entity.position.y < self.world.height:
				self.deleteEntity(i, entity)
		# start = time.perf_counter()
		for i in range(steps):
			self.space.step(1/FPS/steps) # step the simulation in 1/60 seconds
			keepUpright(self.player)
			for entity in self.entities:
				keepUpright(entity)
		# print(f'physics time: {round(time.perf_counter() - start, 3)}')
		return True

	def start(self):
		'''Start game'''
		startTime = time.perf_counter()
		self._generateWorld()
		self._generateWorldShapes()
		self._generateEntities()
		print(f'World generation time: {round(time.perf_counter() - startTime, 2)} seconds')
		px, py = self.player.position
		self.player.position = px, self.world.topy(px) - 1
	
	def _generateEntities(self) -> None:
		px, py = self.player.position
		self.spawnEntity(Npc(px + 1, self.world.topy(px + 1) - 1, self.world))
		self.spawnEntity(Rabbit(px - 2, self.world.topy(px - 2) - 1, self.world))
		for _ in range(self.world.width // 10):
			x = random.randint(0, self.world.width - 1)
			self.spawnEntity(Rabbit(x, self.world.topy(x) - 1, self.world))

	def spawnEntitiesRandom(self) -> None:
		for _ in range(self.world.width // 10 - self.entityCounter[Rabbit]):
			x = random.randint(0, self.world.width - 1)
			self.spawnEntity(Rabbit(x, self.world.topy(x) - 1, self.world))

	def spawnEntity(self, entity: Entity) -> None:
		'''Spawn a new entity into the game'''
		entity.shape = pm.Poly.create_box(entity, (entity.width, entity.height))
		entity.shape.mass = entity.mass
		entity.shape.friction = entity.friction
		self.space.add(entity, entity.shape)
		self.entities.append(entity)
		if type(entity) in self.entityCounter:
			self.entityCounter[type(entity)] += 1
	
	def deleteEntity(self, i: int, entity: Entity) -> None:
		if type(entity) in self.entityCounter:
			self.entityCounter[type(entity)] -= 1
		self.space.remove(entity, entity.shape)
		del self.entities[i]
	
	def placeBlock(self, x: int, y: int):
		'''place a block at coordinates (x, y)'''
		if isinstance(self.world[y][x], AirBlock):
			if self.player.heldSlot.item and isinstance(self.player.heldSlot.item, Placeable):
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

	def mineBlock(self):
		'''mine the block the player is facing'''
		if self.blockFacingCoord:
			x, y = self.blockFacingCoord
			if self.world[y][x].amountBroken < self.world[y][x].hardness:
				miningSpeed = 1
				if self.player.heldSlot.item and isinstance(self.player.heldSlot.item, Tool) and self.player.heldSlot.item.blockType == self.world[y][x].blockType:
					miningSpeed = self.player.heldSlot.item.speed
				self.world[y][x].amountBroken += miningSpeed / FPS
			else:
				itemType = block2Item[self.world[y][x].enum]
				if itemType:
					self.player.inventory.addItem(itemType())
				
				inventoryTypes = None
				if isinstance(self.world[y][x], InventoryBlock):
					inventoryTypes = [inventoryType for _, inventoryType in self.world[y][x].inventories]

				self.space.remove(self.world[y][x].shape)
				if isinstance(self.world[y][x], Light):
					self.lights.remove(self.world[y][x])
				self.world[y][x] = AirBlock()
				if isinstance(self.world.back[y][x], AirBlock):
					self.generateLight(y, x)
				return inventoryTypes

	def _generateWorld(self):
		'''Generate the random world using vectorized NumPy operations'''
		noises = self._generateAllNoise()
  
		start = time.perf_counter()
		self._placeTerrain(noises[Noises.GRASSHEIGHT], noises[Noises.STONEHEIGHT], noises[Noises.CAVES])
		print(f"Terrain time: {round(time.perf_counter() - start, 4)} seconds")
		
		self._placeOres(noises[Noises.COAL], noises[Noises.IRON])
		
		start = time.perf_counter()
		self.generateLight()
		print(f"Light time: {round(time.perf_counter() - start, 4)} seconds")
    
	def _placeTerrain(self, grassNoise: SimplexNoise, stoneNoise: SimplexNoise, caveNoise: SimplexNoise) -> None:
		'''Place the dirt, stone, and cut out caves'''
		grass_noise_array = np.array([grassNoise[x] for x in range(self.world.width)])
		stone_noise_array = np.array([stoneNoise[x] for x in range(self.world.width)])
		
		# Calculate height maps using vectorized operations
		grassHeight = np.round(self.world.height * 0.58 + 9 * grass_noise_array).astype(int)
		stoneHeight = np.round(grassHeight + 5 + 5 * stone_noise_array).astype(int)
		
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
		
		#Generate trees
		for x in range(self.world.width):
			if isinstance(self.world[grassHeight[x]][x], GrassBlock):
				if random.random() > 0.8:
					self._generateTree(x, grassHeight[x] - 1)

	def _generateTree(self, x: int, y: int) -> None:
		'''Place a tree with base at coordinates (x, y) and a random height'''
		if not 3 <= x < WORLD_WIDTH - 3:
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

	def _placeOres(self, coalNoise: SimplexNoise, ironNoise: SimplexNoise):
		'''Place ores'''
		for y in range(self.world.height):
			for x in range(self.world.width):
				if isinstance(self.world[y][x], StoneBlock):
					if coalNoise[y][x] > 0.3:
						self.world[y][x] = CoalOreBlock()
					elif ironNoise[y][x] > 0.38:
						self.world[y][x] = IronOreBlock()

	def _generateAllNoise(self, seed: int | None = None) -> dict[Noises, SimplexNoise]:
		totalStartTime = time.perf_counter()		
		random.seed(seed)

		def generateNoise(noiseType: Noises, scale: float, dimension: int, width: int = WORLD_WIDTH, 
						height: int = WORLD_HEIGHT, seed: int = SEED) -> tuple[Noises, SimplexNoise, float]:
			start_time = time.perf_counter()
			
			noise = SimplexNoise(scale=scale, dimension=dimension, width=width, height=height, seed=seed)
			
			# Calculate the time taken for this noise generation
			generation_time = time.perf_counter() - start_time
			return noiseType, noise, generation_time

		noiseParameters = (
			(Noises.GRASSHEIGHT, 19, 1),
			(Noises.STONEHEIGHT, 30, 1),
			(Noises.CAVES, 9, 2),
			(Noises.COAL, 3.9, 2),
			(Noises.IRON, 3.2, 2),
		)

		with ThreadPoolExecutor() as executor:
			futures = [executor.submit(partial(generateNoise, *parameter)) 
					for parameter in noiseParameters]
			

			noises = {}
			timing_data = {}
			
			for future in as_completed(futures):
				noise_type, noise_obj, generation_time = future.result()
				noises[noise_type] = noise_obj
				timing_data[noise_type] = generation_time
		
		total_time = time.perf_counter() - totalStartTime
		
		#Print timing information
		print("\nNoise Generation Timing:")
		print(f"{'Noise Type':<15} | {'Time (seconds)':<10}")
		print("-" * 30)
		for noise_type, time_taken in timing_data.items():
			print(f"{noise_type.name:<15} | {time_taken:.4f}s")
		print("-" * 30)
		print(f"{'Total':<15} | {total_time:.4f}s\n")

		return noises
 
	def generateLight(self, originr: Optional[int] = None, originc: Optional[int] = None) -> None:
		# Calculate bounds for the light calculation region with proper clamping
		startr = max(0, (0 if originr is None else originr - 6))
		startc = max(0, (0 if originc is None else originc - 6))
		stopr = min(self.world.height, (self.world.height if originr is None else originr + 7))
		stopc = min(self.world.width, (self.world.width if originc is None else originc + 7))
		
		# Pre-calculate world dimensions for boundary checks
		world_width = self.world.width
		world_height = self.world.height
		
		# Direction vectors for neighbor calculation
		DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
		
		def is_dark(x: int, y: int) -> bool:
			"""Check if a block position is considered dark (both front and back are empty)."""
			return self.world[y][x].isEmpty and self.world.back[y][x].isEmpty

		# Initialize lightmap if not already created
		if not hasattr(self, 'lightmap'):
			self.lightmap = [[255 for _ in range(world_width)] 
							for _ in range(world_height)]
		
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
				light_found = False
				
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
					if is_dark(x, y):
						self.lightmap[r][c] = max(0, (level - 1) * 51)
						light_found = True
						break
					
					# Add unvisited neighbors within bounds
					for dx, dy in DIRECTIONS:
						nx, ny = x + dx, y + dy
						if (0 <= nx < world_width and 
							0 <= ny < world_height and 
							(nx, ny) not in visited):
							visited.add((nx, ny))
							bfs.add((nx, ny))
				
				# If no dark blocks found in range, set to full brightness
				if not light_found:
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
		solid_mask = ~np.vectorize(lambda x: x.isEmpty)(self.world.array)
		
		# Get coordinates of solid blocks
		solid_coords = np.where(solid_mask)
		
		# Generate shapes for all solid blocks at once
		for y, x in zip(*solid_coords):
			vertices = (
				(x, y),
				(x, y + 1),
				(x + 1, y + 1),
				(x + 1, y)
			)
			self.world[y][x].shape = pm.Poly(self.worldBody, vertices)
			self.world[y][x].shape.friction = self.world[y][x].friction
			self.space.add(self.world[y][x].shape)

	def generateBlockShape(self, x: int, y: int):
		vertices = (
						(x, y),
						(x, y + 1),
						(x + 1, y + 1),
						(x + 1, y)
					)
		shape = pm.Poly(self.worldBody, vertices)
		shape.friction = self.world[y][x].friction
		self.space.add(shape)
