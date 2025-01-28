from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType


class ChestBlock(Block, InventoryBlock):
    '''Chest block that can store items'''
    def __init__(self):
        self.inventory = Inventory(3, 9)
        
        super().__init__(0.94, 2.5, BlockType.AXE, Blocks.Chest)
        
    @property
    def inventories(self) -> tuple[Inventory, InventoryType]:
        return ((self.inventory, InventoryType.Chest),)