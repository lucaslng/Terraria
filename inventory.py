import pygame as pg
from dataclasses import dataclass

from items import *
from constants import font20, SURF, OVERLAY, BIG
from entities import Player


player = Player()


class Interactable(ABC):
  '''Abstract class for something that can be interacted with (press e key when near)'''

  def interact(self):
    '''To be called when Interactable is interacted with.'''
    pass


class Slot:
  """Slot class"""
  item: Item | None = None
  count: int = 0
  isActive = False
  size = 40
  
  def clear(self):
    '''reset/clear the slot'''
    self.item = None
    self.count = 0

  def draw(self, x: float, y: float, size: float = size, transparent=False) -> None:
    if not transparent:
      pg.draw.rect(OVERLAY, (200, 200, 200), (x, y, size, size))
    else:
      pg.draw.rect(OVERLAY, (200, 200, 200, 160), (x, y, size, size))
      
    if self.isActive:
      pg.draw.rect(OVERLAY, (0, 0, 0), (x, y, size, size), 2)
    else:
      pg.draw.rect(OVERLAY, (90, 90, 90), (x, y, size, size), 2)

    if self.item:
      texture = pg.transform.scale(self.item.texture, (size - 6, size - 6))
      
      #center texture in the slot
      textureRect = texture.get_rect()
      textureRect.center = (x + size / 2, y + size / 2)
      OVERLAY.blit(texture, textureRect.topleft)

      if self.count > 1:
        count_text = font20.render(str(self.count), True, (255, 255, 255))
        
        #item counter in the bottom right of the slot
        text_rect = count_text.get_rect(topleft=textureRect.center)
        OVERLAY.blit(count_text, text_rect.topleft)
        
      #Draw durability bar
      if self.item.isTool() and self.item.durability != self.item.startingDurability:
        barHeight = 3
        barWidth = size - 4
        barx = x + 2
        bary = y + size - barHeight - 1
        
        tool: Tool = self.item
        durabilityPercent = tool.durability / tool.startingDurability
        
        if durabilityPercent > 0.6:
          colour = (0, 255, 0)
        elif durabilityPercent > 0.3:
          colour = (255, 165, 0)
        else:
          colour = (255, 0, 0)
        
        pg.draw.rect(OVERLAY, (50, 50, 50), (barx, bary, barWidth, barHeight))
        pg.draw.rect(OVERLAY, colour, (barx, bary, int(barWidth * durabilityPercent), barHeight))

  def drawBare(self, x: float, y: float, size: float = size):
    '''draw without the box around it, just the item and the number, location is the center instead of topleft'''
    if self.item:
      texture = pg.transform.scale(self.item.texture, (size - 6, size - 6))
    
      #center texture in the slot
      textureRect = texture.get_rect()
      textureRect.center = x, y
      OVERLAY.blit(texture, textureRect.topleft)

      if self.count > 1:
        count_text = font20.render(str(self.count), True, (255, 255, 255))
        
        #item counter in the bottom right of the slot
        text_rect = count_text.get_rect(topleft=textureRect.center)
        OVERLAY.blit(count_text, text_rect.topleft)       
        
        
@dataclass
class Section:
  rows: int
  cols: int
  x: float
  y: float
  slotSize: int = 40
  
  def __post_init__(self):
    self.array = [[Slot() for _ in range(self.cols)] for _ in range(self.rows)]
    self.rect = pg.Rect(self.x, self.y, self.x + self.cols * self.slotSize, self.y + self.rows * self.slotSize)
    
  def __getitem__(self, i: int) -> list[Slot]:
    return self.array[i]
  
  def isHovered(self) -> bool:
    return self.rect.collidepoint(*pg.mouse.get_pos())
  
  def hoveredSlot(self):
    '''returns the location of the slot that is hovered in a tuple (r, c)'''
    for r in range(self.rows):
      for c in range(self.cols):
        slotRect = pg.Rect(self.x + c * self.slotSize, self.y + r * self.slotSize, self.slotSize, self.slotSize)
        if slotRect.collidepoint(*pg.mouse.get_pos()):
          pg.draw.rect(SURF, (0,0,0), slotRect, 4)
          return r, c
    return None
  
  def draw(self, transparent=False) -> None:
    for r in range(self.rows):
      for c in range(self.cols):
        self[r][c].draw(self.x+c*self.slotSize, self.y+r*self.slotSize, size = self.slotSize, transparent=transparent)
        
class Menu:
  '''A menu is effectively a list of Sections. One section is an array of Slots.'''
  def __init__(self, *args: Section, isActive: bool = False):
    self.isActive = isActive
    self.sections = [args[i] for i in range(len(args))]
    minx = miny = BIG
    maxx = maxy = 0
    for section in self.sections:
      minx = min(minx, section.x)
      miny = min(miny, section.y)
      maxx = max(maxx, section.x + section.cols * section.slotSize)
      maxy = max(maxy, section.y + section.rows * section.slotSize)
    self.rect = pg.Rect(minx, miny, maxx - minx, maxy - miny)
    self.hoveredSlot: None | tuple[int, tuple[int, int] | None] = None
  
  def draw(self, transparent=False) -> None:
    for section in self.sections:
      section.draw(transparent=transparent)
  
  def isHovered(self) -> bool:
    return self.rect.collidepoint(*pg.mouse.get_pos())
  
  def getHoveredSlot(self):
    '''
    returns the location of the hovered slot in a tuple \n
    the 0th index is the section index within the menu \n
    the 1st index is the location of the slot in the section in a tuple (r, c)
    '''
    
    if self.isHovered():
      for i in range(len(self.sections)):
        section = self.sections[i]
        if section.isHovered():
          self.hoveredSlot = i, section.hoveredSlot()
          return
    self.hoveredSlot = None
  
  def pickUpItem(self):
    if self.hoveredSlot:
      sectionid, location = self.hoveredSlot
      r, c = location
      player.cursorSlot, self.sections[sectionid][r][c] = self.sections[sectionid][r][c], player.cursorSlot
  
  def __getitem__(self, i: int):
    return self.sections[i]
  
  def __len__(self):
    return len(self.sections)     

@dataclass
class Inventory:
  """Inventory class"""
  rows: int
  cols: int
  menux: int
  menuy: int
  
  def __post_init__(self):
    self.menu = Menu(Section(self.rows, self.cols, self.menux, self.menuy))

  def addItem(self, item: Item) -> bool:
    """Attempts to add an item to the inventory"""
    #add item to stack with existing items
    for r in range(self.rows):
        for c in range(self.cols):
            slot = self.menu[0][r][c]
            if slot.item and slot.item == item and slot.count < slot.item.stackSize:
                slot.count += 1
                self.menu.draw()
                return True
                
    #find first empty slot if there isn't an existing slot
    for r in range(self.rows):
        for c in range(self.cols):
            slot = self.menu[0][r][c]
            if slot.item is None:
                slot.item = item
                slot.count = 1
                #print('added to inventory')
                self.menu.draw()
                return True
                
    return False  #inventory full

  def isPlaceable(self) -> bool:
    return isinstance(self, PlaceableItem)
  
  def draw(self, transparent=True): # notice that default is True here for transparency
    self.menu.draw(transparent=transparent)

  def __getitem__(self, row: int):
    return self.menu[0][row]


class HasInventory:
  """Parent class for classes than have an inventory"""

  def __init__(self, rows: int, cols: int, menux: int, menuy: int):
    self.inventory = Inventory(rows=rows, cols=cols, menux=menux, menuy=menuy)