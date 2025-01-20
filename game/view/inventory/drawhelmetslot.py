import pygame as pg
from game.view import surfaces
from game.model.items.inventory.slot import Slot
from game.view.inventory.drawslot import drawSlot

def drawHelmetSlot(slot: Slot, slotSize: int, x: int, y: int) -> None:
    '''Draw a single slot for the helmet armour'''
    
    width = slotSize + 4
    height = slotSize + 4
    
    pg.draw.rect(surfaces.hud, (100, 100, 100, 160), (x - 2, y - 2, width, height))  
    pg.draw.rect(surfaces.hud, (200, 200, 200, 160), (x, y, slotSize, slotSize))
    pg.draw.rect(surfaces.hud, (90, 90, 90), (x, y, slotSize, slotSize), 2)
    
    drawSlot(surfaces.hud, slot, x, y, slotSize)