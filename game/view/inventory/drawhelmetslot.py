import pygame as pg
from game.view import surfaces
from game.model.items.inventory.slot import Slot
from game.view.inventory.drawslot import drawSlot

def drawHelmetSlot(helmet_slot: Slot, slot_size: int, x: int, y: int) -> None:
    '''Draw a single slot for the helmet armour'''
    
    panel_width = slot_size + 4
    panel_height = slot_size + 4
    
    pg.draw.rect(surfaces.hud, (100, 100, 100, 160), (x - 2, y - 2, panel_width, panel_height))  
    pg.draw.rect(surfaces.hud, (200, 200, 200, 160), (x, y, slot_size, slot_size))
    pg.draw.rect(surfaces.hud, (90, 90, 90), (x, y, slot_size, slot_size), 2)
    
    drawSlot(helmet_slot, x, y, slot_size)