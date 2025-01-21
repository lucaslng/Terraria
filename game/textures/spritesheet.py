import pygame as pg


class SpriteSheet:
  """sprite sheet class"""

  def __init__(this, imageName: str) -> None:
    this.sheet = pg.image.load(imageName).convert_alpha()

  def get(this, x, y, width, height, scale: int | None = None) -> pg.Surface:
    image = pg.Surface((width, height), pg.SRCALPHA)
    image.blit(this.sheet, (0, 0), (x, y, width, height))

    if scale:
      image = pg.transform.scale(image, (scale, scale))

    return image
