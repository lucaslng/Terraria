from typing import Type, Callable
from dataclasses import dataclass
from functools import partial

from game.model.blocks.furnaceblock import FurnaceBlock
from game.model.items.bucket import Bucket
from game.model.items.helmets import DiamondHelmet, GoldHelmet, IronHelmet
from game.model.items.inventory.slot import Slot
from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items
from game.model.items.tools import (
    DiamondAxe,
    DiamondPickaxe,
    DiamondShovel,
    DiamondSword,
    GoldAxe,
    GoldPickaxe,
    GoldShovel,
    GoldSword,
    IronAxe,
    IronPickaxe,
    IronShovel,
    IronSword,
    StoneAxe,
    StoneShovel,
    StoneSword,
    WoodenAxe,
    WoodenPickaxe,
    StonePickaxe,
    WoodenShovel,
    WoodenSword,
)


def getFilledSlots(slots: list[list[Slot]]) -> tuple[int, Slot | None]:
    filledSlots = 0
    filledSlot = None
    
    for row in slots:
      for slot in row:
        if slot.item:
          filledSlots += 1
          filledSlot = slot
          
    return filledSlots, filledSlot


@dataclass
class Recipe:
    outputMultiplier: int       #how many output items are produced per input item
    craftingFunc: Callable[[list[list[Slot]]], tuple[Item, int] | None]

    def __call__(self, slots: list[list[Slot]]) -> tuple[Item, int] | None:
      return self.craftingFunc(slots)


def pickaxeRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:
    '''Generic function for pickaxes'''
    #Check top row material
    if not all(slots[0][i].item and slots[0][i].item.enum == topMaterial for i in range(3)):
        return None

    #Check for sticks in the middle and bottom center
    if not (
        slots[1][1].item
        and slots[1][1].item.enum == Items.Sticks
        and slots[2][1].item
        and slots[2][1].item.enum == Items.Sticks
    ):
      return None

    #Verify other slots are empty
    if any(slots[r][c].item for r, c in ((1, 0), (1, 2), (2, 0), (2, 2))):
        return None

    return toolClass(), 1

def axeRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:
    #Right-side axe
    rightValid = all(
        slots[r][c].item and slots[r][c].item.enum == topMaterial
        for r, c in ((0, 1), (0, 2), (1, 2))
    ) and all(
        slots[r][1].item and slots[r][1].item.enum == Items.Sticks
        for r in (1, 2)
    ) and not any(
        slots[r][c].item for r, c in ((0, 0), (1, 0), (2, 0), (2, 2))
    )

    #Left-side axe recipe
    leftValid = all(
        slots[r][c].item and slots[r][c].item.enum == topMaterial
        for r, c in ((0, 1), (0, 0), (1, 0))
    ) and all(
        slots[r][1].item and slots[r][1].item.enum == Items.Sticks
        for r in (1, 2)
    ) and not any(
        slots[r][c].item for r, c in ((0, 2), (1, 2), (2, 2), (2, 0))
    )

    if rightValid or leftValid:
        return toolClass(), 1

    return None


def shovelRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:
    if not (slots[0][1].item and slots[0][1].item.enum == topMaterial):
      return None

    if not (
        slots[1][1].item
        and slots[1][1].item.enum == Items.Sticks
        and slots[2][1].item
        and slots[2][1].item.enum == Items.Sticks
    ):
      return None

    if any(slots[r][c].item for r in range(3) for c in range(0, 3, 2)):
      return None

    return toolClass(), 1

def swordRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:
    if not all(slots[r][1].item and slots[r][1].item.enum == topMaterial for r in range(2)):
      return None

    if not (slots[2][1].item and slots[2][1].item.enum == Items.Sticks):
      return None

    if any(slots[r][c].item for r in range(3) for c in range(0, 3, 2)):
      return None

    return toolClass(), 1

def helmetRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:
    if not all(slots[r][c].item and slots[r][c].item.enum == topMaterial for r, c in ((0, 0), (0, 1), (0, 2), (1, 0), (1, 2))):
      return None

    if any(slots[r][c].item for r, c in ((1, 1), (2, 0), (2, 1), (2, 2))):
      return None

    return toolClass(), 1


