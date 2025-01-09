import pygame as pg, math, time, threading, random
from queue import Queue

from constants import SURF, WIDTH, HEIGHT, FPS, clock
from utils import sysexit


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
        
    def handle_event(self, event, mouse_pos):
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
        
        self._draw_button(button_rect, current_color)
        self._draw_text(font, text_colour, shadow_colour, button_rect)
        
    def _draw_button(self, button_rect, colour):
        # Draw shadow first
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
        
    def _draw_text(self, font, text_colour, shadow_color, button_rect):
        #Scale text with the hover animation
        scale_factor = 1 + self.hover_animation * 0.05
        
        text_surf = font.render(self.text, True, text_colour)
        text_surf = pg.transform.scale(text_surf, (int(text_surf.get_width() * scale_factor), int(text_surf.get_height() * scale_factor)))
        text_rect = text_surf.get_rect(center=button_rect.center)
        
        #Text shadow
        shadow_surf = font.render(self.text, True, shadow_color)
        shadow_surf = pg.transform.scale(shadow_surf, (int(shadow_surf.get_width() * scale_factor), int(shadow_surf.get_height() * scale_factor)))
        shadow_rect = shadow_surf.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        
        SURF.blit(shadow_surf, shadow_rect)
        SURF.blit(text_surf, text_rect)

