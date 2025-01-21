from typing import Type, Callable
from dataclasses import dataclass
from functools import partial

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
  outputMultiplier: int  # how many output items are produced per input item
  craftingFunc: Callable[[list[list[Slot]]], tuple[Item, int] | None]

  def __call__(self, slots: list[list[Slot]]) -> tuple[Item, int] | None:
    return self.craftingFunc(slots)


def woodenPlanks(slots: list[list[Slot]]) -> tuple[Item, int] | None:
  """Wooden planks recipe"""
  filledSlots, filledSlot = getFilledSlots(slots)
  if filledSlots == 1 and filledSlot.item.enum == Items.Log:
    from game.model.items.planksitem import PlanksItem
    return PlanksItem(), filledSlot.count * 4


def sticks(slots: list[list[Slot]]) -> tuple[Item, int] | None:
  """Sticks recipe"""
  filledSlots = 0

  for row in slots:
    for slot in row:
      if slot.item:
        if slot.item.enum != Items.Planks:
          return None
        filledSlots += 1

  if filledSlots == 2:
    for r in range(2):
      for c, slot in enumerate(slots[r]):
        slotBelow = slots[r + 1][c]
        if slot.item and slotBelow.item:
          from game.model.items.sticksitem import SticksItem

          return SticksItem(), min(slot.count, slotBelow.count) * 4


def pickaxeRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:
  """
  Generic recipe function for pickaxes

  items: The crafting grid slots
  topMaterial: The Items enum value for the required top row material
  toolClass: The class of the tool to create (WoodenPickaxe, StonePickaxe, etc.)

  Returns: A tuple of (created item, count) or None if recipe doesn't match
  """

  # Check top row material
  if not all(slots[0][i].item and slots[0][i].item.enum == topMaterial for i in range(3)):
    return None

  # Check for sticks in the middle and bottom center
  if not (
      slots[1][1].item
      and slots[1][1].item.enum == Items.Sticks
      and slots[2][1].item
      and slots[2][1].item.enum == Items.Sticks
  ):
    return None

  # Verify other slots are empty
  if any(slots[r][c].item for r, c in [(1, 0), (1, 2), (2, 0), (2, 2)]):
    return None

  return toolClass(), 1


def axeRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:

  # Check top row material
  if not all(slots[r][c].item and slots[r][c].item.enum == topMaterial for r, c in [(0, 1), (0, 2), (1, 2)]):
    return None

  # Check for sticks in the middle and bottom center
  if not (
      slots[1][1].item
      and slots[1][1].item.enum == Items.Sticks
      and slots[2][1].item
      and slots[2][1].item.enum == Items.Sticks
  ):
    return None

  # Verify other slots are empty
  if any(slots[r][c].item for r, c in [(0, 0), (1, 0), (2, 0), (2, 2)]):
    return None

  return toolClass(), 1

def shovelRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:

  # Check top row material
  if not (slots[0][1].item and slots[0][1].item.enum == topMaterial):
    return None

  # Check for sticks in the middle and bottom center
  if not (
      slots[1][1].item
      and slots[1][1].item.enum == Items.Sticks
      and slots[2][1].item
      and slots[2][1].item.enum == Items.Sticks
  ):
    return None

  # Verify other slots are empty
  if any(slots[r][c].item for r in range(3) for c in range(0, 3, 2)):
    return None

  return toolClass(), 1

def swordRecipe(slots: list[list[Slot]], topMaterial: Items, toolClass: Type[Item]) -> tuple[Item, int] | None:

  # Check top row material
  if not all(slots[r][1].item and slots[r][1].item.enum == topMaterial for r in range(2)):
    return None

  # Check for sticks in the bottom center
  if not (slots[2][1].item and slots[2][1].item.enum == Items.Sticks):
    return None

  # Verify other slots are empty
  if any(slots[r][c].item for r in range(3) for c in range(0, 3, 2)):
    return None

  return toolClass(), 1


toolClasses = {
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
}


recipes: list[Recipe] = [
    Recipe(4, woodenPlanks),  # 1 log -> 4 planks
    Recipe(4, sticks),  # 2 planks -> 4 sticks
    *[Recipe(1, partial(toolRecipe, topMaterial=topMaterial, toolClass=toolClasses[(toolRecipe, topMaterial)])) for toolRecipe, topMaterial in toolClasses],
]
