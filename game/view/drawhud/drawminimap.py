from utils.constants import BLOCK_SIZE, BLOCK_RECT, SURF
from game.model.world import World
from game.model.blocks.airblock import AirBlock
from game.textures.sprites import sprites
from game.utils.backtint import BACK_TINT
import pygame as pg


def drawMinimap(world: World, camera: pg.Rect, screen_pos: tuple[int, int], minimap_size: tuple[int, int]):
    """Draw a minimap using the game's existing block sprites but at a smaller scale"""
    # Calculate the center of the current view
    center_x = (camera.left + camera.right) // 2
    center_y = (camera.top + camera.bottom) // 2
    
    MINIMAP_SCALE = 4  # Each block will be 4x4 pixels
    
    # Calculate visible blocks in minimap
    blocks_wide = minimap_size[0] // MINIMAP_SCALE
    blocks_high = minimap_size[1] // MINIMAP_SCALE
    
    # Find the world coordinates to show
    start_x = max(0, (center_x // BLOCK_RECT.width) - (blocks_wide // 2))
    end_x = min(world.width, start_x + blocks_wide)
    start_y = max(0, (center_y // BLOCK_RECT.height) - (blocks_high // 2))
    end_y = min(world.height, start_y + blocks_high)
    
    # Create a surface for the minimap
    minimap_surface = pg.Surface(minimap_size, pg.SRCALPHA)
    
    # Draw each block in the minimap
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            # Calculate position on minimap
            minimap_x = (x - start_x) * MINIMAP_SCALE
            minimap_y = (y - start_y) * MINIMAP_SCALE
            
            # Draw background blocks first
            if not isinstance(world.back[y][x], AirBlock):
                # Get the block's texture and scale it down
                texture = sprites[world.back[y][x].enum].copy()
                texture.blit(BACK_TINT, (0, 0))  # Apply the same tint as main view
                scaled_texture = pg.transform.scale(texture, (MINIMAP_SCALE, MINIMAP_SCALE))
                minimap_surface.blit(scaled_texture, (minimap_x, minimap_y))
            
            # Draw foreground blocks
            if not isinstance(world[y][x], AirBlock):
                texture = sprites[world[y][x].enum].copy()
                scaled_texture = pg.transform.scale(texture, (MINIMAP_SCALE, MINIMAP_SCALE))
                minimap_surface.blit(scaled_texture, (minimap_x, minimap_y))
    
    # Draw camera view rectangle
    view_x = ((camera.left // BLOCK_RECT.width) - start_x) * MINIMAP_SCALE
    view_y = ((camera.top // BLOCK_RECT.height) - start_y) * MINIMAP_SCALE
    view_width = (camera.width // BLOCK_RECT.width) * MINIMAP_SCALE
    view_height = (camera.height // BLOCK_RECT.height) * MINIMAP_SCALE
    pg.draw.rect(minimap_surface, (255, 255, 255), 
                (view_x, view_y, view_width, view_height), 1)
    
    # Draw the minimap on the main surface
    SURF.blit(minimap_surface, screen_pos)