from pygame import Rect, mouse
from typing import Union
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.slot import Slot
from game.model.items.inventory.inventorytype import InventoryType

def getHoveredSlotRect(*inventories: tuple[Union[Inventory, Slot], int, int, int]) -> Rect | None:
    mousepos = mouse.get_pos()

    for inventory_or_slot, slotSize, inventoryx, inventoryy in inventories:
        slotRect = Rect(0, 0, slotSize, slotSize)
        
        # Handle single slot case
        if isinstance(inventory_or_slot, Slot):
            rect = slotRect.copy()
            rect.topleft = (inventoryx, inventoryy)
            if rect.collidepoint(*mousepos):
                return rect
        # Handle inventory case
        else:
            for r in range(inventory_or_slot.rows):
                for c in range(inventory_or_slot.cols):
                    x = inventoryx + c * slotSize
                    y = inventoryy + r * slotSize
                    rect = slotRect.copy()
                    rect.topleft = x, y
                    if rect.collidepoint(*mousepos):
                        return rect
    return None

def getHoveredSlotSlot(inventories: dict[InventoryType, tuple[Union[Inventory, Slot], int, int, int]]) -> tuple[InventoryType, int, int] | None:
    mousepos = mouse.get_pos()

    for name, inventorydata in inventories.items():
        inventory_or_slot, slotSize, inventoryx, inventoryy = inventorydata
        slotRect = Rect(0, 0, slotSize, slotSize)
        
        # Handle single slot case
        if isinstance(inventory_or_slot, Slot):
            rect = slotRect.copy()
            rect.topleft = (inventoryx, inventoryy)
            if rect.collidepoint(*mousepos):
                return name, 0, 0  # For single slots, use (0,0) as position
        # Handle inventory case
        else:
            for r in range(inventory_or_slot.rows):
                for c in range(inventory_or_slot.cols):
                    x = inventoryx + c * slotSize
                    y = inventoryy + r * slotSize
                    rect = slotRect.copy()
                    rect.topleft = x, y
                    if rect.collidepoint(*mousepos):
                        return name, r, c
    return None