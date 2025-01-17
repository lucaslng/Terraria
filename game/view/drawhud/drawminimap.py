from utils.constants import BLOCK_SIZE, WORLD_HEIGHT, WORLD_WIDTH
from game.model.blocks.airblock import AirBlock
from game.view import surfaces
from game.textures.sprites import sprites
from game.utils.backtint import BACK_TINT
from game.model.light import Light
import pygame as pg

def drawMinimap(world, lightmap, lights: Light, camera: pg.Rect, minimap_size: tuple[int, int]) -> None:
    """Draw a minimap of the surroundingworld but at a smaller scale"""
    #Calculate the center of the current view
    centerX = (camera.left + camera.right) // 2
    centerY = (camera.top + camera.bottom) // 2
    
    MINIMAP_SCALE = 4
    border_width = 2
    border_colour = (255, 0, 0)
    
    #Calculate visible blocks in minimap
    blocks_wide = minimap_size[0] // MINIMAP_SCALE
    blocks_high = minimap_size[1] // MINIMAP_SCALE
    
    # Find the world coordinates to show
    startX = max(0, (centerX // BLOCK_SIZE) - (blocks_wide // 2))
    endX = min(WORLD_WIDTH, startX + blocks_wide)
    startY = max(0, (centerY // BLOCK_SIZE) - (blocks_high // 2))
    endY = min(WORLD_HEIGHT, startY + blocks_high)
    
    #Draw each block in the minimap
    for y in range(startY, endY):
        for x in range(startX, endX):
            minimap_x = (x - startX) * MINIMAP_SCALE
            minimap_y = (y - startY) * MINIMAP_SCALE
            
            #Draw back blocks first
            if not isinstance(world.back[y][x], AirBlock):
                #Get the block's texture and scale it down
                texture = sprites[world.back[y][x].enum].copy()
                texture.blit(BACK_TINT, (0, 0))
                scaled_texture = pg.transform.scale(texture, (MINIMAP_SCALE, MINIMAP_SCALE))
                surfaces.minimap.blit(scaled_texture, (minimap_x, minimap_y))
            
            if not isinstance(world[y][x], AirBlock):
                texture = sprites[world[y][x].enum].copy()
                scaled_texture = pg.transform.scale(texture, (MINIMAP_SCALE, MINIMAP_SCALE))
                surfaces.minimap.blit(scaled_texture, (minimap_x, minimap_y))
                
            #Draw natural light
            pg.draw.rect(surfaces.minimapLight, (0, 0, 0, lightmap[y][x]), (minimap_x, minimap_y, MINIMAP_SCALE, MINIMAP_SCALE))
    
    #Draw light from blocks
    for light, lightx, lighty in lights:
        #Convert world coordinates to minimap coordinates
        mini_light_x = (lightx - startX) * MINIMAP_SCALE
        mini_light_y = (lighty - startY) * MINIMAP_SCALE
        
        scaled_radius = light.lightRadius * MINIMAP_SCALE
        
        #Only draw if the light is visible in the minimap
        if (0 <= mini_light_x <= minimap_size[0] and 0 <= mini_light_y <= minimap_size[1]):
            pg.draw.circle(surfaces.minimapLight, (255, 255, 255, 0), (mini_light_x, mini_light_y), scaled_radius)
            
    #Draw border around the minimap
    border_rect = pg.Rect(0, 0, minimap_size[0], minimap_size[1])
    pg.draw.rect(surfaces.minimap, border_colour, border_rect, border_width)