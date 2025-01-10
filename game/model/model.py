from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import random
from constants import SEED, WORLD_HEIGHT, WORLD_WIDTH
from game.model.entity.player import Player
from game.model.utils.noisesenum import Noises
from game.model.world import World
from utils.simplexnoise import SimplexNoise


class Model:
	'''All game logic happens in this class'''
	def __init__(self, worldWidth: int, worldHeight: int):
		'''initialize the game'''
		self.world = World(worldWidth, worldHeight)
		self.player = Player(worldWidth * 0.5, worldHeight * 0.55)
	
	def start(self):
		'''Start game'''
		self._generateWorld()
	
	def _generateWorld(self):
		'''Generate the random world'''
		noises = self._generateAllNoise()
		self.placeDirt(noises.get(Noises.GRASSHEIGHT))
	
	def placeDirt(self, noise: SimplexNoise):
		'''Place the dirt based on a simplex noise'''
		


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
		