import math
import random
from constants import BIG, SEED, WORLD_HEIGHT, WORLD_WIDTH
from pygame.math import lerp

class SimplexNoise:
	def __init__(self, scale: float, dimension: int, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT, seed: int = SEED):
		self.seed = seed
		if dimension == 1:
			self.noise = self._noise1d(width, scale)
		elif dimension == 2:
			self.noise = self.__noise2d(width, height, scale)
		else:
			raise ValueError

	def __getitem__(self, x: int):
		return self.noise[x]

	@staticmethod
	def __fade(t):
		return t * t * t * (t * (t * 6 - 15) + 10)

	def _generatePermutation(self):
		random.seed(random.randint(0, BIG))
		p = list(range(256))
		random.shuffle(p)
		random.seed(self.seed)
		return p + p  # Double for wraparound

	@staticmethod
	def _gradient1d(h):
		return 1 if h % 2 == 0 else -1

	@staticmethod
	def _gradient2d(h):
		"""Compute 2D gradient direction based on hash value."""
		directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
		return directions[h % 4]

	def _noise1d(self, width, scale=1.0):
		perm = self._generatePermutation()
		noise = []

		for i in range(width):
			x = i / scale
			x0 = math.floor(x)
			x1 = x0 + 1

			dx0 = x - x0
			dx1 = x - x1

			u = self.__fade(dx0)

			g0 = self._gradient1d(perm[x0 % 256])
			g1 = self._gradient1d(perm[x1 % 256])

			n0 = g0 * dx0
			n1 = g1 * dx1

			value = lerp(n0, n1, u)
			noise.append(value)

		return noise

	def __noise2d(self, width, height, scale=1.0):
		perm = self._generatePermutation()
		noise = []

		for y in range(height):
			row = []
			for x in range(width):
				sx = x / scale
				sy = y / scale

				x0 = math.floor(sx)
				y0 = math.floor(sy)

				x1 = x0 + 1
				y1 = y0 + 1

				dx0 = sx - x0
				dy0 = sy - y0
				dx1 = sx - x1
				dy1 = sy - y1

				u = self.__fade(dx0)
				v = self.__fade(dy0)

				g00 = self._gradient2d(perm[(x0 + perm[y0 % 256]) % 256])
				g10 = self._gradient2d(perm[(x1 + perm[y0 % 256]) % 256])
				g01 = self._gradient2d(perm[(x0 + perm[y1 % 256]) % 256])
				g11 = self._gradient2d(perm[(x1 + perm[y1 % 256]) % 256])

				n00 = g00[0] * dx0 + g00[1] * dy0
				n10 = g10[0] * dx1 + g10[1] * dy0
				n01 = g01[0] * dx0 + g01[1] * dy1
				n11 = g11[0] * dx1 + g11[1] * dy1

				nx0 = lerp(n00, n10, u)
				nx1 = lerp(n01, n11, u)

				value = lerp(nx0, nx1, v)
				row.append(value)
			noise.append(row)

		return noise