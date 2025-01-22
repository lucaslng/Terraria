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
    
    def _calculateConsumtion(self, recipeResult: tuple[Recipe, tuple[Item, int]]) -> dict[tuple[int, int], int]:
        '''Calculate how many items should be consumed from each slot for a successful craft.'''

        recipe, (_, outputCount) = recipeResult
        consumptionMap = {}
        
        craftsPerformed = outputCount // recipe.outputMultiplier
        
        for r, row in enumerate(self.craftingInInventory.array):
            for c, slot in enumerate(row):
                if slot.item:
                    consumptionMap[(r, c)] = craftsPerformed
        
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
        

        self._lastRecipe = None
        self._lastConsumptionMap = None
    
    def update(self) -> None:
        outputSlot = self.craftingOutInventory[0][0]
        
        if self._lastRecipe and outputSlot.item:
            currentResult = self._lastRecipe(self.craftingInInventory.array)
            
            #Clear output if recipe is no longer valid
            if not currentResult:
                outputSlot.clear()
                self._lastRecipe = None
                self._lastConsumptionMap = None
                
        if outputSlot.item is None or outputSlot.count == 0:
            if self._lastRecipe:
                self._consumeMaterials()

            for recipe in recipes:
                result = recipe(self.craftingInInventory.array)
                if result:
                    item, totalCount = result
                    maxStackSize = item.stackSize
                    outputCount = min(totalCount, maxStackSize)     #output at most the stack size
                    
                    outputSlot.item = item
                    outputSlot.count = outputCount
                    
                    remainingCount = totalCount - outputCount
                    if remainingCount > 0:
                        #Store the remaining back into the crafting inventory
                        self._lastRecipe = recipe
                        self._lastConsumptionMap = self._calculateConsumtion((recipe, (item, remainingCount)))
                    else:
                        self._lastRecipe = recipe
                        self._lastConsumptionMap = self._calculateConsumtion((recipe, result))
                    return
