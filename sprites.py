import pygame as pg
from typing import Dict, List, Set, Tuple

from constants import *

pg.init()

class SpriteSheet:
    '''sprite sheet class'''
    def __init__(this, imageName: str):
        this.sheet = pg.image.load(imageName).convert_alpha()
        
    def get(this, x, y, width, height, scale=BLOCK_SIZE, colour=(0,0,0)):
        image = pg.Surface((width, height), pg.SRCALPHA)
        image.blit(this.sheet, (0, 0), (x, y, width, height))
        if colour != (0, 0, 0):
            image.set_colorkey(colour)

        image = pg.transform.scale(image, (scale, scale))
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

oreSheet = SpriteSheet("ores.png")

woodenToolsSheet = SpriteSheet("wooden_tools.png")
stoneToolsSheet = SpriteSheet("stone_tools.png")
ironToolsSheet = SpriteSheet("iron_tools.png")

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
    "coalOre": oreSheet.get(0, 0, 16, 16, BLOCK_SIZE),
    "ironOre": oreSheet.get(16, 0, 16, 16, BLOCK_SIZE),
  
    #Wooden
    "woodenAxe": woodenToolsSheet.get(0, 0, 16, 16, 15),
    "woodenPickaxe": woodenToolsSheet.get(16, 0, 16, 16, 15),
    "woodenShovel": woodenToolsSheet.get(32, 0, 16, 16, 15),
    "woodenSword": woodenToolsSheet.get(48, 0, 16, 16, 15),
  
    #Stone
    "stoneAxe": stoneToolsSheet.get(0, 0, 16, 16, 15),
    "stonePickaxe": stoneToolsSheet.get(16, 0, 16, 16, 15),
    "stoneShovel": stoneToolsSheet.get(32, 0, 16, 16, 15),
    "stoneSword": stoneToolsSheet.get(48, 0, 16, 16, 15),
    
    #Iron
    "ironAxe": ironToolsSheet.get(0, 0, 16, 16, 15),
    "ironPickaxe": ironToolsSheet.get(16, 0, 16, 16, 15),
    "ironShovel": ironToolsSheet.get(32, 0, 16, 16, 15),
    "ironSword": ironToolsSheet.get(48, 0, 16, 16, 15),
}