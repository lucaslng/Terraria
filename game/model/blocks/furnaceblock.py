from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.item import Item
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType
from game.model.items.specialitems.smeltable import Smeltable
from game.model.items.utils.itemsenum import Items
from game.model.items.inventory.slot import Slot


class FurnaceBlock(Block, InventoryBlock):
    '''Furnace block that can smelt items using fuel'''
    def __init__(self):
        self.inputSlot = Slot()
        self.fuelSlot = Slot(condition=lambda other: isinstance(other.item, Smeltable) or other.item is None)
        self.outputSlot = Slot(condition=lambda other: other.item is None)
        
        self.currentBurnTime = 0            # How much burn time is left
        self.currentSmeltTime = 0           # Progress of current smelting operation
        self.maxCurrentBurnTime = 0         # Total burn time of current fuel
        
        super().__init__(0.94, 3.5, BlockType.PICKAXE, Blocks.Furnace)
        
    @property
    def inventories(self) -> tuple[Inventory, InventoryType]:
        '''Provide access to all furnace inventories'''
        return (
            (self.inputSlot, InventoryType.FurnaceIn),
            (self.fuelSlot, InventoryType.FuelIn),
            (self.outputSlot, InventoryType.FurnaceOut)
        )