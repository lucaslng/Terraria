from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.item import Item
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType


class FurnaceBlock(Block, InventoryBlock):
    '''
    Furnace block class that handles smelting operations.
    Contains three inventories:
    - Input: For items to be smelted
    - Fuel: For fuel items that power the furnace
    - Output: For the results of smelting
    '''

    def __init__(self):
        # Create 1x1 inventories for input, fuel, and output slots
        self.inputInventory = Inventory(1, 1)
        self.fuelInventory = Inventory(1, 1)
        self.outputInventory = Inventory(1, 1, lambda other: other.item is None)
        
        # Track smelting progress and fuel status
        self.progress = 0.0  # Progress of current smelting operation (0.0 to 1.0)
        self.fuel_remaining = 0.0  # Amount of fuel burn time remaining
        self.smelting_time = 200  # Time needed to smelt one item (in ticks)
        
        # Initialize the block properties
        super().__init__(0.94, 3.0, BlockType.PICKAXE, Blocks.Furnace)
        
        # Track currently processing recipe for proper consumption
        self._current_input = None
        self._current_fuel = None
    
    @property
    def inventories(self) -> tuple[Inventory, InventoryType]:
        '''Return all inventories associated with the furnace'''
        return (
            (self.inputInventory, InventoryType.FurnaceIn),
            (self.fuelInventory, InventoryType.FurnaceFuel),
            (self.outputInventory, InventoryType.FurnaceOut)
        )
    
    def _can_smelt(self) -> tuple[Item, int] | None:
        '''
        Check if the current input can be smelted.
        Returns (result_item, count) if smeltable, None otherwise.
        '''
        input_slot = self.inputInventory[0][0]
        output_slot = self.outputInventory[0][0]
        
        if not input_slot.item:
            return None
            
        # Here you would implement your smelting recipes logic
        # For example:
        # result = smelting_recipes.get(input_slot.item.id)
        # if result:
        #     if not output_slot.item or (
        #         output_slot.item.id == result.id and 
        #         output_slot.count < output_slot.item.stack_size
        #     ):
        #         return result, 1
        
        return None  # Placeholder - implement your smelting logic
    
    def _can_use_fuel(self) -> float | None:
        '''
        Check if the current fuel can be used.
        Returns burn duration in ticks if usable, None otherwise.
        '''
        fuel_slot = self.fuelInventory[0][0]
        
        if not fuel_slot.item:
            return None
            
        # Here you would implement your fuel checking logic
        # For example:
        # return fuel_burn_times.get(fuel_slot.item.id)
        
        return None  # Placeholder - implement your fuel logic
    
    def _consume_fuel(self) -> None:
        '''Consume one fuel item and update fuel remaining'''
        fuel_slot = self.fuelInventory[0][0]
        if fuel_slot.count <= 1:
            fuel_slot.clear()
        else:
            fuel_slot.count -= 1
            
        self._current_fuel = fuel_slot.item
    
    def _consume_input(self) -> None:
        '''Consume one input item after successful smelting'''
        input_slot = self.inputInventory[0][0]
        if input_slot.count <= 1:
            input_slot.clear()
        else:
            input_slot.count -= 1
    
    def update(self) -> None:
        '''
        Update the furnace state:
        - Check if we can start/continue smelting
        - Update fuel and smelting progress
        - Handle completion of smelting operations
        '''
        can_smelt = self._can_smelt()
        
        # Reset progress if we can't smelt current input
        if not can_smelt:
            self.progress = 0.0
            self._current_input = None
            return
            
        # If we have no fuel, try to use new fuel
        if self.fuel_remaining <= 0:
            burn_time = self._can_use_fuel()
            if burn_time:
                self._consume_fuel()
                self.fuel_remaining = burn_time
            else:
                self.progress = 0.0
                return
        
        # Track the current input item
        input_slot = self.inputInventory[0][0]
        if self._current_input != input_slot.item:
            self._current_input = input_slot.item
            self.progress = 0.0
        
        # Update smelting progress
        if self.fuel_remaining > 0:
            self.progress += 1.0 / self.smelting_time
            self.fuel_remaining -= 1
            
            # Complete smelting if we've reached full progress
            if self.progress >= 1.0:
                result_item, count = can_smelt
                output_slot = self.outputInventory[0][0]
                
                if output_slot.item:
                    output_slot.count += count
                else:
                    output_slot.item = result_item
                    output_slot.count = count
                
                self._consume_input()
                self.progress = 0.0