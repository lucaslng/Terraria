from typing import Type, Callable
from dataclasses import dataclass
from functools import partial

from game.model.items.inventory.slot import Slot
from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items
from game.model.items.tools import WoodenPickaxe, StonePickaxe


@dataclass
class Recipe:
    outputMultiplier: int			#how many output items are produced per input item
    crafting_func: Callable[[list[list[Slot]]], tuple[Item, int] | None]
    
    def __call__(self, items: list[list[Slot]]) -> tuple[Item, int] | None:
        return self.crafting_func(items)


def woodenPlanks(items: list[list[Slot]]) -> tuple[Item, int] | None:
    '''Wooden planks recipe'''
    filledSlots = 0
    
    for row in items:
        for slot in row:
            if slot.item:
                filledSlots += 1
                filledSlot = slot

    if filledSlots == 1 and filledSlot.item.enum == Items.Log:
        from game.model.items.planksitem import PlanksItem
        return PlanksItem(), filledSlot.count * 4


def sticks(items: list[list[Slot]]) -> tuple[Item, int] | None:
    '''Sticks recipe'''
    filledSlots = 0
    
    for row in items:
        for slot in row:
            if slot.item:
                if slot.item.enum != Items.Planks:
                    return None
                filledSlots += 1
    
    if filledSlots == 2:
        for r in range(2):
            for c, slot in enumerate(items[r]):
                slotBelow = items[r + 1][c]
                if slot.item and slotBelow.item:
                    from game.model.items.sticksitem import SticksItem
                    return SticksItem(), min(slot.count, slotBelow.count) * 4


def createPickaxeRecipe(items: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:
    """
    Generic recipe function for pickaxes
    
    items: The crafting grid slots
    top_material: The Items enum value for the required top row material
    tool_class: The class of the tool to create (WoodenPickaxe, StonePickaxe, etc.)
    
    Returns: A tuple of (created item, count) or None if recipe doesn't match
    """
    
    #Check top row material
    if not all(items[0][i].item and items[0][i].item.enum == topMaterial for i in range(3)):
        return None

    #Check for sticks in the middle and bottom center
    if not (items[1][1].item and items[1][1].item.enum == Items.Sticks and
            items[2][1].item and items[2][1].item.enum == Items.Sticks):
        return None

    #Verify other slots are empty
    if any(items[r][c].item for r, c in [(1,0), (1,2), (2,0), (2,2)]):
        return None

    return toolClass(), 1


woodenPickaxe = partial(
    createPickaxeRecipe,
    top_material=Items.Planks,
    tool_class=WoodenPickaxe
)

stonePickaxe = partial(
    createPickaxeRecipe,
    top_material=Items.Cobblestone,
    tool_class=StonePickaxe
)



recipes: list[Recipe] = [
    Recipe(4, woodenPlanks),  # 1 log -> 4 planks
    Recipe(4, sticks),        # 2 planks -> 4 sticks
    Recipe(1, woodenPickaxe),
    Recipe(1, stonePickaxe),
]