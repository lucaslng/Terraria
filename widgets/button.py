import pygame as pg
from utils.constants import SURF

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        
        self.hover_animation = 0
        self.press_animation = 0
        self.is_pressed = False
        
        self.base_colour = (45, 45, 45)
        self.hover_colour = (75, 75, 75)
        
        #Corner roundness
        self.corner_radius = 15
        
    def update(self, mouse_pos):
        #Hover animation
        target_hover = 1 if self.rect.collidepoint(mouse_pos) else 0
        self.hover_animation += (target_hover - self.hover_animation) * 0.15
        
        #Click animation
        if self.is_pressed:
            self.press_animation += (1 - self.press_animation) * 0.2
        else:
            self.press_animation += (0 - self.press_animation) * 0.2
        
    def handleEvent(self, event, mouse_pos):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.is_pressed = False
        
    def draw(self, font, text_colour, shadow_colour):
        current_color = [int(self.base_colour[i] + (self.hover_colour[i] - self.base_colour[i]) * self.hover_animation) for i in range(3)]
        
        hover_offset = int(self.hover_animation * 3)
        press_offset = int(self.press_animation * 2)
        button_rect = self.rect.copy()
        button_rect.y -= hover_offset - press_offset
        
        self._drawButton(button_rect, current_color)
        self._drawText(font, text_colour, shadow_colour, button_rect)
        
    def _drawButton(self, button_rect, colour):
        #Draw shadow first
        shadow_rect = button_rect.copy()
        shadow_rect.y += 4
        pg.draw.rect(SURF, (0, 0, 0, 64), shadow_rect, border_radius=self.corner_radius)
        
        #Base button
        button_surface = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        pg.draw.rect(button_surface, colour, button_surface.get_rect(), border_radius=self.corner_radius)
        
        button_mask = pg.mask.from_surface(button_surface)
        
        #Highlight surface
        highlight_surface = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        highlight_color = (255, 255, 255, 30)
        
        highlight_rect = pg.Rect(0, 0, button_rect.width, 8)
        pg.draw.rect(highlight_surface, highlight_color, highlight_rect)
        
        masked_highlight = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        button_mask.to_surface(masked_highlight, setcolor=highlight_color, unsetcolor=(0,0,0,0))
        
        final_highlight = pg.Surface((button_rect.width, button_rect.height), pg.SRCALPHA)
        final_highlight.blit(masked_highlight, (0,0), highlight_rect)
        
        SURF.blit(button_surface, button_rect)
        SURF.blit(final_highlight, button_rect)
        
    def _drawText(self, font, text_colour, shadow_color, button_rect):
        scale_factor = 1 + self.hover_animation * 0.05

        text_surf = font.render(self.text, True, text_colour)
        text_surf = pg.transform.scale(text_surf, (int(text_surf.get_width() * scale_factor), int(text_surf.get_height() * scale_factor)))
        text_rect = text_surf.get_rect(center=button_rect.center)
        
        text_rect.centery += 5
        SURF.blit(text_surf, text_rect)
