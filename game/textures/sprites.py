from pygame import SRCALPHA, Surface
from utils.constants import BLOCK_SIZE
from game.model.blocks.utils.blocksenum import Blocks
from game.model.items.utils.itemsenum import Items
from game.textures.animation import Animation
from game.textures.spritesheets import catSheet, rabbitsSheet, everythingSheet, weirdBlocksSheet, dogSheet

sprites: dict[str | Blocks | Items, dict[str, Animation] | Surface] = {
    "cat": {
        "walk": Animation(
        catSheet.get(9, 144, 16, 16, BLOCK_SIZE),
        catSheet.get(40, 144, 16, 16, BLOCK_SIZE),
        catSheet.get(71, 144, 16, 16, BLOCK_SIZE),
        catSheet.get(103, 144, 16, 16, BLOCK_SIZE),
        catSheet.get(135, 144, 16, 16, BLOCK_SIZE),
        catSheet.get(167, 144, 16, 16, BLOCK_SIZE),
        catSheet.get(200, 144, 16, 16, BLOCK_SIZE),
        catSheet.get(232, 144, 16, 16, BLOCK_SIZE),
        ),
        "run": Animation(
        catSheet.get(9, 176, 16, 16, BLOCK_SIZE),
        catSheet.get(40, 176, 16, 16, BLOCK_SIZE),
        catSheet.get(71, 176, 16, 16, BLOCK_SIZE),
        catSheet.get(103, 176, 16, 16, BLOCK_SIZE),
        catSheet.get(135, 176, 16, 16, BLOCK_SIZE),
        catSheet.get(167, 176, 16, 16, BLOCK_SIZE),
        catSheet.get(200, 176, 16, 16, BLOCK_SIZE),
        catSheet.get(232, 176, 16, 16, BLOCK_SIZE),
        ),
        "jump": Animation(
        catSheet.get(9, 272, 16, 16, BLOCK_SIZE),
        catSheet.get(40, 272, 16, 16, BLOCK_SIZE),
        catSheet.get(71, 272, 16, 16, BLOCK_SIZE),
        catSheet.get(103, 272, 16, 16, BLOCK_SIZE),
        catSheet.get(135, 272, 16, 16, BLOCK_SIZE),
        catSheet.get(167, 272, 16, 16, BLOCK_SIZE),
        catSheet.get(200, 272, 16, 16, BLOCK_SIZE),
        ),
        "sit": Animation(
        catSheet.get(8, 16, 16, 16, BLOCK_SIZE),
        catSheet.get(40, 16, 16, 16, BLOCK_SIZE),
        catSheet.get(72, 16, 16, 16, BLOCK_SIZE),
        catSheet.get(104, 16, 16, 16, BLOCK_SIZE),
		duration=25
        ),
    },
	
    "dog": Animation(
            dogSheet.get(30, 36, 195, 195, BLOCK_SIZE),
            dogSheet.get(250, 36, 195, 195, BLOCK_SIZE),
        ),
	
    "rabbit": rabbitsSheet.get(0, 18, 100, 100),
    
    #Ores
    Blocks.CoalOre: everythingSheet.get(352, 0, 16, 16, BLOCK_SIZE),
    Blocks.IronOre: everythingSheet.get(368, 0, 16, 16, BLOCK_SIZE),
	Items.IronOre: everythingSheet.get(368, 0, 16, 16),
    Blocks.GoldOre: everythingSheet.get(384, 0, 16, 16, BLOCK_SIZE),
	Items.GoldOre: everythingSheet.get(384, 0, 16, 16),
    Blocks.DiamondOre: everythingSheet.get(400, 0, 16, 16, BLOCK_SIZE),
	
    #Ingots
    Items.Coal: everythingSheet.get(416, 0, 16, 16),
    Items.IronIngot: everythingSheet.get(432, 0, 16, 16),
	Items.GoldIngot: everythingSheet.get(448, 0, 16, 16),
	Items.Diamond: everythingSheet.get(464, 0, 16, 16),
    
    
    #---BLOCKS---	
    Blocks.Air: Surface((0,0), SRCALPHA),

    # Dirt
    Blocks.Dirt: everythingSheet.get(480, 0, 16, 16, BLOCK_SIZE),
	Items.Dirt: everythingSheet.get(480, 0, 16, 16),
 
	#Grass
    Blocks.Grass: everythingSheet.get(496, 0, 16, 16, BLOCK_SIZE),
	Items.Grass: everythingSheet.get(496, 0, 16, 16),
 
    #Stone 
	Blocks.Stone: everythingSheet.get(512, 0, 16, 16, BLOCK_SIZE),
	Items.Stone: everythingSheet.get(512, 0, 16, 16),
 
    #Cobblestone
    Blocks.Cobblestone: everythingSheet.get(528, 0, 16, 16, BLOCK_SIZE),
	Items.Cobblestone: everythingSheet.get(528, 0, 16, 16),
    
    #Wood
    Blocks.Planks: everythingSheet.get(544, 0, 16, 16, BLOCK_SIZE),
	Items.Planks: everythingSheet.get(544, 0, 16, 16),
    Blocks.Log: everythingSheet.get(560, 0, 16, 16, BLOCK_SIZE),
	Items.Log: everythingSheet.get(560, 0, 16, 16),
    Blocks.Leaves: weirdBlocksSheet.get(30, 5, 360, 360, BLOCK_SIZE),
    Blocks.CraftingTable: everythingSheet.get(592, 0, 14, 16, BLOCK_SIZE),
	Items.CraftingTable: everythingSheet.get(592, 0, 14, 16),
	Items.Sticks: everythingSheet.get(606, 0, 16, 16),
 
    #Furnace
    Blocks.Furnace: everythingSheet.get(622, 0, 16, 16, BLOCK_SIZE),
    "furnaceOn": everythingSheet.get(638, 0, 16, 16, BLOCK_SIZE),
    Items.Furnace: everythingSheet.get(622, 0, 16, 16),

    #Misc
    Blocks.Torch: everythingSheet.get(576, 0, 16, 16, BLOCK_SIZE),
	Items.Torch: everythingSheet.get(576, 0, 16, 16),
	Items.RabbitMeat: everythingSheet.get(654, 0, 16, 16),
	Items.BucketEmpty: everythingSheet.get(718, 0, 16, 16),
	Items.BucketWater: everythingSheet.get(734, 0, 16, 16),
	Items.BucketMilk: everythingSheet.get(750, 0, 16, 16),
  
  
    #---TOOLS---
    #Wooden
    Items.WoodenAxe: everythingSheet.get(0, 0, 16, 16),
    Items.WoodenPickaxe: everythingSheet.get(16, 0, 16, 16),
    Items.WoodenShovel: everythingSheet.get(32, 0, 16, 16),
    Items.WoodenSword: everythingSheet.get(48, 0, 16, 16),

    #Stone
    Items.StoneAxe: everythingSheet.get(64, 0, 16, 16),
    Items.StonePickaxe: everythingSheet.get(80, 0, 16, 16),
    Items.StoneShovel: everythingSheet.get(96, 0, 16, 16),
    Items.StoneSword: everythingSheet.get(112, 0, 16, 16),
    
    #Iron
    Items.IronAxe: everythingSheet.get(128, 0, 16, 16),
    Items.IronPickaxe: everythingSheet.get(144, 0, 16, 16),
    Items.IronShovel: everythingSheet.get(160, 0, 16, 16),
    Items.IronSword: everythingSheet.get(176, 0, 16, 16),
    
    #Gold
    Items.GoldAxe: everythingSheet.get(192, 0, 16, 16),
    Items.GoldPickaxe: everythingSheet.get(208, 0, 16, 16),
    Items.GoldShovel: everythingSheet.get(224, 0, 16, 16),
    Items.GoldSword: everythingSheet.get(240, 0, 16, 16),
    
    #Diamond
    Items.DiamondAxe: everythingSheet.get(256, 0, 16, 16),
    Items.DiamondPickaxe: everythingSheet.get(272, 0, 16, 16),
    Items.DiamondShovel: everythingSheet.get(288, 0, 16, 16),
    Items.DiamondSword: everythingSheet.get(304, 0, 16, 16),
    
    #Misc
    "shears": everythingSheet.get(320, 0, 16, 16),
    "flintAndSteel": everythingSheet.get(336, 0, 16, 16),
    
    
    #---ARMOUR---
	Items.GoldHelmet: everythingSheet.get(670, 0, 16, 16),
	Items.IronHelmet: everythingSheet.get(686, 0, 16, 16),
	Items.DiamondHelmet: everythingSheet.get(702, 0, 16, 16),
    
    
    #---HEARTS---
    "empty heart": weirdBlocksSheet.get(0, 0, 9, 9, BLOCK_SIZE),
    "half heart": weirdBlocksSheet.get(18, 0, 9, 9, BLOCK_SIZE),
    "full heart": weirdBlocksSheet.get(9, 0, 9, 9, BLOCK_SIZE),
}