import pygame as pg
from typing import *

from constants import *

pg.init()

class SpriteSheet:
    '''sprite sheet class'''
    def __init__(this, imageName: str):
        this.sheet = pg.image.load(imageName).convert_alpha()
        
    def get(this, x, y, width, height, colour=(0,0,0)):
        image = pg.Surface((width, height), pg.SRCALPHA)
        image.blit(this.sheet, (0, 0), (x, y, width, height))
        if colour != (0, 0, 0):
            image.set_colorkey(colour)
   
        return image
            

class Animation:
    '''list of frames to cycle between for an animation. unit of duration is in frames'''
    def __init__(this, *args, duration: int=10, startFrame: int = 0):
        this.arr: List[pg.surface.Surface] = list(args)
        this.duration = duration
        this.frame = startFrame * duration
    
    def __getitem__(this, i: int) -> pg.surface.Surface:
        return this.arr[i]
    
    def drawAnimated(this, x: int, y: int, flipped=False):
        '''draws the the animation, takes a pixel relative to camera'''
        index = this.frame//this.duration
        this.frame += 1
        if this.frame > len(this.arr) * this.duration - 1: this.frame = 0
        return this.drawFrame(x, y, index, flipped)

    def drawFrame(this, x: int, y: int, index=0, flipped=False):
        '''draws the frame of the given index, takes a pixel relative to camera'''
        texture = this[index]
        if flipped: texture = pg.transform.flip(texture, True, False).convert_alpha()
        return SURF.blit(texture, (x, y))


catSheet = SpriteSheet("cat.png")
everythingSheet = SpriteSheet("everything.png")
weirdBlocksSheet = SpriteSheet("weird block spritesheet.png")

sprites = {
    "cat": {
        "walk": Animation(
        catSheet.get(9, 144, 16, 16),
        catSheet.get(40, 144, 16, 16),
        catSheet.get(71, 144, 16, 16),
        catSheet.get(103, 144, 16, 16),
        catSheet.get(135, 144, 16, 16),
        catSheet.get(167, 144, 16, 16),
        catSheet.get(200, 144, 16, 16),
        catSheet.get(232, 144, 16, 16),
        ),
        "run": Animation(
        catSheet.get(9, 176, 16, 16),
        catSheet.get(40, 176, 16, 16),
        catSheet.get(71, 176, 16, 16),
        catSheet.get(103, 176, 16, 16),
        catSheet.get(135, 176, 16, 16),
        catSheet.get(167, 176, 16, 16),
        catSheet.get(200, 176, 16, 16),
        catSheet.get(232, 176, 16, 16),
        ),
        "jump": Animation(
        catSheet.get(9, 272, 16, 16),
        catSheet.get(40, 272, 16, 16),
        catSheet.get(71, 272, 16, 16),
        catSheet.get(103, 272, 16, 16),
        catSheet.get(135, 272, 16, 16),
        catSheet.get(167, 272, 16, 16),
        catSheet.get(200, 272, 16, 16),
        ),
        "sit": Animation(
        catSheet.get(8, 16, 16, 16),
        catSheet.get(40, 16, 16, 16),
        catSheet.get(72, 16, 16, 16),
        catSheet.get(104, 16, 16, 16),
        ),
    },
    
    #Ores
    "coalOre": everythingSheet.get(352, 0, 16, 16),
    "ironOre": everythingSheet.get(368, 0, 16, 16),
    "goldOre": everythingSheet.get(384, 0, 16, 16),
    "diamondOre": everythingSheet.get(400, 0, 16, 16),
    
    #---BLOCKS---
    #Grass
    "dirt": everythingSheet.get(480, 0, 16, 16),
    "grass": everythingSheet.get(496, 0, 16, 16),
    
    #Stone
    "stone": everythingSheet.get(512, 0, 16, 16),
    "cobblestone": everythingSheet.get(528, 0, 16, 16),
    
    #Wood
    "oak plank": everythingSheet.get(544, 0, 16, 16),
    "oak log": everythingSheet.get(560, 0, 16, 16,),
    "oak leaves": weirdBlocksSheet.get(30, 5, 360, 360),
    
    #Misc
    "torch": everythingSheet.get(576, 0, 16, 16),
    
    #---ITEMS---
    "coal": everythingSheet.get(416, 0, 16, 16, 15),
  
  
    #---TOOLS---
    #Wooden
    "woodenAxe": everythingSheet.get(0, 0, 16, 16),
    "woodenPickaxe": everythingSheet.get(16, 0, 16, 16),
    "woodenShovel": everythingSheet.get(32, 0, 16, 16),
    "woodenSword": everythingSheet.get(48, 0, 16, 16),
  
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
    "empty heart": weirdBlocksSheet.get(0, 0, 9, 9),
    "half heart": weirdBlocksSheet.get(18, 0, 9, 9),
    "full heart": weirdBlocksSheet.get(9, 0, 9, 9),
}