def mainMenu():
    button_font = pg.font.Font("MinecraftRegular-Bmg3.otf",  36)
    splash_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 28)
    button_text_colour = (240, 240, 240)
    text_shadow = (20, 20, 20, 160)

    bg_panorama = pg.image.load("title screen background animation.jpg").convert()
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(40)

    title_image = pg.image.load("title screen title.png").convert_alpha()
    title_image_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))

    splash_texts = [
      "Dont sue us Mojang!",
      "Made with Pygame!",
      "Lorem ipsum!",
      "Pygame >",
    ]
  
    current_splash = random.choice(splash_texts)
    splash_angle = -15
    splash_wave_offset = 0
    splash_scale = 1.0

    button_width, button_height = 400, 50
    button_x = (WIDTH - button_width) // 2
    spacing = 24
    start_y = HEIGHT // 2

    buttons = {
        'play': Button(button_x, start_y, button_width, button_height, "Play"),
        'instructions': Button(button_x, start_y + button_height + spacing, button_width, button_height, "Instructions"),
        'options': Button(button_x, start_y + (button_height + spacing) * 2, button_width, button_height, "Options"),
        'quit': Button(button_x, start_y + (button_height + spacing) * 3, button_width, button_height, "Quit"),
    }

    bg_scroll_speed = 20
    bg_offset = 0
    clock = pg.time.Clock()

    while True:
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit"

            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                for button in buttons.values():
                    button.handle_event(event, mouse_pos)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if buttons['play'].rect.collidepoint(mouse_pos):
                    return
                elif buttons['instructions'].rect.collidepoint(mouse_pos):
                    instructionsScreen()
                elif buttons['options'].rect.collidepoint(mouse_pos):
                    changeKeybinds()
                elif buttons['quit'].rect.collidepoint(mouse_pos):
                    sysexit()

        for button in buttons.values():
            button.update(mouse_pos)

        bg_offset = (bg_offset + bg_scroll_speed * clock.get_time() / 1000.0) % bg_panorama.get_width()

        #Draw background
        SURF.blit(bg_panorama, (-bg_offset, 0))
        SURF.blit(bg_panorama, (bg_panorama.get_width() - bg_offset, 0))
        SURF.blit(overlay, (0, 0))

        SURF.blit(title_image, title_image_rect)

        #Draw splash text
        splash_wave_offset += 0.03
        splash_scale = 1.0 + math.sin(splash_wave_offset * 0.5) * 0.03

        splash_surf = splash_font.render(current_splash, True, (255, 255, 0))
        splash_surf = pg.transform.rotate(splash_surf, splash_angle)
        splash_surf = pg.transform.scale(splash_surf, (int(splash_surf.get_width() * splash_scale), int(splash_surf.get_height() * splash_scale)))

        splash_y_offset = math.sin(splash_wave_offset) * 6
        splash_pos = (WIDTH // 2 + 180, HEIGHT // 4 + splash_y_offset)
        SURF.blit(splash_surf, splash_pos)

        #Draw buttons
        for button in buttons.values():
            button.draw(button_font, button_text_colour, text_shadow)

        pg.display.flip()
        clock.tick(FPS)
    
#TODO work on these later hopefully        
def instructionsScreen():
  pass
          
def changeKeybinds():
    pass
  
def pauseMenu():
    button_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 36)
    button_text_colour = (240, 240, 240)
    text_shadow = (20, 20, 20, 160)

    resume_button = Button((WIDTH - 400) // 2, HEIGHT // 2, 400, 50, "Back to Game")
    quit_button = Button((WIDTH - 400) // 2, (HEIGHT // 2) + 100, 400, 50, "Save and Quit")
    
    blurScale = 0.1    #lower is blurrier
    screen_size = SURF.get_size()
    small_size = (int(screen_size[0] * blurScale), int(screen_size[1] * blurScale))
    small_surface = pg.transform.smoothscale(SURF, small_size)
    blurred_surface = pg.transform.smoothscale(small_surface, screen_size)

    buttons = {
        'resume': resume_button,
        'quit': quit_button,
    }

    clock = pg.time.Clock()
    while True:
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sysexit()

            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                for button in buttons.values():
                    button.handle_event(event, mouse_pos)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if buttons['resume'].rect.collidepoint(mouse_pos):
                    return
                elif buttons['quit'].rect.collidepoint(mouse_pos):
                    sysexit()

        for button in buttons.values():
            button.update(mouse_pos)

        SURF.blit(blurred_surface, (0, 0))
        
        for button in buttons.values():
            button.draw(button_font, button_text_colour, text_shadow)

        pg.display.flip()
        clock.tick(FPS)

class LoadingScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        
        self.font = pg.font.Font("MinecraftRegular-Bmg3.otf", 20)
        self.titleFont = pg.font.Font("MinecraftRegular-Bmg3.otf", 40)

        self.currentStep = "Initializing world..."
        
        self.currentMessage = 0   #seconds
        self.progress = 0.0
        self.startTime = time.time()

        self.barWidth = 400
        self.barHeight = 20
        self.barX = (width - self.barWidth) // 2
        self.barY = height // 2 + 30
        
    def update(self, progress, current_step):
        self.progress = progress
        self.currentStep = current_step

    def draw(self):
        self.screen.fill((25, 25, 25))

        title = self.titleFont.render("Loading world...", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title, title_rect)

        #Loading message
        message = self.font.render(self.currentStep, True, (200, 200, 200))
        message_rect = message.get_rect(center=(self.width // 2, self.height // 2 - 20))
        self.screen.blit(message, message_rect)

        #Progress bar
        pg.draw.rect(self.screen, (50, 50, 50), (self.barX, self.barY, self.barWidth, self.barHeight))
        fill_width = int(self.barWidth * self.progress)
        pg.draw.rect(self.screen, (106, 176, 76), (self.barX, self.barY, fill_width, self.barHeight))

        #Percentage
        percentage = f"{int(self.progress * 100)}%"
        percent_text = self.font.render(percentage, True, (255, 255, 255))
        percent_rect = percent_text.get_rect(center=(self.width // 2, self.barY + 40))
        self.screen.blit(percent_text, percent_rect)

        #Elapsed load time
        elapsed_time = time.time() - self.startTime
        elapsed_text = self.font.render(f"Time elapsed: {elapsed_time:.1f} seconds", True, (200, 200, 200))
        elapsed_rect = elapsed_text.get_rect(center=(self.width // 2, self.barY + 120))
        self.screen.blit(elapsed_text, elapsed_rect)

        pg.display.flip()
        clock.tick(FPS)