import sys
import pygame as pg
from pygame.locals import *
import math
from math import radians, hypot
import random
from enum import Enum
import pickle  # use pickle to store save

pg.init()

WIDTH = 1000
HEIGHT = 600
FPS = 60
SURF = pg.display.set_mode((WIDTH, HEIGHT))
FRAME = SURF.get_rect()

BLOCK_SIZE = 20
WORLD_HEIGHT = 100
WORLD_WIDTH = 1000
gravity = 1

pg.display.set_caption("Terraria")
clock = pg.time.Clock()


def pixelToCoord(x: float, y: float) -> tuple[int, int]:
  """Returns coordinate based on pixel location"""
  coord = int((x + player.camera.left) // BLOCK_SIZE), int(
      (y + player.camera.top) // BLOCK_SIZE
  )
  return coord


def relativeRect(rect: pg.rect.Rect):
  """Returns on screen rect relative to the camera"""
  return pg.rect.Rect(
      rect.x - player.camera.x, rect.y - player.camera.y, rect.width, rect.height
  )


def relativeCoord(x: float, y: float) -> tuple[int, int]:
  return x - player.camera.x, y - player.camera.y


def bresenham(x0, y0, x1=FRAME.centerx, y1=FRAME.centery):
  """Bresenham's algorithm to detect first non-air block along a line, starting from end point."""

  def plotLineLow(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    xi = -1 if x0 < x1 else 1
    yi = -1 if y0 < y1 else 1
    d = (2 * dy) - dx
    y = y1
    x = x1
    while x != x0 - xi:
      blockTouched = world.blockAt(*pixelToCoord(x, y))
      if not blockTouched.isAir:
        return blockTouched
      if d > 0:
        y += yi
        d += 2 * (dy - dx)
      else:
        d += 2 * dy
      x += xi
    return None

  def plotLineHigh(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    xi = -1 if x0 < x1 else 1
    yi = -1 if y0 < y1 else 1
    d = (2 * dx) - dy
    x = x1
    y = y1
    while y != y0 - yi:
      blockTouched = world.blockAt(*pixelToCoord(x, y))
      if not blockTouched.isAir:
        return blockTouched
      if d > 0:
        x += xi
        d += 2 * (dx - dy)
      else:
        d += 2 * dx
      y += yi
    return None

  if abs(y1 - y0) < abs(x1 - x0):
    return plotLineLow(x0, y0, x1, y1)
  else:
    return plotLineHigh(x0, y0, x1, y1)


def distance(x1, y1, x2=FRAME.centerx, y2=FRAME.centery):
  return hypot(x1 - x2, y1 - y2)


class Item:
  """Base item class"""

  ITEM_SIZE = BLOCK_SIZE

  def __init__(this, name: str, texture, stackSize: int):
    this.texture = texture
    this.stackSize = stackSize
    this.name = name

  def drawItem(this, x: int, y: int):
    SURF.blit(this.itemTexture, (x, y))

  def __eq__(this, other) -> bool:
    if other is None:
      return False
    return this.name == other.name


class Inventory:
  """Inventory class"""

  class Slot:
    """Inventory slot class"""

    item: Item = None
    count: int = 0

    def __repr__(this):
      return this.item.name + "x" + str(this.count)

    def __str__(this):
      return this.item.name + "x" + str(this.count)

  def __init__(this, rows: int, cols: int):
    this.rows = rows
    this.cols = cols
    this.inventory = [[this.Slot() for _ in range(cols)]
                      for _ in range(rows)]

  def __repr__(this):
    out = ""
    for r in this.inventory:
      for slot in r:
        out += str(slot)
      out += "\n"
    print(out)
    return out

  def addItem(this, item: Item):
    for r in range(this.rows):
      for c in range(this.cols):
        slot = this.inventory[r][c]
        # if item exist increase by one
        if slot.item and slot.item == item:
          if slot.count < slot.item.stackSize:  # stack size limit
            slot.count += 1
            return
        # if slot empty add the item
        elif slot.item is None:
          slot.item = item
          slot.count = 1
          return

  def __getitem__(this, row: int):
    return this.inventory[row]


class HasInventory:
  """Parent class for classes than have an inventory"""

  def __init__(this, rows: int, cols: int):
    this.inventory = Inventory(rows, cols)


class Entity:
  """Base entity class. Contains methods for moving, drawing, and gravity"""

  hvelo = 0
  vvelo = 0
  gravityvelo = 0
  previousDirection = True
  isOnBlock = False

  def __init__(
      this,
      x: float,
      y: float,
      width: float,
      height: float,
      texture: pg.surface.Surface,
      health: float,
  ):
    this.rect = pg.rect.Rect(x, y, width, height)
    this.texture = texture
    this.reversedTexture = pg.transform.flip(texture, True, False)
    this.mask = pg.mask.from_surface(texture)
    this.health = health

  def moveLeft(this):
    if this.hvelo > -5:
      this.hvelo -= 2

  def moveRight(this):
    if this.hvelo < 5:
      this.hvelo += 2

  def jump(this):
    if this.vvelo > 4 and this.isOnBlock:
      this.vvelo -= 15

  def checkCollisionH(this) -> int:
    newrect = this.rect.copy()
    newrect.x += this.hvelo - 1
    blockRightTop = world.blockAt(
        newrect.right // BLOCK_SIZE, (newrect.top + 10) // BLOCK_SIZE
    )
    blockRightBot = world.blockAt(
        newrect.right // BLOCK_SIZE, (newrect.centery + 10) // BLOCK_SIZE
    )
    blockLeftBot = world.blockAt(
        newrect.left // BLOCK_SIZE, (newrect.centery + 10) // BLOCK_SIZE
    )
    blockLeftTop = world.blockAt(
        newrect.left // BLOCK_SIZE, (newrect.top + 10) // BLOCK_SIZE
    )
    # pg.draw.rect(SURF, (0,0,255),relativeRect(blockRightTop.rect),3)
    # pg.draw.rect(SURF, (255,0,255),relativeRect(blockRightBot.rect),3)
    # pg.draw.rect(SURF, (255,128,128),relativeRect(blockLeftBot.rect),3)
    # pg.draw.rect(SURF, (255,0,0),relativeRect(blockLeftTop.rect),3)
    if (
        blockRightBot.collides(*newrect.topleft)
        or blockRightTop.collides(*newrect.topleft)
        or blockLeftBot.collides(*newrect.topleft)
        or blockLeftTop.collides(*newrect.topleft)
    ):
      # print("side collides! not moving!")
      return 0
    else:
      return this.hvelo

  def checkCollisionV(this) -> int:
    newrect = this.rect.copy()
    newrect.y += this.vvelo
    blockTopRight = world.blockAt(
        (newrect.right - 8) // BLOCK_SIZE, newrect.top // BLOCK_SIZE
    )
    blockTopLeft = world.blockAt(
        newrect.left // BLOCK_SIZE, newrect.top // BLOCK_SIZE
    )
    blockBotRight = world.blockAt(
        (newrect.right - 8) // BLOCK_SIZE, (newrect.bottom + 10) // BLOCK_SIZE
    )
    blockBotLeft = world.blockAt(
        newrect.left // BLOCK_SIZE, (newrect.bottom + 10) // BLOCK_SIZE
    )
    # blockTopRight.drawBlockOutline((0,255,0))
    # blockTopLeft.drawBlockOutline((0,255,255))
    # pg.draw.rect(SURF, (0,0,0), relativeRect(newrect), 2)
    if this.vvelo < 0:
      # print("attepmting to move up!")
      if blockTopRight.collides(*newrect.topleft) or blockTopLeft.collides(
          *newrect.topleft
      ):
        # print("top collides! not moving!")
        this.vvelo = 0
        return 0
      else:
        return this.vvelo
    elif this.vvelo > 0:
      if blockBotRight.collides(*newrect.topleft) or blockBotLeft.collides(
          *newrect.topleft
      ):
        # print("bot collides! not moving!")
        this.isOnBlock = True
        return 0
      else:
        this.isOnBlock = False
        return this.vvelo
    else:
      return 0

  def move(this):
    if this.hvelo < 0:
      this.hvelo += min(
          1, abs(this.hvelo)
      )  # reduce horizontal velocity constantly to 0
    elif this.hvelo > 0:
      this.hvelo -= min(1, this.hvelo)
    this.rect.x += this.checkCollisionH()
    this.rect.y += this.checkCollisionV()
    if this.vvelo < 5:
      this.vvelo += gravity

  def draw(this):
    if this.hvelo < 0:
      SURF.blit(this.reversedTexture, relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.reversedTexture)
      this.previousDirection = 0
    elif this.hvelo > 0:
      SURF.blit(this.texture, relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.texture)
      this.previousDirection = 1
    elif this.previousDirection:
      SURF.blit(this.texture, relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.texture)
    else:
      SURF.blit(this.reversedTexture, relativeRect(this.rect).topleft)
      this.mask = pg.mask.from_surface(this.reversedTexture)

  def update(this):
    this.move()
    this.draw()


vertices = set()


class Player(Entity, HasInventory):
  camera = FRAME.copy()
  camera.center = (
      BLOCK_SIZE * (WORLD_WIDTH // 2),
      BLOCK_SIZE * round(WORLD_HEIGHT * 0.55),
  )
  texture = pg.transform.scale(
      pg.image.load("player.png"), (BLOCK_SIZE, BLOCK_SIZE * 2)
  )
  reversedTexture = pg.transform.flip(texture, True, False)
  reach = 4 * BLOCK_SIZE
  full_heart_texture = pg.transform.scale(
      pg.image.load("full_heart.png"), (20, 20))
  half_heart_texture = pg.transform.scale(
      pg.image.load("half_heart.png"), (20, 20))
  empty_heart_texture = pg.transform.scale(
      pg.image.load("empty_heart.png"), (20, 20))
  blockFacing = None

  def __init__(this):
    Entity.__init__(
        this,
        this.camera.centerx - BLOCK_SIZE // 2,
        this.camera.centery - BLOCK_SIZE,
        BLOCK_SIZE,
        BLOCK_SIZE * 2,
        this.texture,
        10,
    )
    HasInventory.__init__(this, 4, 10)
    this.heldSlotIndex = 0  # number from 0 to 9
    this.rect.center = this.camera.center
    this.centerRect = this.rect.copy()
    this.centerRect.center = FRAME.center
    this.max_health = 20
    this.health = this.max_health

    this.falling = False
    this.fall_start_y = None
    this.fall_damage_threshold = 4 * BLOCK_SIZE
    this.is_initial_spawn = True
    this.spawn_protection_timer = 60

  def draw_health(this):
    """Draw health as hearts on the screen"""
    HEART_SPACING = 25
    HEART_X_START = 10
    HEART_Y = 10

    full_hearts = this.health // 2
    half_hearts = this.health % 2
    empty_hearts = (this.max_health - this.health) // 2

    # Full hearts
    for i in range(full_hearts):
      SURF.blit(
          this.full_heart_texture, (HEART_X_START +
                                    i * HEART_SPACING, HEART_Y)
      )
    # Draw half heart
    if half_hearts:
      SURF.blit(
          this.half_heart_texture,
          (HEART_X_START + full_hearts * HEART_SPACING, HEART_Y),
      )
    # Draw empty hearts
    for i in range(empty_hearts):
      SURF.blit(
          this.empty_heart_texture,
          (
              HEART_X_START +
              (full_hearts + half_hearts + i) * HEART_SPACING,
              HEART_Y,
          ),
      )

  def draw(this):
    super().draw()
    this.draw_health()

  def hotbar(this) -> list[Item]:
    return this.inventory[0]

  def heldSlot(this) -> Inventory.Slot:
    slot = this.hotbar()[this.heldSlotIndex]
    if slot.item:
      return slot
    else:
      return None

  def drawHeldItem(this):
    slot = this.heldSlot()
    if slot:
      texture = pg.transform.scale_by(slot.item.texture, 0.8)
      SURF.blit(texture, FRAME.center)

  def drawHotbar(this):
    """Draws the first row of the inventory on the screen"""
    SLOT_SIZE = 40  # size of each slot
    HOTBAR_X = (WIDTH - (this.inventory.cols * SLOT_SIZE)) // 2
    HOTBAR_Y = HEIGHT - SLOT_SIZE - 10
    FONT = pg.font.Font(None, 20)

    for col in range(this.inventory.cols):
      slot_x = HOTBAR_X + col * SLOT_SIZE
      slot_y = HOTBAR_Y

      # draws the slots
      pg.draw.rect(SURF, (200, 200, 200),
                   (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE))
      if col == this.heldSlotIndex:
        pg.draw.rect(SURF, (0, 0, 0),
                   (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE), 2)
      else:
        pg.draw.rect(SURF, (90, 90, 90),
                   (slot_x, slot_y, SLOT_SIZE, SLOT_SIZE), 2)

      slot = this.hotbar()[col]
      if slot.item is not None:
        item_texture = slot.item.texture
        scaled_texture = pg.transform.scale(
            item_texture, (SLOT_SIZE - 6, SLOT_SIZE - 6)
        )
        # center texture in the slot
        texture_rect = scaled_texture.get_rect(
            center=(slot_x + SLOT_SIZE // 2, slot_y + SLOT_SIZE // 2)
        )
        SURF.blit(scaled_texture, texture_rect.topleft)

        if slot.count > 0:
          count_text = FONT.render(
              str(slot.count), True, (255, 255, 255))
          # item counter is in the bottom right of the slot
          text_rect = count_text.get_rect(
              bottomright=(slot_x + SLOT_SIZE - 5,
                           slot_y + SLOT_SIZE - 5)
          )
          SURF.blit(count_text, text_rect.topleft)

  def move(this):
    if this.is_initial_spawn:
      this.falling = False
      this.fall_start_y = None

      this.spawn_protection_timer -= 1
      if this.spawn_protection_timer <= 0:
        this.is_initial_spawn = False

    if this.vvelo > 0:
      if not this.falling:
        this.falling = True
        this.fall_start_y = this.rect.bottom

    super().move()
    this.camera.center = this.rect.center

    if this.falling and this.isOnBlock and not this.is_initial_spawn:
      fall_distance = abs(this.fall_start_y - this.rect.bottom)

      if fall_distance > this.fall_damage_threshold:
        # damage based on fall distance
        damage = int(
          (fall_distance - this.fall_damage_threshold) / BLOCK_SIZE)
        this.health = max(0, this.health - damage)

      this.falling = False
      this.fall_start_y = None

  def mine(this):
    if this.blockFacing:
      if this.blockFacing.amountBroken < this.blockFacing.hardness:
        this.blockFacing.amountBroken += 1 / FPS
      else:
        print("mined", this.blockFacing.name,
              "got", this.blockFacing.item.name)
        world[this.blockFacing.y][this.blockFacing.x] = Air(
            this.blockFacing.x, this.blockFacing.y
        )
        this.inventory.addItem(this.blockFacing.item)

  def drawCircle(this):
    pg.draw.circle(ASURF, (0, 0, 0, 120), FRAME.center, BLOCK_SIZE * 4)

  def getBlockFacing(this):
    """Returns the block that the player is facing, if it is in range"""
    block = bresenham(*pg.mouse.get_pos())
    if block is None:
      return None
    for vertex in block.vertices:
      if distance(*relativeCoord(*vertex)) < this.reach:
        return block
    return None

  def drawBlockFacing(this):
    if this.blockFacing:
      this.blockFacing.drawBlockOutline((0, 0, 0, 200))

  # def sweep(this):
  # https://www.redblobgames.com/articles/visibility/
  # endpoints = []

  def update(this):
    super().update()
    this.blockFacing = this.getBlockFacing()
    this.drawBlockFacing()
    this.drawHotbar()
    this.drawHeldItem()


ASURF = pg.surface.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
ASURF.fill((0, 0, 0, 0))
player = Player()


class Block:
  SIZE = BLOCK_SIZE

  def __init__(
    this,
    name: str,
    texture,
    x: int,
    y: int,
    item: Item,
    hardness: float,
    isAir=False,
  ):
    this.name = name
    this.texture = texture
    this.rect = pg.rect.Rect(
      x * BLOCK_SIZE, y * BLOCK_SIZE, this.SIZE, this.SIZE)
    this.vertices = (
      this.rect.topleft,
      this.rect.topright,
      this.rect.bottomleft,
      this.rect.bottomright,
    )
    this.mask = pg.mask.from_surface(texture)
    this.x = x
    this.y = y
    this.item = item
    this.hardness = hardness
    this.isAir = isAir
    this.amountBroken = 0

  def drawBlockOutline(this, color):
    pg.draw.rect(ASURF, color, relativeRect(this.rect), 2)

  def drawBlock(this):
    SURF.blit(this.texture, relativeRect(this.rect))
    breakingRect = relativeRect(this.rect.copy())
    breakingRect.scale_by_ip(
      this.amountBroken / this.hardness, this.amountBroken / this.hardness
    )
    pg.draw.rect(ASURF, (0, 0, 0, 100), breakingRect)

  def offset(this, x: int, y: int) -> tuple[int, int]:
    return x - this.rect.x, y - this.rect.y

  def collides(this, x: int, y: int) -> bool:
    if this.isAir:
      return False
    if this.mask.overlap(player.mask, this.offset(x, y)):
      # pg.draw.rect(SURF, (255, 0, 0), relativeRect(this.rect), width=3)
      return True
    else:
      return False

  def isInCamera(this):
    return this.rect.colliderect(player.camera)

  def __repr__(this):
    return this.name

  def __hash__(this):
    return hash((this.x, this.y))

  def __eq__(this, other):
    return hash(this) == hash(other)


class Air(Block):
  texture = pg.surface.Surface((BLOCK_SIZE, BLOCK_SIZE))
  texture.fill((0, 0, 0, 0))
  item = Item("Air", texture, 0)

  def __init__(this, x=-1, y=-1):
    super().__init__("Air", this.texture, x, y, this.item, 0, isAir=True)


class DirtVariant:
  itemTexture = pg.transform.scale(pg.image.load("dirt.png"), (15, 15))

  def __init__(this, name: str, texture):
    this.name = name
    this.texture = texture
    this.item = Item("Dirt", this.itemTexture, 64)


class DirtVariantDirt(DirtVariant):
  dirtTexture = pg.transform.scale(
    DirtVariant.itemTexture, (BLOCK_SIZE, BLOCK_SIZE))

  def __init__(this):
    super().__init__("Dirt", this.dirtTexture)


class DirtVariantGrass(DirtVariant):
  grassTexture = pg.transform.scale(
    pg.image.load("grass_block.png"), (BLOCK_SIZE, BLOCK_SIZE)
  )
  grassItemTexture = pg.transform.scale(grassTexture, (15, 15))

  def __init__(this):
    super().__init__("Grass Block", this.grassTexture)


class Dirt(Block):
  def __init__(this, x, y, variant: DirtVariant = DirtVariantDirt()):
    super().__init__(variant.name, variant.texture, x, y, variant.item, 1)


class World:
  seed = random.randint(0, sys.maxsize)
  def __init__(this):
    this.array = [
        [Air(x, y) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    this.__generateAllDirt()

  # https://gpfault.net/posts/perlin-noise.txt.html
  @staticmethod
  def __simplexNoise1D(length, scale=1.0, seed=0):
    """
    Generate a 1D array of simplex noise.

    Args:
        length (int): Length of the noise array.
        scale (float): Scale factor for the noise.
        seed (int): Seed for reproducibility.

    Returns:
        list: Array of 1D simplex noise values.
    """
    def dot_product(grad, x):
        """Compute the dot product of the gradient and distance."""
        return grad * x

    def gradient(h):
        """Generate gradient based on hash value."""
        return 1 if h % 2 == 0 else -1

    def fade(t):
        """Fade function as defined by Ken Perlin. This eases coordinate values."""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(a, b, t):
        """Linear interpolation between a and b using t."""
        return a + t * (b - a)

    def generate_permutation(seed):
      """Generate a pseudo-random permutation table."""
      random.seed(seed)
      p = list(range(256))
      random.shuffle(p)
      return p + p  # Double the permutation table
    perm = generate_permutation(seed)
    noise = []

    for i in range(length):
        # Scaled position
        x = i / scale

        # Determine lattice points
        x0 = math.floor(x)  # Left point
        x1 = x0 + 1         # Right point

        # Relative positions
        dx0 = x - x0
        dx1 = x - x1

        # Apply fade function to smooth the interpolation
        u = fade(dx0)

        # Gradient indices
        g0 = gradient(perm[x0 % 256])
        g1 = gradient(perm[x1 % 256])

        # Compute contributions from each gradient
        n0 = dot_product(g0, dx0)
        n1 = dot_product(g1, dx1)

        # Interpolate between contributions
        value = lerp(n0, n1, u)
        noise.append(value)

    return noise

  def __generateAllDirt(this):
    noise = this.__simplexNoise1D(length=WORLD_WIDTH, scale=18, seed=this.seed)
    print(noise)
    for x in range(0, WORLD_WIDTH):
      grass_height = round(WORLD_HEIGHT * 0.6 + 9 * noise[x])

      # generate grass on the top layer
      for y in range(WORLD_HEIGHT - 1, grass_height, -1):
        this.array[y][x] = Dirt(x, y)

      this.array[grass_height][x] = Dirt(
          x, grass_height, DirtVariantGrass()
      )

  def hoveredBlock(this) -> Block:
    mousepos = pg.mouse.get_pos()
    return this.blockAt(*pixelToCoord(*mousepos))

  def blockAt(this, x, y) -> Block:
    return this[y][x]

  def __getitem__(this, x: int):
    return this.array[x]

  def draw(this):
    for y in range(
        player.camera.top // BLOCK_SIZE, (player.camera.bottom //
                                          BLOCK_SIZE) + 1
    ):
      for x in range(
          player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1,
      ):
        block = this[y][x]
        if not block.isAir:
          block.drawBlock()

  def __repr__(this):
    out = ""
    for row in this.array:
      for block in row:
        if block.name == "Air":
          out += "."
        elif block.name == "Dirt":
          out += "X"
      out += "\n"
    return out


world = World()


while True:
  SURF.fill((255, 255, 255))
  ASURF.fill((0, 0, 0, 0))
  keys = pg.key.get_pressed()
  vertices.clear()

  world.draw()
  player.update()

  # temporarily game over logic
  if player.health <= 0:
    print("The skbidi has died")
    pg.quit()
    sys.exit()

  if keys[pg.K_a]:
    player.moveLeft()
  if keys[pg.K_d]:
    player.moveRight()
  if keys[pg.K_SPACE]:
    player.jump()
  if keys[pg.K_1]:
    player.heldSlotIndex = 0
  if keys[pg.K_2]:
    player.heldSlotIndex = 1
  if keys[pg.K_3]:
    player.heldSlotIndex = 2
  if keys[pg.K_4]:
    player.heldSlotIndex = 3
  if keys[pg.K_5]:
    player.heldSlotIndex = 4
  if keys[pg.K_6]:
    player.heldSlotIndex = 5
  if keys[pg.K_7]:
    player.heldSlotIndex = 6
  if keys[pg.K_8]:
    player.heldSlotIndex = 7
  if keys[pg.K_9]:
    player.heldSlotIndex = 8
  if keys[pg.K_0]:
    player.heldSlotIndex = 9

  if pg.mouse.get_pressed()[0]:
    player.mine()
  for event in pg.event.get():
    if event.type == QUIT:
      pg.quit()
      sys.exit()

  SURF.blit(ASURF, (0, 0))
  pg.display.flip()
  clock.tick(FPS)
