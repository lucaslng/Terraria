import random
import time
from typing import Optional
import numpy as np
import pymunk as pm
from pymunk import Space
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

from game.model.blocks.airblock import AirBlock
from game.model.blocks.coaloreblock import CoalOreBlock
from game.model.blocks.diamondoreblock import DiamondOreBlock
from game.model.blocks.dirtblock import DirtBlock
from game.model.blocks.flowerblocks import AlliumBlock, CornflowerBlock, DandelionBlock, PoppyBlock
from game.model.blocks.goldoreblock import GoldOreBlock
from game.model.blocks.grassblock import GrassBlock
from game.model.blocks.ironoreblock import IronOreBlock
from game.model.blocks.leavesblock import LeavesBlock
from game.model.blocks.oaklogblock import LogBlock
from game.model.blocks.stoneblock import StoneBlock
from game.model.utils.biomesenum import Biome
from game.model.utils.noisesenum import Noises
from utils.customqueue import Queue
from utils.simplexnoise import SimplexNoise


# class TerrainGenerator():
#     def _placeTerrain(self, biomeNoise: SimplexNoise, grassNoise: SimplexNoise, stoneNoise: SimplexNoise, caveNoise: SimplexNoise) -> None:
#             '''Place the dirt, stone, and cut out caves'''
#             grassNoiseArray = np.array([grassNoise[x] for x in range(self.world.width)])
#             stoneNoiseArray = np.array([stoneNoise[x] for x in range(self.world.width)])
            
#             # biome
#             self.biomeArray = [Biome.FOREST if noise > 0 else Biome.PLAINS for noise in biomeNoise.noise]

#             # Calculate height maps using vectorized operations
#             grassHeight = np.round(self.world.height * 0.35 + 9 * grassNoiseArray).astype(int)
#             stoneHeight = np.round(grassHeight + 5 + 5 * stoneNoiseArray).astype(int)
            
#             for x in range(self.world.width):
#                 # Place stone and dirt
#                 for y in range(self.world.height - 1, grassHeight[x], -1):
#                     if y > stoneHeight[x]:
#                         self.world[y][x] = StoneBlock()
#                         self.world.back[y][x] = StoneBlock()
#                     else:
#                         self.world[y][x] = DirtBlock()
#                         self.world.back[y][x] = DirtBlock()
                
#                 # Place grass block at the surface
#                 if 0 <= grassHeight[x] < self.world.height:
#                     self.world[grassHeight[x]][x] = GrassBlock()
            
#             # Cut out caves
#             for y in range(self.world.height):
#                 for x in range(self.world.width):
#                     if (caveNoise[y][x] > 0.1 and 
#                         y >= grassHeight[x] and 
#                         y < self.world.height):
#                         self.world[y][x] = AirBlock()
            
#             #Generate trees / flowers depending on biome
#             for x in range(self.world.width):
#                 if isinstance(self.world[grassHeight[x]][x], GrassBlock):
#                     if random.random() > 0.65:
#                         if self.biomeArray[x] == Biome.FOREST:
#                             self._generateTree(x, grassHeight[x] - 1)
#                         elif self.biomeArray[x] == Biome.PLAINS:
#                             self.world[grassHeight[x] - 1][x] = random.choice((PoppyBlock, DandelionBlock, CornflowerBlock, AlliumBlock))()

#         def _generateTree(self, x: int, y: int) -> None:
#             '''Place a tree with base at coordinates (x, y) and a random height'''
#             if not 3 <= x < self.world.width - 3:
#                 return
#             height = random.randint(3, 7)
#             for r in range(y - height - 1, y + 1):
#                 for c in range(x - 2, x + 3):
#                     if not isinstance(self.world[r][c], AirBlock):
#                         return
#             for i in range(height):
#                 self.world[y - i][x] = LogBlock()
#             self.world[y - height][x - 2] = LeavesBlock()
#             self.world[y - height][x - 1] = LeavesBlock()
#             self.world[y - height][x] = LeavesBlock()
#             self.world[y - height][x + 1] = LeavesBlock()
#             self.world[y - height][x + 2] = LeavesBlock()
#             self.world[y - height - 1][x - 1] = LeavesBlock()
#             self.world[y - height - 1][x] = LeavesBlock()
#             self.world[y - height - 1][x + 1] = LeavesBlock()
#             self.world[y + 1][x] = DirtBlock()

#         def _placeOres(self, coalNoise: SimplexNoise, ironNoise: SimplexNoise, goldNoise: SimplexNoise, diamondNoise: SimplexNoise):
#             '''Place ores'''
#             for y in range(self.world.height):
#                 for x in range(self.world.width):
#                     if isinstance(self.world[y][x], StoneBlock):
#                         if coalNoise[y][x] > 0.3:
#                             self.world[y][x] = CoalOreBlock()
#                         elif ironNoise[y][x] > 0.38 and y > self.world.height * 0.5:
#                             self.world[y][x] = IronOreBlock()
#                         elif goldNoise[y][x] > 0.42 and y > self.world.height * 0.7:
#                             self.world[y][x] = GoldOreBlock()
#                         elif diamondNoise[y][x] > 0.46 and y > self.world.height * 0.85:
#                             self.world[y][x] = DiamondOreBlock()				

#         def _generateAllNoise(self) -> dict[Noises, SimplexNoise]:
#             total_start_time = time.perf_counter()

#             def generateNoise(noiseType: Noises, scale: float, dimension: int, width: int = self.world.width, height: int = self.world.height) -> tuple[Noises, SimplexNoise, float]:     
#                 noise = SimplexNoise(scale=scale, dimension=dimension, width=width, height=height)
#                 return noiseType, noise

#             noiseParameters = (
#                 (Noises.BIOME, 200, 1),
#                 (Noises.GRASSHEIGHT, 19, 1),
#                 (Noises.STONEHEIGHT, 30, 1),
#                 (Noises.CAVES, 9, 2),
#                 (Noises.COAL, 3.9, 2),
#                 (Noises.IRON, 3.2, 2),
#                 (Noises.GOLD, 2.5, 2),
#                 (Noises.DIAMOND, 1.2, 2),
#             )

#             with ThreadPoolExecutor() as executor:
#                 futures = [executor.submit(partial(generateNoise, *parameter)) for parameter in noiseParameters]			

#                 noises = {}
                
#                 for future in as_completed(futures):
#                     noiseType, noiseObj = future.result()
#                     noises[noiseType] = noiseObj
            
#             totalTime = time.perf_counter() - total_start_time
#             print(f"{"SimplexNoise":<20} | {totalTime:.4f}s")

#             return noises