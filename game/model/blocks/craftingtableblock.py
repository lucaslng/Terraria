from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.recipes.recipes import recipes, Recipe
from game.model.items.item import Item
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType


class CraftingTableBlock(Block, InventoryBlock):
    '''Crafting table block class with material consumption'''

    def __init__(self):
        self.craftingInInventory = Inventory(3, 3)
        self.craftingOutInventory = Inventory(1, 1, lambda other: other.item is None)
        self._last_recipe = None
        self._last_consumption_map = None
        super().__init__(0.94, 2.5, BlockType.AXE, Blocks.CraftingTable)
    
    @property
    def inventories(self) -> tuple[Inventory, InventoryType]:
        return (self.craftingInInventory, InventoryType.CraftingIn), (self.craftingOutInventory, InventoryType.CraftingOut)
    
    def _calculateConsumtion(self, recipe_result: tuple[Recipe, tuple[Item, int]]) -> dict[tuple[int, int], int]:
        '''Calculate how many items should be consumed from each slot for a successful craft.'''
        
        recipe, (_, output_count) = recipe_result
        consumption_map = {}
        
        # Calculate how many items we need to consume based on output quantity
        crafts_performed = output_count // recipe.output_multiplier
        
        for row_idx, row in enumerate(self.craftingInInventory.array):
            for col_idx, slot in enumerate(row):
                if slot.item:
                    consumption_map[(row_idx, col_idx)] = crafts_performed
        
        return consumption_map

    def _consumeMaterials(self) -> None:
        """
        Consume materials from the input inventory based on the last successful recipe.
        Only called when items are removed from the output slot.
        """
        if not self._last_consumption_map:
            return
            
        for (row, col), amount in self._last_consumption_map.items():
            slot = self.craftingInInventory[row][col]
            if slot.count <= amount:
                slot.clear()
            else:
                slot.count -= amount
        
        #reset the variables
        self._last_recipe = None
        self._last_consumption_map = None
    
    def update(self) -> None:
        output_slot = self.craftingOutInventory[0][0]
        
        # First, check if we had a previous recipe and the ingredients are still valid
        if self._last_recipe and output_slot.item:
            current_result = self._last_recipe(self.craftingInInventory.array)
            
            # If the recipe is no longer valid, clear the output
            if not current_result:
                output_slot.clear()
                self._last_recipe = None
                self._last_consumption_map = None
                
        # If output slot is empty, check for new recipe
        if output_slot.item is None:
            # Consume materials if we had a previous recipe
            if self._last_recipe:
                self._consumeMaterials()
            
            # Check for new recipe
            for recipe in recipes:
                result = recipe(self.craftingInInventory.array)
                if result:
                    item, count = result
                    output_slot.item = item
                    output_slot.count = count
                    self._last_recipe = recipe
                    self._last_consumption_map = self._calculateConsumtion((recipe, result))
                    return