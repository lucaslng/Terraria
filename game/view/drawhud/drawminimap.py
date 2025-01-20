from time import perf_counter
from game.model.world import World
from utils.constants import BLOCK_SIZE, WORLD_WIDTH, WORLD_HEIGHT
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

def drawMinimap(world: World, lightmap: list[list[int]], lights: Light, camera: pg.Rect, minimapSize: tuple[int, int]) -> None:
    """Draw a minimap of the surrounding world but at a smaller scale"""
    MINIMAP_SCALE = 4
    borderWidth = 2
    borderColour = (80, 80, 80)
    
    #Calculate visible area
    centerX = (camera.left + camera.right) // 2
    centerY = (camera.top + camera.bottom) // 2
    blocks_wide = minimapSize[0] // MINIMAP_SCALE
    blocks_high = minimapSize[1] // MINIMAP_SCALE
    startX = max(0, (centerX // BLOCK_SIZE) - (blocks_wide // 2))
    endX = min(WORLD_WIDTH, startX + blocks_wide)
    startY = max(0, (centerY // BLOCK_SIZE) - (blocks_high // 2))
    endY = min(WORLD_HEIGHT, startY + blocks_high)
    
    lightSurf = pg.Surface(minimapSize, pg.SRCALPHA)
    # time = 0
    # time2 = perf_counter()
    # time3 = 0
    for y in range(startY, endY):
        for x in range(startX, endX):
            minimapX = (x - startX) * MINIMAP_SCALE
            minimapY = (y - startY) * MINIMAP_SCALE
            isDark = False
            try:
                alpha = min(
                    surfaces.sunlight.get_at((minimapX, minimapY))[3],
                    surfaces.sunlight.get_at((minimapX + MINIMAP_SCALE, minimapY))[3],
                    surfaces.sunlight.get_at((minimapX, minimapY + MINIMAP_SCALE))[3],
                    surfaces.sunlight.get_at((minimapX + MINIMAP_SCALE, minimapY + MINIMAP_SCALE))[3]
                )
                isDark = alpha == 253
            except IndexError:
                pass
            if not isDark:
                #Draw back blocks first
                back_block = world.back[y][x]
                if not isinstance(back_block, AirBlock) and world[y][x].isEmpty:
                    # start = perf_counter()
                    surfaces.minimap.blit(minimap_cache.getScaledSpritesBack(back_block.enum) ,(minimapX, minimapY))
                    # time += perf_counter() - start
                
                frontBlock = world[y][x]
                if not isinstance(frontBlock, AirBlock):
                    # start = perf_counter()
                    surfaces.minimap.blit(
                        minimap_cache.getScaledSprite(frontBlock.enum),
                        (minimapX, minimapY)
                    )
                    # time += perf_counter() - start
                    
            # if y < world.height * 0.58 + 15:
            # start = perf_counter()
            pg.draw.rect(lightSurf, (0, 0, 0, lightmap[y][x]), (minimapX, minimapY, MINIMAP_SCALE, MINIMAP_SCALE))
            # time3 += perf_counter() - start
    # print(round(time, 4), round(time3, 4), round(perf_counter() - time2, 4))
    # time = 0
    for light, lightx, lighty in lights:
        minimapLightX = (lightx - startX) * MINIMAP_SCALE
        minimapLightY = (lighty - startY) * MINIMAP_SCALE
        scaledRadius = light.lightRadius * MINIMAP_SCALE
        
        if (0 <= minimapX <= minimapSize[0] and 
            0 <= minimapY <= minimapSize[1]):
            pg.draw.circle(lightSurf, (255, 255, 255, 0), (minimapLightX, minimapLightY), scaledRadius)
    
    surfaces.minimapLight.blit(lightSurf, (0, 0))
    
    #Draw border
    pg.draw.rect(surfaces.minimap, borderColour, pg.Rect(0, 0, minimapSize[0], minimapSize[1]), borderWidth)