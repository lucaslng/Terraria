import numpy as np
from utils.constants import BIG


class SimplexNoise:
    '''https://github.com/SRombauts/SimplexNoise/blob/master/src/SimplexNoise.cpp'''
    def __init__(self, scale: float, dimension: int, width: int, height: int):

        self.rng = np.random.RandomState()
        
        if dimension == 1:
            self.noise = self._noise1d(width, scale)
        elif dimension == 2:
            self.noise = self._noise2d(width, height, scale)
        else:
            raise ValueError("Dimension must be 1 or 2")

    def __getitem__(self, x: int) -> float | np.ndarray:
        return self.noise[x]

    @staticmethod
    def _fade(t: np.ndarray) -> np.ndarray:
        '''this function has a smooth curve to generate the smooth curves of the simplex noise'''
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def _lerp(a: np.ndarray, b: np.ndarray, weight: np.ndarray) -> np.ndarray:
        '''
        Linear interpolation between a and b with a weight.
        weight should be in range [0.0, 1.0], which represents which point is weighted more in the interpolation
        '''
        return (1 - weight) * a + weight * b

    def _generate_permutation(self) -> np.ndarray:
        '''
        generates a shuffled array of the numbers 0-255, then the array is repeated twice for wrapping.
        the array is used to calculate the random noise value of each point
        '''
        temp_rng = np.random.RandomState(self.rng.randint(0, BIG))
        p = temp_rng.permutation(256)
        return np.tile(p, 2)

    @staticmethod
    def _gradient1d(h: np.ndarray) -> np.ndarray:
        '''
        The gradient determines the direction of the slope. for 1d arrays the slope can only be up or down.
        % 2 shows there are 2 directions being picked from
        '''
        return np.where(h % 2 == 0, 1, -1)

    @staticmethod
    def _gradient2d(h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        '''
        the gradient in a 2d array has 4 directions instead of 2, so 2 different gradient arrays are generated.
        the value is picked % 4 which shows the 4 directions being picked from
        '''
        h_mod = h % 4
        grad_x = np.where(h_mod < 2, np.where(h_mod == 0, 1, -1), 0)
        grad_y = np.where(h_mod >= 2, np.where(h_mod == 2, 1, -1), 0)
        return grad_x, grad_y

    def _noise1d(self, width: int, scale: float = 1.0) -> np.ndarray:
        '''generate 1d simplex noise'''
        x = np.arange(width, dtype=np.float32) / scale # generate an array of evenly spaced points scaled out by the scale parameter
        x0 = np.floor(x).astype(np.int32) # find the grid cell that the point belongs using floor to convert the float to an int
        x1 = x0 + 1 # x0 is the floor cell, x1 is the ceil cell

        dx0 = x - x0 # the fractional distance from the point to the floor cell
        dx1 = x - x1 # the fractional distance from the point to the ceil cell
        u = self._fade(dx0) # smooth the fractional distance using the fade function

        perm = self._generate_permutation()
        ix0 = perm[x0 % 256] # generates the hash values, basically converting the grid point into a random number
        ix1 = perm[x1 % 256]

        g0 = self._gradient1d(ix0) # gets the slope (either -1 or 1) based on the random hash value
        g1 = self._gradient1d(ix1)
        n0 = g0 * dx0 # multplies the fractional distance by either -1 or 1
        n1 = g1 * dx1

        return self._lerp(n0, n1, u) # blend the contributions of x0 and x1, weighted by u

    def _noise2d(self, width: int, height: int, scale: float = 1.0) -> np.ndarray:
        '''generate 2D Simplex noise'''
        # create coordinate arrays
        y, x = np.mgrid[0:height, 0:width]
        x = x.astype(np.float32) / scale
        y = y.astype(np.float32) / scale

        # calculate integer coordinates
        x0 = np.floor(x).astype(np.int32) % 256
        y0 = np.floor(y).astype(np.int32) % 256
        x1 = (x0 + 1) % 256
        y1 = (y0 + 1) % 256

        # calculate fractional coordinates
        dx0 = x - np.floor(x)
        dy0 = y - np.floor(y)
        dx1 = dx0 - 1
        dy1 = dy0 - 1

        # calculate fade curves
        u = self._fade(dx0)
        v = self._fade(dy0)

        # get permutation table
        perm = self._generate_permutation()

        # calculate hash values for all corners
        aa = perm[x0] + y0
        ab = perm[x0] + y1
        ba = perm[x1] + y0
        bb = perm[x1] + y1

        # get final hashed values
        a0 = perm[aa % 256]
        a1 = perm[ab % 256]
        b0 = perm[ba % 256]
        b1 = perm[bb % 256]

        # calculate gradients and dot products
        g00 = self._gradient2d(a0)
        g01 = self._gradient2d(a1)
        g10 = self._gradient2d(b0)
        g11 = self._gradient2d(b1)

        n00 = g00[0] * dx0 + g00[1] * dy0
        n01 = g01[0] * dx0 + g01[1] * dy1
        n10 = g10[0] * dx1 + g10[1] * dy0
        n11 = g11[0] * dx1 + g11[1] * dy1

        # interpolate between values
        nx0 = self._lerp(n00, n10, u)
        nx1 = self._lerp(n01, n11, u)
        
        return self._lerp(nx0, nx1, v)