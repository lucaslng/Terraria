from abc import ABC, abstractmethod
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType

class InventoryBlock(ABC):
    '''Abstract class for a block that has corresponding inventories'''

    @property
    @abstractmethod
    def inventories(self) -> tuple[Inventory, InventoryType]:
        '''The inventories corresponding to this block'''
        pass