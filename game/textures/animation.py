from typing import List
import pygame as pg

from constants import SURF

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
        if this.frame > len(this.arr) * this.duration - 1:
            this.frame = 0
        return this.drawFrame(x, y, index, flipped)

    def drawFrame(this, x: int, y: int, index=0, flipped=False):
        '''draws the frame of the given index, takes a pixel relative to camera'''
        texture = this[index]
        if flipped:
            texture = pg.transform.flip(texture, True, False).convert_alpha()
        return SURF.blit(texture, (x, y))