from pygame import SRCALPHA, Surface
import pygame as pg
from constants import BLOCK_SIZE
from game.model.blocks.utils.blocksenum import Blocks
from game.model.items.utils.itemsenum import Items
from game.textures.animation import Animation
from game.textures.spritesheets import catSheet, everythingSheet, weirdBlocksSheet

sprites = {
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
        ),
    },
    
    #Ores
    Blocks.CoalOre: everythingSheet.get(352, 0, 16, 16, BLOCK_SIZE),
    Blocks.IronOre: everythingSheet.get(368, 0, 16, 16, BLOCK_SIZE),
    "goldOre": everythingSheet.get(384, 0, 16, 16),
    "diamondOre": everythingSheet.get(400, 0, 16, 16),
    
    #---BLOCKS---
	
    Blocks.Air: Surface((0,0), SRCALPHA),

    # Dirt
    Blocks.Dirt: everythingSheet.get(480, 0, 16, 16, BLOCK_SIZE),
	Items.Dirt: everythingSheet.get(480, 0, 16, 16),
	# Grass
    Blocks.Grass: everythingSheet.get(496, 0, 16, 16, BLOCK_SIZE),
	Items.Grass: everythingSheet.get(496, 0, 16, 16),
    # Stone
	Blocks.Stone: everythingSheet.get(512, 0, 16, 16, BLOCK_SIZE),
	Items.Stone: everythingSheet.get(512, 0, 16, 16),
    # Cobblestone
    Blocks.Cobblestone: everythingSheet.get(528, 0, 16, 16, BLOCK_SIZE),
	Items.Cobblestone: everythingSheet.get(528, 0, 16, 16),
    
    #Wood
    Blocks.Planks: everythingSheet.get(544, 0, 16, 16, BLOCK_SIZE),
	Items.Planks: everythingSheet.get(544, 0, 16, 16),
    Blocks.Log: everythingSheet.get(560, 0, 16, 16, BLOCK_SIZE),
    Blocks.Leaves: weirdBlocksSheet.get(30, 5, 360, 360, BLOCK_SIZE),
    Blocks.CraftingTable: everythingSheet.get(592, 0, 14, 16, BLOCK_SIZE, BLOCK_SIZE),
	Items.CraftingTable: everythingSheet.get(592, 0, 14, 16),

    #Misc
    Blocks.Torch: everythingSheet.get(576, 0, 16, 16, BLOCK_SIZE),
	Items.Torch: everythingSheet.get(576, 0, 16, 16),
    
    #---ITEMS---
    "coal": everythingSheet.get(416, 0, 16, 16, 15),
  
  
    #---TOOLS---
    #Wooden
    Items.WoodenAxe: pg.transform.flip(everythingSheet.get(0, 0, 16, 16), True, False),
    Items.WoodenPickaxe: everythingSheet.get(16, 0, 16, 16),
    Items.WoodenShovel: everythingSheet.get(32, 0, 16, 16),
    Items.WoodenSword: everythingSheet.get(48, 0, 16, 16),
  
    #Stone
    "stoneAxe": everythingSheet.get(64, 0, 16, 16),
    "stonePickaxe": everythingSheet.get(80, 0, 16, 16),
    "stoneShovel": everythingSheet.get(96, 0, 16, 16),
    "stoneSword": everythingSheet.get(112, 0, 16, 16),
    
    #Iron
    "ironAxe": everythingSheet.get(128, 0, 16, 16),
    "ironPickaxe": everythingSheet.get(144, 0, 16, 16),
    "ironShovel": everythingSheet.get(160, 0, 16, 16),
    "ironSword": everythingSheet.get(176, 0, 16, 16),
    
    #Gold
    "goldAxe": everythingSheet.get(192, 0, 16, 16),
    "goldPickaxe": everythingSheet.get(208, 0, 16, 16),
    "goldShovel": everythingSheet.get(224, 0, 16, 16),
    "goldSword": everythingSheet.get(240, 0, 16, 16),
    
    #Diamond
    "diamondAxe": everythingSheet.get(256, 0, 16, 16),
    "diamondPickaxe": everythingSheet.get(272, 0, 16, 16),
    "diamondShovel": everythingSheet.get(288, 0, 16, 16),
    "diamondSword": everythingSheet.get(304, 0, 16, 16),
    
    #Misc
    "shears": everythingSheet.get(320, 0, 16, 16),
    "flintAndSteel": everythingSheet.get(336, 0, 16, 16),
    
    #---HEARTS---
    "empty heart": weirdBlocksSheet.get(0, 0, 9, 9, BLOCK_SIZE),
    "half heart": weirdBlocksSheet.get(18, 0, 9, 9, BLOCK_SIZE),
    "full heart": weirdBlocksSheet.get(9, 0, 9, 9, BLOCK_SIZE),
}