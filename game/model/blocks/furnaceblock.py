from typing import Optional
from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.item import Item
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType
from game.model.items.specialitems.fuel import Fuel
from game.model.items.specialitems.smeltable import Smeltable
from game.model.items.utils.itemsenum import Items
from game.model.items.inventory.slot import Slot
from utils.constants import clock


class FurnaceBlock(Block, InventoryBlock):
    '''Furnace block that can smelt items using fuel'''
    def __init__(self):
        self.inputSlot = Inventory(1, 1, condition=lambda other: isinstance(other.item, Smeltable) or other.item is None)           #only smeltable items
        self.fuelSlot = Inventory(1, 1, condition=lambda other: isinstance(other.item, Fuel) or other.item is None)                 #only fuel items
        self.outputSlot = Inventory(1, 1, condition=lambda other: other.item is None)                                               #can't put items in
        
        self._isBurning = False
        self._burnTimeRemaining = 0.0
        self._smeltingProgress = 0.0
        self._smeltingTime = 10.0               # default smelting time in seconds
        
        super().__init__(0.94, 3.5, BlockType.PICKAXE, Blocks.Furnace)
        
    @property
    def inventories(self) -> tuple[Inventory, InventoryType]:
        return (
            (self.inputSlot, InventoryType.FurnaceIn),
            (self.fuelSlot, InventoryType.FuelIn),
            (self.outputSlot, InventoryType.FurnaceOut)
        )
        
    @property
    def isBurning(self) -> bool:
        '''Check if the furnace is currently burning fuel'''
        return self._isBurning
    
    @property
    def smeltingProgress(self) -> float:
        '''Get current smelting progress (0-1)'''
        return self._smeltingProgress
    
    def _canStartSmelting(self) -> bool:
        input_slot = self.inputSlot.array[0][0]
        output_slot = self.outputSlot.array[0][0]
        
        if input_slot.item is None:
            return False
            
        #Check output slot
        if output_slot.item is not None:
            result_item = input_slot.item.resultItem
            if output_slot.item != result_item:
                return False
            if output_slot.count >= result_item.stackSize:
                return False
                
        return True
    
    def _consumeFuel(self) -> bool:
        fuel_slot = self.fuelSlot.array[0][0]
        
        if fuel_slot.item is None:
            return False
            
        self._burnTimeRemaining = fuel_slot.item.burnTime
        
        fuel_slot.count -= 1
        if fuel_slot.count <= 0:
            fuel_slot.clear()
            self._isBurning = False
            
        self._isBurning = True
        return True
    
    def _completeSmelting(self) -> None:
        input_slot = self.inputSlot.array[0][0]
        output_slot = self.outputSlot.array[0][0]
        
        result_item = input_slot.item.resultItem
        
        input_slot.count -= 1
        if input_slot.count <= 0:
            input_slot.clear()
            self._isBurning = False
        
        if output_slot.item is not None:
            output_slot.count += 1
        else:
            output_slot.item = result_item
            output_slot.count = 1
            
        self._smeltingProgress = 0.0
        self._isBurning = False
    
    def update(self) -> None:
        dt = clock.get_time() / 1000.0
        
        if not self._canStartSmelting():
            self._smeltingProgress = 0.0
            self._isBurning = False
            return
            
        if self._burnTimeRemaining <= 0:
            if not self._consumeFuel():
                self._isBurning = False
                return
                
        if self._burnTimeRemaining > 0:
            self._burnTimeRemaining = max(0.0, self._burnTimeRemaining - dt)
            
        if self._isBurning:
            self._smeltingProgress += dt / self._smeltingTime
            
            if self._smeltingProgress >= 1.0:
                self._completeSmelting()