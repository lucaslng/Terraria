import pygame as pg
from utils.constants import FRAME, SURF
from utils.screens import Screens
from utils.updatescreen import updateScreen
from widgets.button import Button


def instructionsScreen():
    '''Instructions screen'''

    titleFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 36)
    textFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 24)
    buttonFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 28)
    textColour = (240, 240, 240)
    backgroundColour = (40, 40, 40)
    buttonTextColour = (240, 240, 240)
    textShadow = (20, 20, 20, 160)

    background = pg.Surface((FRAME.width, FRAME.height))
    background.fill(backgroundColour)
    
    titleSurface = titleFont.render("Instructions", True, textColour)
    titleRect = titleSurface.get_rect(center=(FRAME.width // 2, FRAME.height // 6))

    #Instruction text
    instructions = [
        "- Use A and D to move your character.",
        "- Press space to jump.",
        "- Change your slots with the number keys."
        "- Left-click to break blocks.",
        "- Right-click to place blocks.",
        "- Press 'E' to open your inventory.",
        "- Press 'F' to interact with an entity (attack/talk)",
        "- Press 'C' to consume food.",
        "- Explore the world!",
    ]

    instructionSurfaces = [
        textFont.render(line, True, textColour) for line in instructions
    ]

    #Buttons
    buttonWidth, buttonHeight = 300, 50
    buttonx = (FRAME.width - buttonWidth) // 2
    buttony = FRAME.height - buttonHeight - 50

    back_button = Button(buttonx, buttony, buttonWidth, buttonHeight, "Back")

    while True:
        mousePos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return Screens.QUIT

            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                back_button.handleEvent(event, mousePos)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.rect.collidepoint(mousePos):
                    return Screens.MENU

        back_button.update(mousePos)

        SURF.blit(background, (0, 0))
        SURF.blit(titleSurface, titleRect)

        #Draw instructions
        for i, surface in enumerate(instructionSurfaces):
            lineRect = surface.get_rect(center=(FRAME.width // 2, FRAME.height // 3 + i * 40))
            SURF.blit(surface, lineRect)

        back_button.draw(buttonFont, buttonTextColour, textShadow)

        updateScreen()