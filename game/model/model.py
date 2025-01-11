from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import random
from typing import List

from pymunk import Space
import pymunk as pm
from constants import BLOCK_SIZE, SEED, WORLD_HEIGHT, WORLD_WIDTH, clock
from game.model.blocks.airblock import AirBlock
from game.model.blocks.dirtblock import DirtBlock
from game.model.blocks.grassblock import GrassBlock
from game.model.blocks.stoneblock import StoneBlock
from game.model.entity.entities.player import Player
from game.model.utils.noisesenum import Noises
from game.model.world import World
from main import Entity
from utils.customqueue import Queue
from utils.simplexnoise import SimplexNoise


class Model:
	'''All game logic happens in this class'''
	def __init__(self, worldWidth: int, worldHeight: int):
		'''initialize the game'''
		self.world = World(worldWidth, worldHeight)
		self.player = Player(worldWidth * 0.5, worldHeight * 0.55)
		self.lightmap = [
			[0 for x in range(worldWidth)] for y in range(worldHeight)
		]
		self.entities: List[Entity] = [] # list of the entities in the world except the player
		self.space = Space()
		self.space.gravity = 0, 4 # earth's gravity is 9.81
		playerShape = pm.Poly.create_box(self.player, (self.player.width, self.player.height))
		playerShape.mass = self.player.mass
		self.space.add(self.player, playerShape)
		self.worldBody = pm.Body(body_type=pm.Body.STATIC)
		self.space.add(self.worldBody)

	def update(self):
		'''Update the model, should be called every frame'''
		self.space.step(clock.get_time() / 1000) # step the simulation in roughly 1/60s in milliseconds

	def start(self):
		'''Start game'''
		self._generateWorld()
		self._generateWorldShapes()
	
	def spawnEntity(self, entity: Entity):
		'''Spawn a new entity into the game'''
		self.entities.append(entity)
		self.space.add(entity, pm.Poly.create_box(entity, (entity.width, entity.height)))
	
	def _generateWorld(self):
		'''Generate the random world'''
		noises = self._generateAllNoise()
		self._generateTerrain(noises[Noises.GRASSHEIGHT], noises[Noises.STONEHEIGHT], noises[Noises.CAVES])
		self.generateLight()
	
	def _generateTerrain(self, grassNoise: SimplexNoise, stoneNoise: SimplexNoise, caveNoise: SimplexNoise) -> None:
		'''Place the dirt, stone, and cut out caves based on a simplex noise'''
		for x in range(self.world.width):

			# Place dirt and stone
			grassHeight = round(self.world.height * 0.58 + 9 * grassNoise[x])
			stoneHeight = round(grassHeight + 5 + 5 * stoneNoise[x])
			for y in range(self.world.height - 1, grassHeight - 1, -1):
				if y > stoneHeight:
					self.world[y][x] = StoneBlock()
					self.world.back[y][x] = StoneBlock()
				else:
					self.world[y][x] = DirtBlock()
					self.world.back[y][x] = DirtBlock()
			
			# Place grass block
			self.world[grassHeight][x] = GrassBlock()

			# Cut out caves
			for y in range(self.world.height - 1, grassHeight - 1, -1):
				if caveNoise[y][x] > 0.1:
					self.world[y][x] = AirBlock()

	@staticmethod
	def _generateAllNoise(seed: int | None = None) -> dict[Noises, SimplexNoise]:
		random.seed(seed)

		def generateNoise(noiseType: Noises, scale: float, dimension: int, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT, seed: int = SEED) -> tuple[Noises, SimplexNoise]:
			return noiseType, SimplexNoise(scale=scale, dimension=dimension, width=width, height=height, seed=seed)

		noiseParameters = (
			(Noises.GRASSHEIGHT, 19, 1), # grass height noise
			(Noises.STONEHEIGHT, 30, 1), # stone height noise
			(Noises.CAVES, 9, 2),  # caves noise
		)

		with ThreadPoolExecutor() as executor:
			futures = [executor.submit(partial(generateNoise, *parameter)) for parameter in noiseParameters]
			noises = [future.result() for future in as_completed(futures)]
			return {k: v for k, v in noises}
		
		raise Exception
	
	def generateLight(self, originr=None, originc=None) -> None:
		'''Generate the lightmap for the entire world'''
    
		def isDark(world: World, x: int, y: int) -> bool:
			return False if not world[y][x].isEmpty or not world.back[y][x].isEmpty else True

		if originr is None and originc is None:
			startr = startc = 0
			stopr = self.world.height
			stopc = self.world.width
		else:
			startr = max(originr - 6, 0)
			startc = max(originc - 6, 0)
			stopr = min(originr + 7, self.world.height)
			stopc = min(originc + 7, self.world.width)

		# loop over every block in the world
		for r in range(startr, stopr):
			for c in range(startc, stopc):
				# make queue to perform breadth first search to calculate the light at the block at row r and col c
				bfs = Queue()
				bfs.add((c, r)) # c is x and r is y
				bfs.add(None) # use Nones to track the level of the bfs
				level = 0 # keep track of level of bfs
				# set to store visited coordinates
				visited = set()
				visited.add((c, r))
				
				while bfs:
					
					if level > 6:
						self.lightmap[r][c] = 255
						break # exit after traversing 5 levels
					
					cur = bfs.poll()
					if cur is None:
						level += 1
						bfs.add(None)
						if bfs.peek() is None:
							break
						else:
							continue
					
					x, y = cur
					
					if isDark(self.world, x, y):
						self.lightmap[r][c] = max(0, (level - 1) * 51)
						break
					
					# left block
					if x - 1 >= 0: # if block is inside world bounds
						new = (x - 1, y)
						if new not in visited: # if block has not been checked
							visited.add(new)
							bfs.add(new)

					# right block
					if x + 1 < self.world.width: # if block is inside world bounds
						new = (x + 1, y)
						if new not in visited: # if block has not been checked
							visited.add(new)
							bfs.add(new)

					# upper block
					if y - 1 >= 0: # if block is inside world bounds
						new = (x, y - 1)
						if new not in visited: # if block has not been checked
							visited.add(new)
							bfs.add(new)
					
					# lower block
					if y + 1 < self.world.height: # if block is inside world bounds
						new = (x, y + 1)
						if new not in visited: # if block has not been checked
							visited.add(new)
							bfs.add(new)
	
	def _generateWorldShapes(self):
		'''Generate pymunk shapes for the world'''
		for y, row in enumerate(self.world.array):
			for x, block in enumerate(row):
				if not block.isEmpty:
					self.generateBlockShape(x, y)

	def generateBlockShape(self, x: int, y: int):
		vertices = (
						(x, y),
						(x + 1, y),
						(x + 1, y + 1),
						(x, y + 1)
					)
		shape = pm.Poly(self.worldBody, vertices)
		self.space.add(shape)
