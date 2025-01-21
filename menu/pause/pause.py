import pygame as pg
from utils.constants import WIDTH, HEIGHT, SURF, FRAME
from utils.screens import Screens
from utils.clearscreen import clearScreen
from utils.updatescreen import updateScreen
from widgets.button import Button
from game.utils import saving
from game.model.model import Model
from game.view.surfaces import pauseSurf

def pauseMenu(model: Model, backgroundBytes: bytes) -> None | Screens:
    buttonFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 36)
    buttonTextColour = (240, 240, 240)
    textShadow = (20, 20, 20, 160)
    
    buttonWidth, buttonHeight = 400, 50
    buttonX = (WIDTH - buttonWidth) // 2
    spacing = 75
    startY = HEIGHT // 2

    resumeButton = Button(buttonX, startY, buttonWidth, buttonHeight, "Back to Game")
    resetButton = Button(buttonX, startY + spacing, buttonWidth, buttonHeight, "Reset Game")
    quitButton = Button(buttonX, startY + spacing * 2, buttonWidth, buttonHeight, "Save and Quit")

    background = pg.image.frombytes(backgroundBytes, FRAME.size, 'RGBA')
    background = pg.transform.smoothscale(background, (FRAME.width // 15, FRAME.height // 15))
    background = pg.transform.smoothscale(background, FRAME.size)

    overlay = pg.Surface(FRAME.size, pg.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    background.blit(overlay, (0, 0))

    buttons = {
        'resume': resumeButton,
        'reset': resetButton,
        'quit': quitButton
    }

    while True:
        clearScreen()
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                saving.save(model)
                return Screens.QUIT

            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                for button in buttons.values():
                    button.handleEvent(event, mouse_pos)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if buttons['resume'].rect.collidepoint(mouse_pos):
                    return
                elif buttons['reset'].rect.collidepoint(mouse_pos):
                    saving.clear()
                    return Screens.MENU
                elif buttons['quit'].rect.collidepoint(mouse_pos):
                    saving.save(model)
                    return Screens.QUIT

        for button in buttons.values():
            button.update(mouse_pos)
            
        pauseSurf.blit(background, (0, 0))
        SURF.blit(pauseSurf, (0, 0))
        
        for button in buttons.values():
            button.draw(buttonFont, buttonTextColour, textShadow)

        updateScreen()