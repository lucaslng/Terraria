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
        self.furnaceInInventory = Inventory(1, 1, condition=lambda other: isinstance(other.item, Smeltable) or other.item is None)           #only smeltable items
        self.fuelInInventory = Inventory(1, 1, condition=lambda other: isinstance(other.item, Fuel) or other.item is None)                 #only fuel items
        self.furnaceOutInventory = Inventory(1, 1, condition=lambda other: other.item is None)                                               #can't put items in
        
        self.isBurning = False
        self._burnTimeRemaining = 0.0
        self._smeltingProgress = 0.0
        self._smeltingTime = 10.0               # default smelting time in seconds
        
        super().__init__(0.94, 3.5, BlockType.PICKAXE, Blocks.Furnace)
        
    @property
    def inventories(self) -> tuple[Inventory, InventoryType]:
        return (
            (self.furnaceInInventory, InventoryType.FurnaceIn),
            (self.fuelInInventory, InventoryType.FuelIn),
            (self.furnaceOutInventory, InventoryType.FurnaceOut)
        )
    
    @property
    def smeltingProgress(self) -> float:
        '''Get current smelting progress (0-1)'''
        return self._smeltingProgress
    
    def _canStartSmelting(self) -> bool:
        inputSlot = self.furnaceInInventory.array[0][0]
        outputSlot = self.furnaceOutInventory.array[0][0]
        
        if inputSlot.item is None:
            return False
            
        #Check output slot
        if outputSlot.item is not None:
            result_item = inputSlot.item.resultItem
            if outputSlot.item != result_item:
                return False
            if outputSlot.count >= result_item.stackSize:
                return False
                
        return True
    
    def _consumeFuel(self) -> bool:
        fuelSlot = self.fuelInInventory.array[0][0]
        
        if fuelSlot.item is None:
            return False
            
        self._burnTimeRemaining = fuelSlot.item.burnTime
        
        fuelSlot.count -= 1
        if fuelSlot.count <= 0:
            fuelSlot.clear()
            self.isBurning = False
            
        self.isBurning = True
        return True
    
    def _completeSmelting(self) -> None:
        input_slot = self.furnaceInInventory.array[0][0]
        output_slot = self.furnaceOutInventory.array[0][0]
        
        result_item = input_slot.item.resultItem
        
        input_slot.count -= 1
        if input_slot.count <= 0:
            input_slot.clear()
            self.isBurning = False
        
        if output_slot.item is not None:
            output_slot.count += 1
        else:
            output_slot.item = result_item
            output_slot.count = 1
            
        self._smeltingProgress = 0.0
    
    def update(self) -> None:
        dt = clock.get_time() / 1000.0
        
        if not self._canStartSmelting():
            self._smeltingProgress = 0.0
            self.isBurning = False
            return
            
        if self._burnTimeRemaining <= 0:
            if not self._consumeFuel():
                self.isBurning = False
                return
                
        if self._burnTimeRemaining > 0:
            self._burnTimeRemaining = max(0.0, self._burnTimeRemaining - dt)
            
        if self.isBurning:
            self._smeltingProgress += dt / self._smeltingTime
            
            if self._smeltingProgress >= 1.0:
                self._completeSmelting()
    
    @property
    def enum(self) -> Blocks:
        if self.isBurning:
            return Blocks.FurnaceBurning
        else:
            return Blocks.Furnace
    
    @enum.setter
    def enum(self, _):
        pass