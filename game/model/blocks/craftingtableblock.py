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
        self._lastRecipe = None
        self._lastConsumptionMap = None
        super().__init__(0.94, 2.5, BlockType.AXE, Blocks.CraftingTable)
    
    @property
    def inventories(self) -> tuple[Inventory, InventoryType]:
        return (self.craftingInInventory, InventoryType.CraftingIn), (self.craftingOutInventory, InventoryType.CraftingOut)
    
    def _calculateConsumtion(self, recipe_result: tuple[Recipe, tuple[Item, int]]) -> dict[tuple[int, int], int]:
        '''Calculate how many items should be consumed from each slot for a successful craft.'''

        recipe, (_, outputCount) = recipe_result
        consumptionMap = {}
        
        # Calculate how many items we need to consume based on output quantity
        craftsPerformed = outputCount // recipe.outputMultiplier
        
        for row_idx, row in enumerate(self.craftingInInventory.array):
            for col_idx, slot in enumerate(row):
                if slot.item:
                    consumptionMap[(row_idx, col_idx)] = craftsPerformed
        
        return consumptionMap

    def _consumeMaterials(self) -> None:    
        if not self._lastConsumptionMap:
            return
            
        for (row, col), amount in self._lastConsumptionMap.items():
            slot = self.craftingInInventory[row][col]
            if slot.count <= amount:
                slot.clear()
            else:
                slot.count -= amount
        
        #reset the variables
        self._lastRecipe = None
        self._lastConsumptionMap = None
    
    def update(self) -> None:
        outputSlot = self.craftingOutInventory[0][0]
        
        # First, check if we had a previous recipe and the ingredients are still valid
        if self._lastRecipe and outputSlot.item:
            current_result = self._lastRecipe(self.craftingInInventory.array)
            
            # If the recipe is no longer valid, clear the output
            if not current_result:
                outputSlot.clear()
                self._lastRecipe = None
                self._lastConsumptionMap = None
                
        # If output slot is empty, check for new recipe
        if outputSlot.item is None:
            # Consume materials if we had a previous recipe
            if self._lastRecipe:
                self._consumeMaterials()
            
            # Check for new recipe
            for recipe in recipes:
                result = recipe(self.craftingInInventory.array)
                if result:
                    item, count = result
                    outputSlot.item = item
                    outputSlot.count = count
                    self._lastRecipe = recipe
                    self._lastConsumptionMap = self._calculateConsumtion((recipe, result))
                    return