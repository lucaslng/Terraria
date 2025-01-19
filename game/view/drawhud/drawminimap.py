from utils.constants import BLOCK_SIZE, WORLD_HEIGHT, WORLD_WIDTH
from game.model.blocks.airblock import AirBlock
from game.view import surfaces
from game.textures.sprites import sprites
from game.utils.backtint import BACK_TINT
from game.model.light import Light
import pygame as pg

class MinimapCache:
    def __init__(self, scale):
        self.scale = scale
        self.scaledSprites = {}         #normal blocks
        self.scaledSpritesBack = {}     #background blocks
        self.lightSurface = None
        
    def initLightSurf(self, minimapSize):
        if self.lightSurface is None or self.lightSurface.get_size() != minimapSize:
            self.lightSurface = pg.Surface(minimapSize, pg.SRCALPHA)
        return self.lightSurface
        
    def getScaledSprite(self, enum):
        if enum not in self.scaledSprites:
            texture = sprites[enum]
            self.scaledSprites[enum] = pg.transform.scale(texture, (self.scale, self.scale))
        return self.scaledSprites[enum]
    
    def getScaledSpritesBack(self, enum):
        if enum not in self.scaledSpritesBack:
            texture = sprites[enum].copy()
            texture.blit(BACK_TINT, (0, 0))
            self.scaledSpritesBack[enum] = pg.transform.scale(texture, (self.scale, self.scale))
        return self.scaledSpritesBack[enum]

minimap_cache = MinimapCache(4)

def drawMinimap(world, lightmap, lights: Light, camera: pg.Rect, minimap_size: tuple[int, int]) -> None:
    '''Draw a minimap of the surrounding world but at a smaller scale'''
    
    MINIMAP_SCALE = 4
    border_width = 2
    border_colour = (255, 0, 0)
    
    #Calculate visible area
    centerX = (camera.left + camera.right) // 2
    centerY = (camera.top + camera.bottom) // 2
    blocks_wide = minimap_size[0] // MINIMAP_SCALE
    blocks_high = minimap_size[1] // MINIMAP_SCALE
    startX = max(0, (centerX // BLOCK_SIZE) - (blocks_wide // 2))
    endX = min(WORLD_WIDTH, startX + blocks_wide)
    startY = max(0, (centerY // BLOCK_SIZE) - (blocks_high // 2))
    endY = min(WORLD_HEIGHT, startY + blocks_high)
    
    lightSurf = minimap_cache.initLightSurf(minimap_size)
    lightSurf.fill((0, 0, 0, 0))
    
    for y in range(startY, endY):
        for x in range(startX, endX):
            minimapX = (x - startX) * MINIMAP_SCALE
            minimapY = (y - startY) * MINIMAP_SCALE
            
            #Draw back blocks first
            back_block = world.back[y][x]
            if not isinstance(back_block, AirBlock):
                surfaces.minimap.blit(minimap_cache.getScaledSpritesBack(back_block.enum) ,(minimapX, minimapY))
            
            front_block = world[y][x]
            if not isinstance(front_block, AirBlock):
                surfaces.minimap.blit(
                    minimap_cache.getScaledSprite(front_block.enum),
                    (minimapX, minimapY)
                )
            
            pg.draw.rect(lightSurf, (0, 0, 0, lightmap[y][x]), (minimapX, minimapY, MINIMAP_SCALE, MINIMAP_SCALE))
    
    for light, lightx, lighty in lights:
        mini_light_x = (lightx - startX) * MINIMAP_SCALE
        mini_light_y = (lighty - startY) * MINIMAP_SCALE
        scaled_radius = light.lightRadius * MINIMAP_SCALE
        
        if (0 <= mini_light_x <= minimap_size[0] and 
            0 <= mini_light_y <= minimap_size[1]):
            pg.draw.circle(lightSurf, (255, 255, 255, 0), (mini_light_x, mini_light_y), scaled_radius)
    
    surfaces.minimapLight.blit(lightSurf, (0, 0))
    
    #Draw border
    pg.draw.rect(surfaces.minimap, border_colour, pg.Rect(0, 0, minimap_size[0], minimap_size[1]), border_width)