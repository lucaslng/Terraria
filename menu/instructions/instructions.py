import pygame as pg
from constants import HEIGHT, SURF, WIDTH
from screens import Screens
from utils.updatescreen import updateScreen
from widgets.button import Button


def instructionsScreen():
    '''Instructions screen'''

    title_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 36)
    text_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 24)
    button_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 28)
    text_color = (240, 240, 240)
    background_color = (40, 40, 40)
    button_text_colour = (240, 240, 240)
    text_shadow = (20, 20, 20, 160)

    background = pg.Surface((WIDTH, HEIGHT))
    background.fill(background_color)

    title_text = "Instructions"
    title_surface = title_font.render(title_text, True, text_color)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 6))

    #Instruction text
    instructions = [
        "- Use WASD to move your character.",
        "- Left-click to break blocks.",
        "- Right-click to place blocks.",
        "- Press 'E' to open your inventory.",
        "- Explore the world!"
    ]

    instruction_surfaces = [
        text_font.render(line, True, text_color) for line in instructions
    ]

    #Buttons
    button_width, button_height = 300, 50
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT - button_height - 50

    back_button = Button(button_x, button_y, button_width, button_height, "Back")

    while True:
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return Screens.QUIT

            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                back_button.handle_event(event, mouse_pos)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.rect.collidepoint(mouse_pos):
                    return Screens.MENU

        back_button.update(mouse_pos)

        SURF.blit(background, (0, 0))
        SURF.blit(title_surface, title_rect)

        #Draw instructions
        for i, surface in enumerate(instruction_surfaces):
            line_rect = surface.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 40))
            SURF.blit(surface, line_rect)

        back_button.draw(button_font, button_text_colour, text_shadow)

        updateScreen()