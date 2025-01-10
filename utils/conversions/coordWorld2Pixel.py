from constants import BLOCK_SIZE


def coordWorld2Pixel(x: int, y: int) -> tuple[int, int]:
  '''convert world coordinates to pixel'''
  return x * BLOCK_SIZE, y * BLOCK_SIZE