from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType
from game.model.items.item import Item


class FurnaceBlock(Block, InventoryBlock):
    '''
    Furnace block that can smelt items using fuel.
    Has three inventory slots:
    - Input slot for items to smelt
    - Fuel slot for burning materials
    - Output slot for smelted items
    '''

    def __init__(self):
        # Create single-slot inventories for input, fuel, and output
        self.inputInventory = Inventory(1, 1)
        self.fuelInventory = Inventory(1, 1)
        self.outputInventory = Inventory(1, 1, lambda other: other.item is None)
        
        # Smelting progress (0.0 to 1.0)
        self.progress = 0.0
        # Remaining fuel burn time in ticks
        self.burnTimeRemaining = 0
        # Total burn time of current fuel item
        self.totalBurnTime = 0
        
        super().__init__(0.94, 3.5, BlockType.PICKAXE, Blocks.Furnace)
    
    @property
    def inventories(self) -> tuple[Inventory, InventoryType]:
        '''Return all inventories this block contains'''
        return (
            (self.inputInventory, InventoryType.FurnaceInput),
            (self.fuelInventory, InventoryType.FurnaceFuel),
            (self.outputInventory, InventoryType.FurnaceOutput)
        )
    
    def _canSmelt(self) -> tuple[Item, int] | None:
        '''
        Check if current input can be smelted.
        Returns tuple of (output_item, count) if possible, None if not
        '''
        input_slot = self.inputInventory[0][0]
        if not input_slot.item:
            return None
            
        # Here you would check against your smelting recipes
        # For example, if input_slot.item is an iron ore, return iron ingot
        # This is a simplified example - you'll need to implement actual recipes
        smelting_result = self._getSmeltingResult(input_slot.item)
        if not smelting_result:
            return None
            
        # Check if output slot can accept the result
        output_slot = self.outputInventory[0][0]
        if output_slot.item and (
            output_slot.item != smelting_result or 
            output_slot.count >= output_slot.item.stackSize
        ):
            return None
            
        return (smelting_result, 1)
    
    def _getSmeltingResult(self, item: Item) -> Item | None:
        '''
        Get the result of smelting an item.
        You'll need to implement your actual smelting recipes here.
        '''
        # Example smelting recipes - replace with your actual items
        smelting_recipes = {
            'IronOre': 'IronIngot',
            'GoldOre': 'GoldIngot',
            'Sand': 'Glass',
            # Add more recipes as needed
        }
        
        if item.name in smelting_recipes:
            # You'll need to implement a way to get Item instances by name
            return self._getItemByName(smelting_recipes[item.name])
        return None
    
    def _getFuelBurnTime(self, item: Item) -> int:
        '''
        Get how many ticks an item can burn for.
        Implement your fuel values here.
        '''
        # Example fuel burn times in ticks
        fuel_times = {
            'Coal': 1600,  # 80 seconds at 20 ticks/sec
            'Wood': 300,   # 15 seconds
            'Stick': 100,  # 5 seconds
            # Add more fuels as needed
        }
        
        return fuel_times.get(item.name, 0)
    
    def _consumeFuel(self) -> bool:
        '''
        Attempt to consume a fuel item.
        Returns True if successful, False if no fuel available.
        '''
        fuel_slot = self.fuelInventory[0][0]
        if not fuel_slot.item:
            return False
            
        burn_time = self._getFuelBurnTime(fuel_slot.item)
        if burn_time <= 0:
            return False
            
        # Consume one fuel item
        if fuel_slot.count <= 1:
            fuel_slot.clear()
        else:
            fuel_slot.count -= 1
            
        self.burnTimeRemaining = burn_time
        self.totalBurnTime = burn_time
        return True
    
    def _smeltItem(self) -> None:
        '''Complete the smelting process for one item'''
        result = self._canSmelt()
        if not result:
            return
            
        output_item, count = result
        input_slot = self.inputInventory[0][0]
        output_slot = self.outputInventory[0][0]
        
        # Consume input
        if input_slot.count <= 1:
            input_slot.clear()
        else:
            input_slot.count -= 1
            
        # Add to output
        if output_slot.item is None:
            output_slot.item = output_item
            output_slot.count = count
        else:
            output_slot.count += count
    
    def update(self) -> None:
        '''
        Update the furnace state:
        - Check if we can smelt
        - Update fuel burning
        - Progress smelting if conditions are met
        '''
        can_smelt = self._canSmelt() is not None
        
        # Handle fuel burning
        if self.burnTimeRemaining > 0:
            self.burnTimeRemaining -= 1
        
        # Try to consume new fuel if needed and we can smelt
        elif can_smelt and self._consumeFuel():
            self.burnTimeRemaining -= 1
        
        # Update smelting progress
        if can_smelt and self.burnTimeRemaining > 0:
            self.progress += 0.05  # Adjust speed as needed
            if self.progress >= 1.0:
                self._smeltItem()
                self.progress = 0.0
        elif not can_smelt:
            self.progress = 0.0