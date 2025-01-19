import pygame as pg


class Animation:
    '''list of frames to cycle between for an animation. unit of duration is in frames'''
    def __init__(this, *args, duration: int=10, startFrame: int = 0):
        this.arr: list[pg.surface.Surface] = list(args)
        this.duration = duration
        this.frame = startFrame * duration
    
    def __getitem__(this, i: int) -> pg.surface.Surface:
        return this.arr[i]
    
    def drawAnimated(this, surface: pg.Surface, center: tuple[int, int], flipped=False) -> None:
        '''draws the the animation, takes a pixel relative to camera'''
        index = this.frame // this.duration
        this.frame += 1
        if this.frame > len(this.arr) * this.duration - 1:
            this.frame = 0
        this.drawFrame(surface, center, index, flipped)

    def drawFrame(this, surface: pg.Surface, center: tuple[int, int], index=0, flipped=False) -> None:
        '''draws the frame of the given index, takes a pixel relative to camera'''
        texture = this[index]
        if flipped:
            texture = pg.transform.flip(texture, True, False).convert_alpha()
        surface.blit(texture, texture.get_rect(center=center))
        # pg.draw.rect(surface, (0, 0, 0), texture.get_rect(center=center), 1)