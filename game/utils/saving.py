import os
import time
import pickle
import numpy as np
from dataclasses import dataclass

from game.model.blocks.utils.blocksenum import Blocks
from game.model.items.utils.itemsenum import Items

saveDirectory = 'game/saves'
saveFile      = 'saveFile'
savePath      = os.path.join(saveDirectory, saveFile)


# ─────────────────────────────────────────────────────────────────────────────
#  Compact container – plain Python + numpy only, zero pymunk objects
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class SaveData:
    world_width:        int
    world_height:       int
    world_enums:        np.ndarray   # (H, W) uint8  – front layer
    back_enums:         np.ndarray   # (H, W) uint8  – back layer
    block_states:       dict         # {(x,y): dict} for chests / furnaces / crafting tables
    player_pos:         tuple
    player_health:      float
    player_held_index:  int
    player_inventory:   list         # [(r, c, item_dict, count), ...]
    player_helmet_slot: tuple        # (item_dict | None, count)
    player_cursor_slot: tuple        # (item_dict | None, count)
    entities:           list         # [(class_name, x, y, health), ...]


# ─────────────────────────────────────────────────────────────────────────────
#  Block enum → constructor  (needed for world reconstruction on load)
# ─────────────────────────────────────────────────────────────────────────────
def _buildBlockConstructors() -> dict:
    from game.model.blocks.airblock         import AirBlock
    from game.model.blocks.dirtblock        import DirtBlock
    from game.model.blocks.grassblock       import GrassBlock
    from game.model.blocks.stoneblock       import StoneBlock
    from game.model.blocks.cobblestoneblock import CobblestoneBlock
    from game.model.blocks.oaklogblock      import LogBlock
    from game.model.blocks.planksblock      import PlanksBlock
    from game.model.blocks.leavesblock      import LeavesBlock
    from game.model.blocks.coaloreblock     import CoalOreBlock
    from game.model.blocks.ironoreblock     import IronOreBlock
    from game.model.blocks.goldoreblock     import GoldOreBlock
    from game.model.blocks.diamondoreblock  import DiamondOreBlock
    from game.model.blocks.craftingtableblock import CraftingTableBlock
    from game.model.blocks.torchblock       import TorchBlock
    from game.model.blocks.furnaceblock     import FurnaceBlock
    from game.model.blocks.chestblock       import ChestBlock
    from game.model.blocks.flowerblocks     import PoppyBlock, DandelionBlock, CornflowerBlock, AlliumBlock

    return {
        Blocks.Air:          AirBlock,
        Blocks.Dirt:         DirtBlock,
        Blocks.Grass:        GrassBlock,
        Blocks.Stone:        StoneBlock,
        Blocks.Cobblestone:  CobblestoneBlock,
        Blocks.Log:          LogBlock,
        Blocks.Planks:       PlanksBlock,
        Blocks.Leaves:       LeavesBlock,
        Blocks.CoalOre:      CoalOreBlock,
        Blocks.IronOre:      IronOreBlock,
        Blocks.GoldOre:      GoldOreBlock,
        Blocks.DiamondOre:   DiamondOreBlock,
        Blocks.CraftingTable: CraftingTableBlock,
        Blocks.Torch:        TorchBlock,
        Blocks.Furnace:      FurnaceBlock,
        Blocks.FurnaceBurning: FurnaceBlock,  # reconstructed as Furnace; isBurning is in block_states
        Blocks.Chest:        ChestBlock,
        Blocks.Poppy:        PoppyBlock,
        Blocks.Dandelion:    DandelionBlock,
        Blocks.Cornflower:   CornflowerBlock,
        Blocks.Allium:       AlliumBlock,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Item enum → constructor
# ─────────────────────────────────────────────────────────────────────────────
def _buildItemConstructors() -> dict:
    from game.model.items.dirtitem          import DirtItem
    from game.model.items.grassitem         import GrassItem
    from game.model.items.cobblestoneitem   import CobblestoneItem
    from game.model.items.logitem           import LogItem
    from game.model.items.planksitem        import PlanksItem
    from game.model.items.sticksitem        import SticksItem
    from game.model.items.torchitem         import TorchItem
    from game.model.items.craftingtableitem import CraftingTableItem
    from game.model.items.furnaceitem       import FurnaceItem
    from game.model.items.chestitem         import ChestItem
    from game.model.items.ingots            import CoalItem, IronIngotItem, GoldIngotItem, DiamondItem
    from game.model.items.ores              import IronOreItem, GoldOreItem
    from game.model.items.tools             import (
        WoodenPickaxe, WoodenAxe, WoodenShovel, WoodenSword,
        StonePickaxe,  StoneAxe,  StoneShovel,  StoneSword,
        IronPickaxe,   IronAxe,   IronShovel,   IronSword,
        GoldPickaxe,   GoldAxe,   GoldShovel,   GoldSword,
        DiamondPickaxe, DiamondAxe, DiamondShovel, DiamondSword,
    )
    from game.model.items.helmets           import GoldHelmet, IronHelmet, DiamondHelmet
    from game.model.items.rabbitmeat        import RabbitMeat
    from game.model.items.bucket            import Bucket
    from game.model.items.rpg               import Rpg
    from game.model.items.flowers           import PoppyItem, DandelionItem, CornflowerItem, AlliumItem

    return {
        Items.Dirt:           DirtItem,
        Items.Grass:          GrassItem,
        Items.Stone:          CobblestoneItem,   # mining stone gives cobblestone
        Items.Cobblestone:    CobblestoneItem,
        Items.Log:            LogItem,
        Items.Planks:         PlanksItem,
        Items.Sticks:         SticksItem,
        Items.Torch:          TorchItem,
        Items.CraftingTable:  CraftingTableItem,
        Items.Furnace:        FurnaceItem,
        Items.Chest:          ChestItem,
        Items.Coal:           CoalItem,
        Items.IronOre:        IronOreItem,
        Items.IronIngot:      IronIngotItem,
        Items.GoldOre:        GoldOreItem,
        Items.GoldIngot:      GoldIngotItem,
        Items.Diamond:        DiamondItem,
        Items.WoodenPickaxe:  WoodenPickaxe,
        Items.WoodenAxe:      WoodenAxe,
        Items.WoodenShovel:   WoodenShovel,
        Items.WoodenSword:    WoodenSword,
        Items.StonePickaxe:   StonePickaxe,
        Items.StoneAxe:       StoneAxe,
        Items.StoneShovel:    StoneShovel,
        Items.StoneSword:     StoneSword,
        Items.IronPickaxe:    IronPickaxe,
        Items.IronAxe:        IronAxe,
        Items.IronShovel:     IronShovel,
        Items.IronSword:      IronSword,
        Items.GoldPickaxe:    GoldPickaxe,
        Items.GoldAxe:        GoldAxe,
        Items.GoldShovel:     GoldShovel,
        Items.GoldSword:      GoldSword,
        Items.DiamondPickaxe: DiamondPickaxe,
        Items.DiamondAxe:     DiamondAxe,
        Items.DiamondShovel:  DiamondShovel,
        Items.DiamondSword:   DiamondSword,
        Items.GoldHelmet:     GoldHelmet,
        Items.IronHelmet:     IronHelmet,
        Items.DiamondHelmet:  DiamondHelmet,
        Items.RabbitMeat:     RabbitMeat,
        Items.BucketEmpty:    lambda: Bucket(),
        Items.BucketWater:    lambda: Bucket(),   # liquid/fill restored separately
        Items.Rpg:            Rpg,
        Items.Poppy:          PoppyItem,
        Items.Dandelion:      DandelionItem,
        Items.Cornflower:     CornflowerItem,
        Items.Allium:         AlliumItem,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Item serialization helpers
# ─────────────────────────────────────────────────────────────────────────────
def _serializeItem(item) -> dict | None:
    if item is None:
        return None

    from game.model.items.specialitems.tool   import Tool
    from game.model.items.specialitems.helmet import Helmet
    from game.model.items.bucket              import Bucket
    from game.model.items.rpg                 import Rpg

    d: dict = {'e': item.enum.name}

    if isinstance(item, (Tool, Helmet)):
        d['dur'] = item.durability
    if isinstance(item, Bucket):
        d['liq']  = item.liquid.__name__ if item.liquid else None
        d['fill'] = item.filledAmount
    if isinstance(item, Rpg):
        d['ammo'] = item.ammo

    return d


def _deserializeItem(d: dict | None):
    if d is None:
        return None

    from game.model.items.specialitems.tool   import Tool
    from game.model.items.specialitems.helmet import Helmet
    from game.model.items.bucket              import Bucket
    from game.model.items.rpg                 import Rpg
    from game.model.liquids.liquid            import Water

    constructors = _buildItemConstructors()
    enum   = Items[d['e']]
    item   = constructors[enum]()

    if isinstance(item, (Tool, Helmet)) and 'dur' in d:
        item.durability = d['dur']
    if isinstance(item, Bucket):
        liquid_map = {'Water': Water, None: None}
        item.liquid      = liquid_map.get(d.get('liq'))
        item.filledAmount = d.get('fill', 0)
    if isinstance(item, Rpg) and 'ammo' in d:
        item.ammo = d['ammo']

    return item


# ─────────────────────────────────────────────────────────────────────────────
#  Inventory serialization helpers
# ─────────────────────────────────────────────────────────────────────────────
def _serializeInventory(inventory) -> list:
    '''Sparse: only non-empty slots are stored.'''
    out = []
    for r, row in enumerate(inventory.array):
        for c, slot in enumerate(row):
            if slot.item is not None:
                out.append((r, c, _serializeItem(slot.item), slot.count))
    return out


def _deserializeInventory(inventory, data: list) -> None:
    for r, c, item_dict, count in data:
        inventory.array[r][c].item  = _deserializeItem(item_dict)
        inventory.array[r][c].count = count


def _serializeSlot(slot) -> tuple:
    return (_serializeItem(slot.item), slot.count)


def _deserializeSlot(slot, data: tuple) -> None:
    item_dict, count = data
    slot.item  = _deserializeItem(item_dict)
    slot.count = count


# ─────────────────────────────────────────────────────────────────────────────
#  Block state serialization  (InventoryBlocks only)
# ─────────────────────────────────────────────────────────────────────────────
def _serializeBlockState(block) -> dict | None:
    from game.model.blocks.chestblock         import ChestBlock
    from game.model.blocks.furnaceblock       import FurnaceBlock
    from game.model.blocks.craftingtableblock import CraftingTableBlock

    if isinstance(block, ChestBlock):
        return {'type': 'chest', 'inv': _serializeInventory(block.inventory)}

    if isinstance(block, FurnaceBlock):
        return {
            'type':     'furnace',
            'in':       _serializeInventory(block.furnaceInInventory),
            'fuel':     _serializeInventory(block.fuelInInventory),
            'out':      _serializeInventory(block.furnaceOutInventory),
            'burning':  block.isBurning,
            'burnLeft': block.burnTimeRemaining,
            'progress': block.smeltingProgress,
        }

    if isinstance(block, CraftingTableBlock):
        return {
            'type': 'crafting',
            'in':   _serializeInventory(block.craftingInInventory),
            'out':  _serializeInventory(block.craftingOutInventory),
        }

    return None


def _restoreBlockState(block, state: dict) -> None:
    from game.model.blocks.chestblock         import ChestBlock
    from game.model.blocks.furnaceblock       import FurnaceBlock
    from game.model.blocks.craftingtableblock import CraftingTableBlock

    t = state['type']
    if t == 'chest':
        _deserializeInventory(block.inventory, state['inv'])
    elif t == 'furnace':
        _deserializeInventory(block.furnaceInInventory, state['in'])
        _deserializeInventory(block.fuelInInventory,    state['fuel'])
        _deserializeInventory(block.furnaceOutInventory, state['out'])
        block.isBurning         = state['burning']
        block.burnTimeRemaining = state['burnLeft']
        block.smeltingProgress  = state['progress']
    elif t == 'crafting':
        _deserializeInventory(block.craftingInInventory, state['in'])
        _deserializeInventory(block.craftingOutInventory, state['out'])


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────
def _ensureSaveDirectory() -> None:
    os.makedirs(saveDirectory, exist_ok=True)


def clear() -> None:
    try:
        os.remove(savePath)
        print("Clearing save...")
    except FileNotFoundError:
        pass


def save(model) -> None:
    print("\nSaving...")
    print(f"{'Task':<22} | Time (seconds)")
    print("-" * 40)
    total_start = time.perf_counter()

    # ── World block enums ────────────────────────────────────────────────────
    t = time.perf_counter()
    H, W = model.world.height, model.world.width
    # << CHANGED: read directly from the pre-built enum arrays — no Python loop
    world_enums = model.world.enums.copy()
    back_enums  = model.world.back_enums.copy()
    print(f"{'World arrays':<22} | {time.perf_counter() - t:.4f}s")

    # ── Block inventory states ───────────────────────────────────────────────
    t = time.perf_counter()
    from game.model.blocks.utils.inventoryblock import InventoryBlock
    block_states = {}
    for y in range(H):
        for x in range(W):
            if isinstance(model.world[y][x], InventoryBlock):
                state = _serializeBlockState(model.world[y][x])
                if state:
                    block_states[(x, y)] = state
    print(f"{'Block states':<22} | {time.perf_counter() - t:.4f}s")

    # ── Player ───────────────────────────────────────────────────────────────
    t = time.perf_counter()
    p = model.player
    player_inventory = _serializeInventory(p.inventory)
    player_helmet    = _serializeSlot(p.helmetSlot)
    player_cursor    = _serializeSlot(p.cursorSlot)
    print(f"{'Player':<22} | {time.perf_counter() - t:.4f}s")

    # ── Entities ─────────────────────────────────────────────────────────────
    t = time.perf_counter()
    from game.model.entity.entity import Entity
    entities = []
    for e in model.entities:
        if isinstance(e, Entity):
            entities.append((
                type(e).__name__,
                float(e.body.position.x),
                float(e.body.position.y),
                e.health,
            ))
    print(f"{'Entities':<22} | {time.perf_counter() - t:.4f}s")

    # ── Pickle & write ───────────────────────────────────────────────────────
    t = time.perf_counter()
    _ensureSaveDirectory()
    data = SaveData(
        world_width        = W,
        world_height       = H,
        world_enums        = world_enums,
        back_enums         = back_enums,
        block_states       = block_states,
        player_pos         = (float(p.body.position.x), float(p.body.position.y)),
        player_health      = p.health,
        player_held_index  = p.heldSlotIndex,
        player_inventory   = player_inventory,
        player_helmet_slot = player_helmet,
        player_cursor_slot = player_cursor,
        entities           = entities,
    )
    with open(savePath, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"{'Pickle & write':<22} | {time.perf_counter() - t:.4f}s")

    print("-" * 40)
    print(f"{'Total save':<22} | {time.perf_counter() - total_start:.4f}s\n")


def load():
    print("\nLoading save...")
    print(f"{'Task':<22} | Time (seconds)")
    print("-" * 40)
    total_start = time.perf_counter()

    # ── Read & unpickle ──────────────────────────────────────────────────────
    t = time.perf_counter()
    try:
        with open(savePath, 'rb') as f:
            data = pickle.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        # Likely an old dill-format save - wipe it and start fresh
        print("Save file is incompatible (old format), clearing...")
        clear()
        return None

    if not isinstance(data, SaveData):
        print("Save file is incompatible (old format), clearing...")
        clear()
        return None

    print(f"{'Read & unpickle':<22} | {time.perf_counter() - t:.4f}s")

    # ── Create model skeleton (no world generation) ──────────────────────────
    t = time.perf_counter()
    from game.model.model import Model
    model = Model(data.world_width, data.world_height, _from_save=True)
    print(f"{'Model skeleton':<22} | {time.perf_counter() - t:.4f}s")

    # ── Restore world blocks ─────────────────────────────────────────────────
    t = time.perf_counter()
    constructors = _buildBlockConstructors()
    for y in range(data.world_height):
        for x in range(data.world_width):
            front_enum = Blocks(int(data.world_enums[y, x]))
            back_enum  = Blocks(int(data.back_enums[y, x]))
            model.world[y][x]      = constructors[front_enum]()
            model.world.back[y][x] = constructors[back_enum]()
    # << CHANGED: copy saved enum arrays directly into world — no recomputation
    model.world.enums      = data.world_enums.copy()
    model.world.back_enums = data.back_enums.copy()
    print(f"{'World blocks':<22} | {time.perf_counter() - t:.4f}s")

    # ── Restore block inventory states ───────────────────────────────────────
    t = time.perf_counter()
    for (x, y), state in data.block_states.items():
        _restoreBlockState(model.world[y][x], state)
    print(f"{'Block states':<22} | {time.perf_counter() - t:.4f}s")

    # ── Rebuild physics shapes ───────────────────────────────────────────────
    t = time.perf_counter()
    model._generateWorldShapes()
    print(f"{'World shapes':<22} | {time.perf_counter() - t:.4f}s")

    # ── Rebuild lightmap ─────────────────────────────────────────────────────
    t = time.perf_counter()
    model.generateLight()
    print(f"{'Lightmap':<22} | {time.perf_counter() - t:.4f}s")

    # ── Restore player ───────────────────────────────────────────────────────
    t = time.perf_counter()
    p = model.player
    p.body.position  = data.player_pos
    p.health         = data.player_health
    p.heldSlotIndex  = data.player_held_index
    _deserializeInventory(p.inventory,  data.player_inventory)
    _deserializeSlot(p.helmetSlot, data.player_helmet_slot)
    _deserializeSlot(p.cursorSlot, data.player_cursor_slot)
    print(f"{'Player':<22} | {time.perf_counter() - t:.4f}s")

    # ── Restore entities ─────────────────────────────────────────────────────
    t = time.perf_counter()
    from game.model.entity.entities.npc    import Npc
    from game.model.entity.entities.rabbit import Rabbit
    from game.model.entity.entities.dog    import Dog
    entity_map = {'Npc': Npc, 'Rabbit': Rabbit, 'Dog': Dog}
    for class_name, x, y, health in data.entities:
        cls = entity_map.get(class_name)
        if cls:
            model.spawnEntity(cls, x, y)
            model.entities[-1].health = health
    print(f"{'Entities':<22} | {time.perf_counter() - t:.4f}s")

    # ── Rebuild torch light list ─────────────────────────────────────────────
    t = time.perf_counter()
    from game.model.light import Light
    for y in range(data.world_height):
        for x in range(data.world_width):
            if isinstance(model.world[y][x], Light):
                model.lights.append((model.world[y][x], x, y))
    print(f"{'Lights list':<22} | {time.perf_counter() - t:.4f}s")

    print("-" * 40)
    print(f"{'Total load':<22} | {time.perf_counter() - total_start:.4f}s\n")
    return model