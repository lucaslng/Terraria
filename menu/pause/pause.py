import pygame as pg
from utils.constants import WIDTH, HEIGHT, SURF, FPS, FRAME
from utils.screens import Screens
from widgets.button import Button
from game.utils import saving
from game.model.model import Model


def pauseMenu(model: Model) -> None | Screens:
    buttonFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 36)
    buttonTextColour = (240, 240, 240)
    textShadow = (20, 20, 20, 160)

    resumeButton = Button((WIDTH - 400) // 2, HEIGHT // 2, 400, 50, "Back to Game")
    resetButton = Button((WIDTH - 400) // 2, (HEIGHT // 2) + 75, 400, 50, "Reset Game")
    quitButton = Button((WIDTH - 400) // 2, (HEIGHT // 2) + 150, 400, 50, "Save and Quit")
    
    blurScale = 0.1    #lower is blurrier
    small_size = (int(WIDTH * blurScale), int(HEIGHT* blurScale))
    small_surface = pg.transform.smoothscale(SURF, small_size)
    blurred_surface = pg.transform.smoothscale(small_surface, (WIDTH, HEIGHT))

    buttons = {
        'resume': resumeButton,
        'reset': resetButton,
        'quit': quitButton
    }

    clock = pg.time.Clock()
    while True:
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

        SURF.blit(blurred_surface, (0, 0))
        
        for button in buttons.values():
            button.draw(buttonFont, buttonTextColour, textShadow)

        pg.display.flip()
        clock.tick(FPS)