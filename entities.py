import pygame as pg, math
from pygame.math import Vector2
from dataclasses import dataclass

from constants import *
from sprites import sprites
from items import *
from blocks import *
from inventory import *
from utils.utils import pixelToCoord, relativeRect, relativeCoord, bresenham
from world import WorldLoader

loader = WorldLoader(WIDTH, HEIGHT)
world = loader.world

class Entity:
  """Base entity class. Contains methods for moving, drawing, and gravity"""

  hvelo = 0
  vvelo = 0
  gravityvelo = 0
  previousDirection = True
  isOnBlock = False
  animations = {}

  def __init__(
      self,
      x: float,
      y: float,
      width: float,
      height: float,
      texture: pg.surface.Surface,
      health: float,
      speed: float,
      jumpHeight: float,
  ):
    self.rect = pg.rect.Rect(x, y, width, height)
    self.texture = texture
    self.reversedTexture = pg.transform.flip(texture, True, False).convert_alpha()
    self.mask = pg.mask.from_surface(texture)
    self.health = health
    self.speed = speed
    self.jumpHeight = jumpHeight
    
    # kinematic vectors
    self.position = Vector2(x, y)
    self.velocity = Vector2()
    self.accel = Vector2()
    
    # kinematic constants
    self.HORIZONTAL_ACCEL = 1
    self.HORIZONTAL_FRICTION = 0.2

  def moveLeft(self) -> None:
    if self.hvelo > -5:
      self.hvelo -= self.speed

  def moveRight(self) -> None:
    if self.hvelo < 5:
      self.hvelo += self.speed

  def jump(self) -> None:
    if self.vvelo > 4 and self.isOnBlock:
      self.vvelo -= self.jumpHeight

  def checkCollisionH(self) -> int:
    newrect = self.rect.copy()
    newrect.x += self.hvelo - 1
    blockRightTop = world.blockAt(
      x = newrect.right // BLOCK_SIZE,
      y = (newrect.top + 10) // BLOCK_SIZE
    )
    blockRightBot = world.blockAt(
      x = newrect.right // BLOCK_SIZE, 
      y = (newrect.centery + 10) // BLOCK_SIZE
    )
    blockLeftBot = world.blockAt(
      x = newrect.left // BLOCK_SIZE,
      y = (newrect.centery + 10) // BLOCK_SIZE
    )
    blockLeftTop = world.blockAt(
      x = newrect.left // BLOCK_SIZE,
      y = (newrect.top + 10) // BLOCK_SIZE
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
      return self.hvelo

  def checkCollisionV(self) -> int:
    newrect = self.rect.copy()
    newrect.y += self.vvelo
    blockTopRight = world.blockAt(
      x = (newrect.right - 8) // BLOCK_SIZE,
      y = newrect.top // BLOCK_SIZE
    )
    blockTopLeft = world.blockAt(
      x = newrect.left // BLOCK_SIZE,
      y = newrect.top // BLOCK_SIZE
    )
    blockBotRight = world.blockAt(
      x = (newrect.right - 8) // BLOCK_SIZE,
      y = (newrect.bottom + 10) // BLOCK_SIZE
    )
    blockBotLeft = world.blockAt(
      x = newrect.left // BLOCK_SIZE,
      y = (newrect.bottom + 10) // BLOCK_SIZE
    )
    # blockTopRight.drawBlockOutline((0,255,0))
    # blockTopLeft.drawBlockOutline((0,255,255))
    # pg.draw.rect(SURF, (0,0,0), relativeRect(newrect), 2)
    if self.vvelo < 0:
      # print("attepmting to move up!")
      if (
        blockTopRight.collides(*newrect.topleft)
        or blockTopLeft.collides(*newrect.topleft)
        ):
        # print("top collides! not moving!")
        self.vvelo = 0
        return 0
      else:
        return self.vvelo
    elif self.vvelo > 0:
      if (
        blockBotRight.collides(*newrect.topleft)
        or blockBotLeft.collides(*newrect.topleft)
      ):
        # print("bot collides! not moving!")
        self.isOnBlock = True
        return 0
      else:
        self.isOnBlock = False
        return self.vvelo
    else:
      return 0

  def move(self) -> None:
    if self.hvelo < 0:
      self.hvelo += min(1, abs(self.hvelo))  # reduce horizontal velocity constantly to 0
    elif self.hvelo > 0:
      self.hvelo -= min(1, self.hvelo)
    self.rect.x += self.checkCollisionH()
    self.rect.y += self.checkCollisionV()
    if self.vvelo < 5:
      self.vvelo += gravity

  def draw(self) -> None:
    if self.hvelo < 0:
      SURF.blit(self.reversedTexture, relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.reversedTexture)
      self.previousDirection = 0
    elif self.hvelo > 0:
      SURF.blit(self.texture, relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.texture)
      self.previousDirection = 1
    elif self.previousDirection:
      SURF.blit(self.texture, relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.texture)
    else:
      SURF.blit(self.reversedTexture, relativeRect(self.rect).topleft)
      self.mask = pg.mask.from_surface(self.reversedTexture)

  def update(self) -> None:
    self.move()
    self.draw()


class Player(Entity, HasInventory, Light):
  texture = sprites["cat"]["walk"][0]
  selfSprites = sprites["cat"]
  blockFacing = None
  reach = 4 * BLOCK_SIZE
  
  full_heart_texture = sprites["full heart"]
  half_heart_texture = sprites["half heart"]
  empty_heart_texture = sprites["empty heart"]

  def __init__(self):
    Light.__init__(self, BLOCK_SIZE//2, *FRAME.center, relative=False)
    self.camera = FRAME.copy()
    self.camera.center = (
      BLOCK_SIZE * (WORLD_WIDTH // 2),
      BLOCK_SIZE * round(WORLD_HEIGHT * 0.55),
    )
    
    Entity.__init__(
        self,
        self.camera.centerx - BLOCK_SIZE // 2,
        self.camera.centery - BLOCK_SIZE // 2,
        BLOCK_SIZE,
        BLOCK_SIZE,
        self.texture,
        10,
        2,
        18,
    )
    self.mask = pg.mask.Mask((20, 20), True)

    HasInventory.__init__(self, 4, 10, 15, 80)
    self.cursorSlot = Slot()
    
    self.heldSlotIndex = 0  # number from 0 to 9
    self.rect.center = self.camera.center
    self.centerRect = self.rect.copy()
    self.centerRect.center = FRAME.center
    self.max_health = 20
    self.health = self.max_health

    self.falling = False
    self.fall_start_y = None
    self.fall_damage_threshold = 10 * BLOCK_SIZE
    self.is_initial_spawn = True
    self.spawn_protection_timer = 120

    self.usingItem = False
    self.placingBlock = False

    #Add items at the beginning of the game to the player
    defaultItems = [GoldPickaxe(), IronAxe(), StoneAxe(), WoodenShovel(), CraftingTableItem()] + [
    CobbleStoneItem() for _ in range(192)] + [TorchItem() for _ in range(64)]
    
    for item in defaultItems: 
        self.inventory.addItem(item)

    # beginning tick, tick length
    self.animations["usingItem"] = pg.time.get_ticks() + 200
    self.animations["placingBlock"] = 250

  def draw_health(self):
    """Draw health as hearts on the screen"""
    HEART_SPACING = 25
    HEART_X_START = 10
    HEART_Y = 10

    full_hearts = self.health // 2
    half_hearts = self.health % 2
    empty_hearts = (self.max_health - self.health) // 2

    #Full hearts
    for i in range(full_hearts):
      OVERLAY.blit(self.full_heart_texture, (HEART_X_START + i * HEART_SPACING, HEART_Y))   
    #Half hearts
    if half_hearts:
      OVERLAY.blit(self.half_heart_texture,(HEART_X_START + full_hearts * HEART_SPACING, HEART_Y))     
    #Empty hearts
    for i in range(empty_hearts):
      OVERLAY.blit(self.empty_heart_texture,(HEART_X_START +(full_hearts + half_hearts + i) * HEART_SPACING,HEART_Y))

  def draw(self):
    # print(self.vvelo)
    if self.hvelo < 0:
      if self.vvelo < -4:
        self.selfSprites["jump"].drawFrame(*relativeRect(self.rect).topleft, 2, flipped=True)
      else:
        self.selfSprites["walk"].drawAnimated(*relativeRect(self.rect).topleft, flipped=True)
      self.previousDirection = 0
    elif self.hvelo > 0:
      if self.vvelo < -4:
        self.selfSprites["jump"].drawFrame(*relativeRect(self.rect).topleft, 2)
      else:
        self.selfSprites["walk"].drawAnimated(*relativeRect(self.rect).topleft)
      self.previousDirection = 1
    elif self.previousDirection:
      self.selfSprites["sit"].drawAnimated(*relativeRect(self.rect).topleft)
    else:
      self.selfSprites["sit"].drawAnimated(*relativeRect(self.rect).topleft, flipped=True)

  def hotbar(self) -> list[Slot]:
    '''Returns the first row of the player's inventory'''
    return self.inventory[0]

  def heldSlot(self) -> Slot:
    '''Returns the held slot, or None if the slot is empty'''
    slot = self.hotbar()[self.heldSlotIndex]
    if slot:
      return slot
    else:
      return None
  
  def drawCursorSlot(self):
    ...

  def executeHeldSlotEffect(self):
    '''do whatever the heldslot says needs to be done'''
    if self.heldSlot().item and self.heldSlot().item.isExecutable():
      self.heldSlot().item.execute()
  
  def changeSlot(self, index: int):
    self.heldSlot().isActive = False
    if self.heldSlot().item and self.heldSlot().item.isExecutable():
      self.heldSlot().item.unexecute()
    self.heldSlotIndex = index
    self.heldSlot().isActive = True

  def drawHeldItem(self):
    slot = self.heldSlot()
    if slot.item:
      texture = slot.item.slotTexture()
      if self.usingItem and pg.time.get_ticks() % 200 < 100:
        texture = pg.transform.rotozoom(texture, -35, 1)
      elif self.animations["placingBlock"] < 100:
        texture = pg.transform.rotozoom(
          texture, -self.animations["placingBlock"] / 3.8, 1)
        self.animations["placingBlock"] += 1000 / FPS
        self.placingBlock = False
      if self.previousDirection == False:
        texture = pg.transform.flip(texture, True, False)
      
      SURF.blit(texture, FRAME.center)

  def drawHotbar(self):
    """Draws the first row of the inventory on the screen"""
    HOTBAR_X = (WIDTH - (self.inventory.cols * Slot.size)) // 2
    HOTBAR_Y = HEIGHT - Slot.size - 10

    for col in range(self.inventory.cols):
      slot_x = HOTBAR_X + col * Slot.size
      slot_y = HOTBAR_Y
      slot = self.hotbar()[col]
      slot.draw(slot_x, slot_y)

  def move(self):
    if self.is_initial_spawn:
      self.falling = False
      self.fall_start_y = None

      self.spawn_protection_timer -= 1
      if self.spawn_protection_timer <= 0:
        self.is_initial_spawn = False

    if self.vvelo > 0:
      if not self.falling:
        self.falling = True
        self.fall_start_y = self.rect.bottom

    super().move()
    self.camera.center = self.rect.center

    if self.falling and self.isOnBlock and not self.is_initial_spawn:
      fall_distance = abs(self.fall_start_y - self.rect.bottom)

      if fall_distance > self.fall_damage_threshold:
        # damage based on fall distance
        damage = int(
          (fall_distance - self.fall_damage_threshold) / BLOCK_SIZE)
        self.health = max(0, self.health - damage)

      self.falling = False
      self.fall_start_y = None

  def mine(self):
    if self.blockFacing:
      if self.blockFacing.amountBroken < self.blockFacing.hardness:
        miningSpeed = 1
        
        if self.heldSlot().item and self.heldSlot().item.isTool():
          #Checks if durability is 0
          if self.heldSlot().item.blockType == self.blockFacing.blockType:
            miningSpeed = self.heldSlot().item.speed
          if self.heldSlot().item.durability == 0:
            self.heldSlot().clear()
            
        self.usingItem = True
        self.blockFacing.amountBroken += miningSpeed / FPS
      else:
        # print("mined", self.blockFacing.name,
        #       "got", self.blockFacing.item().name)
        # world.mask.erase(world[self.blockFacing.y][self.blockFacing.x].mask, self.blockFacing.rect.topleft)
        world[self.blockFacing.y][self.blockFacing.x] = AirBlock(
            self.blockFacing.x, self.blockFacing.y
        )
        if world.back[self.blockFacing.y][self.blockFacing.x].isAir: world.generateLight(self.blockFacing.y, self.blockFacing.x)
        item = self.blockFacing.item()
        
        if self.heldSlot().item and self.heldSlot().item.isTool():
          if self.heldSlot().item.blockType == self.blockFacing.blockType:
            miningSpeed = self.heldSlot().item.speed
            
          self.heldSlot().item.durability -= 1
        
        if item:
          self.inventory.addItem(item())

  def place(self):
    if self.heldSlot().item and self.heldSlot().count > 0 and self.heldSlot().item.isPlaceable():
      x, y = pixelToCoord(*pg.mouse.get_pos())
      if world.blockAt(x, y).isAir:
        self.animations["placingBlock"] = 0
        self.heldSlot().item.place(x, y)
        self.heldSlot().count -= 1
        if self.heldSlot().count == 0:
          self.heldSlot().item = None
        if world.back[y][x].isAir: world.generateLight(y, x)

  def drawCircle(self):
    pg.draw.circle(ASURF, (0, 0, 0, 120), FRAME.center, BLOCK_SIZE * 4)

  def getBlockFacing(self):
    """Returns the block that the player is facing, if it is in range"""
    blockPixel = bresenham(*pg.mouse.get_pos(), *FRAME.center)
    if blockPixel:
      block = world.blockAt(*pixelToCoord(*bresenham(*pg.mouse.get_pos(), *FRAME.center)))
      for vertex in block.vertices:
        if math.dist(relativeCoord(*vertex), FRAME.center) < self.reach:
          return block
    return None

  def drawBlockFacing(self):
    if self.blockFacing:
      self.blockFacing.drawBlockOutline((0, 0, 0, 200))

  def update(self):
    super().update()
    
    self.blockFacing = self.getBlockFacing()
    self.drawBlockFacing()
    self.drawHeldItem()
    self.drawHUD()
    if not pg.mouse.get_pressed()[0]:
      self.usingItem = False
    self.executeHeldSlotEffect()
    self.inventory.menu.getHoveredSlot()
    self.cursorSlot.drawBare(*pg.mouse.get_pos(), self.inventory.menu[0].slotSize)
  
  def drawHUD(self):
    self.draw_health()
    self.drawHotbar()
    self.inventory.draw()