recipeDictionary = {
  (pickaxeRecipe, Items.Planks): WoodenPickaxe,
  (pickaxeRecipe, Items.Cobblestone): StonePickaxe,
  (pickaxeRecipe, Items.IronIngot): IronPickaxe,
  (pickaxeRecipe, Items.GoldIngot): GoldPickaxe,
  (pickaxeRecipe, Items.Diamond): DiamondPickaxe,
  (axeRecipe, Items.Planks): WoodenAxe,
  (axeRecipe, Items.Cobblestone): StoneAxe,
  (axeRecipe, Items.IronIngot): IronAxe,
  (axeRecipe, Items.GoldIngot): GoldAxe,
  (axeRecipe, Items.Diamond): DiamondAxe,
  (shovelRecipe, Items.Planks): WoodenShovel,
  (shovelRecipe, Items.Cobblestone): StoneShovel,
  (shovelRecipe, Items.IronIngot): IronShovel,
  (shovelRecipe, Items.GoldIngot): GoldShovel,
  (shovelRecipe, Items.Diamond): DiamondShovel,
  (swordRecipe, Items.Planks): WoodenSword,
  (swordRecipe, Items.Cobblestone): StoneSword,
  (swordRecipe, Items.IronIngot): IronSword,
  (swordRecipe, Items.GoldIngot): GoldSword,
  (swordRecipe, Items.Diamond): DiamondSword,
  (helmetRecipe, Items.IronIngot): IronHelmet,
  (helmetRecipe, Items.GoldIngot): GoldHelmet,
  (helmetRecipe, Items.Diamond): DiamondHelmet,
}


def woodenPlanks(slots: list[list[Slot]]) -> tuple[Item, int] | None:
  '''Wooden planks recipe'''
  filledSlots, filledSlot = getFilledSlots(slots)
  if filledSlots == 1 and filledSlot.item.enum == Items.Log:
    from game.model.items.planksitem import PlanksItem
    return PlanksItem(), filledSlot.count * 4


def sticks(slots: list[list[Slot]]) -> tuple[Item, int] | None:
    '''Sticks recipe'''
    filledSlots = 0

    for row in slots:
      for slot in row:
        if slot.item:
          if slot.item.enum != Items.Planks:
            return
          filledSlots += 1

    if filledSlots == 2:
      for r in range(2):
        for c, slot in enumerate(slots[r]):
          slotBelow = slots[r + 1][c]
          if slot.item and slotBelow.item:
            from game.model.items.sticksitem import SticksItem

            return SticksItem(), min(slot.count, slotBelow.count) * 4

def torches(slots: list[list[Slot]]) -> tuple[Item, int] | None:
    filledSlots, _ = getFilledSlots(slots)
    if filledSlots != 2:
      return None
    for r in range(2):
      for c, slot in enumerate(slots[r]):
        slotBelow = slots[r + 1][c]
        if slot.item and slotBelow.item:
          if slot.item.enum == Items.Coal and slotBelow.item.enum == Items.Sticks:
            from game.model.items.torchitem import TorchItem
            return TorchItem(), min(slot.count, slotBelow.count) * 4
        
def furnace(slots: list[list[Slot]]) -> tuple[Item, int] | None:
    if not all(slots[0][i].item and slots[0][i].item.enum == Items.Cobblestone for i in range(3)):
        return None
    if not all(slots[2][i].item and slots[2][i].item.enum == Items.Cobblestone for i in range(3)):
        return None
    
    if not (slots[1][0].item and slots[1][0].item.enum == Items.Cobblestone
            and slots[1][2].item and slots[1][2].item.enum == Items.Cobblestone
            and slots[2][0].item and slots[2][0].item.enum == Items.Cobblestone
            and slots[2][2].item and slots[2][2].item.enum == Items.Cobblestone):
      return None
    
    if slots[1][1].item:
        return None

    return FurnaceBlock(), 1
  
def bucket(slots: list[list[Slot]]) -> tuple[Item, int] | None:
    topPatternIngots = ((0, 0), (0, 2), (1, 1))
    topPatternAir = ((0, 1), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2))
    
    bottomPatternIngots = ((1, 0), (1, 2), (2, 1))
    bottomPatternAir = ((0, 0), (0, 1), (0, 2), (1, 1), (2, 0), (2, 2))
    
    pattern1Valid = (all(slots[r][c].item and slots[r][c].item.enum == Items.IronIngot for r, c in topPatternIngots) and all(not slots[r][c].item for r, c in topPatternAir))
    pattern2Valid = (all(slots[r][c].item and slots[r][c].item.enum == Items.IronIngot for r, c in bottomPatternIngots) and all(not slots[r][c].item for r, c in bottomPatternAir))
    
    if pattern1Valid or pattern2Valid:
        return Bucket(), 1
        
    return None
        

recipes: list[Recipe] = [
    Recipe(4, woodenPlanks),        # 1 log -> 4 planks
    Recipe(4, sticks),              # 2 planks -> 4 sticks
    Recipe(1, furnace),             # 8 cobblestone -> 1 furnace
    Recipe(4, torches),             # 1 coal + 1 stick -> 4 torches
    Recipe(1, bucket),              # 3 iron ingots -> 1 bucket
    *[Recipe(1, partial(recipe, topMaterial=topMaterial, toolClass=recipeDictionary[(recipe, topMaterial)])) for recipe, topMaterial in recipeDictionary],
]
