import numpy as np
from typing import Union, Tuple
from utils.constants import BIG, SEED, WORLD_HEIGHT, WORLD_WIDTH


class SimplexNoise:
    def __init__(self, scale: float, dimension: int, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT, seed: int = SEED):
        self.seed = int(seed)
        
        self.rng = np.random.RandomState(self.seed)
        
        if dimension == 1:
            self.noise = self._noise1d(width, scale)
        elif dimension == 2:
            self.noise = self._noise2d(width, height, scale)
        else:
            raise ValueError("Dimension must be 1 or 2")

    def __getitem__(self, x: int) -> Union[float, np.ndarray]:
        return self.noise[x]

    @staticmethod
    def _fade(t: np.ndarray) -> np.ndarray:
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def _lerp(a: np.ndarray, b: np.ndarray, t: np.ndarray) -> np.ndarray:
        """
        Linear interpolation between a and b using parameter t.
        t should be in range [0.0, 1.0].
        """
        return (1 - t) * a + t * b

    def _generate_permutation(self) -> np.ndarray:
        temp_rng = np.random.RandomState(self.rng.randint(0, BIG))
        p = temp_rng.permutation(256)
        return np.tile(p, 2)

    @staticmethod
    def _gradient1d(h: np.ndarray) -> np.ndarray:
        return np.where(h % 2 == 0, 1, -1)

    @staticmethod
    def _gradient2d(h: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Vectorized 2D gradient computation.
        Returns two arrays for x and y components of the gradient vectors.
        """
        h_mod = h % 4
        grad_x = np.where(h_mod < 2, np.where(h_mod == 0, 1, -1), 0)
        grad_y = np.where(h_mod >= 2, np.where(h_mod == 2, 1, -1), 0)
        return grad_x, grad_y

    def _noise1d(self, width: int, scale: float = 1.0) -> np.ndarray:
        """Generate 1D Simplex noise using vectorized operations."""
        x = np.arange(width, dtype=np.float32) / scale
        x0 = np.floor(x).astype(np.int32)
        x1 = x0 + 1

        dx0 = x - x0
        dx1 = x - x1
        u = self._fade(dx0)

        perm = self._generate_permutation()
        ix0 = perm[x0 % 256]
        ix1 = perm[x1 % 256]

        g0 = self._gradient1d(ix0)
        g1 = self._gradient1d(ix1)
        n0 = g0 * dx0
        n1 = g1 * dx1

        return self._lerp(n0, n1, u)

    def _noise2d(self, width: int, height: int, scale: float = 1.0) -> np.ndarray:
        """Generate 2D Simplex noise using vectorized operations."""
        # Create coordinate arrays
        y, x = np.mgrid[0:height, 0:width]
        x = x.astype(np.float32) / scale
        y = y.astype(np.float32) / scale

        # Calculate integer coordinates
        x0 = np.floor(x).astype(np.int32) % 256
        y0 = np.floor(y).astype(np.int32) % 256
        x1 = (x0 + 1) % 256
        y1 = (y0 + 1) % 256

        # Calculate fractional coordinates
        dx0 = x - np.floor(x)
        dy0 = y - np.floor(y)
        dx1 = dx0 - 1
        dy1 = dy0 - 1

        # Calculate fade curves
        u = self._fade(dx0)
        v = self._fade(dy0)

        # Get permutation table
        perm = self._generate_permutation()

        # Calculate hash values for all corners
        # This is the key fix for the broadcasting issue
        aa = perm[x0] + y0
        ab = perm[x0] + y1
        ba = perm[x1] + y0
        bb = perm[x1] + y1

        # Get final hashed values
        a0 = perm[aa % 256]
        a1 = perm[ab % 256]
        b0 = perm[ba % 256]
        b1 = perm[bb % 256]

        # Calculate gradients and dot products
        g00 = self._gradient2d(a0)
        g01 = self._gradient2d(a1)
        g10 = self._gradient2d(b0)
        g11 = self._gradient2d(b1)

        n00 = g00[0] * dx0 + g00[1] * dy0
        n01 = g01[0] * dx0 + g01[1] * dy1
        n10 = g10[0] * dx1 + g10[1] * dy0
        n11 = g11[0] * dx1 + g11[1] * dy1

        # Interpolate between values
        nx0 = self._lerp(n00, n10, u)
        nx1 = self._lerp(n01, n11, u)
        
        return self._lerp(nx0, nx1, v)