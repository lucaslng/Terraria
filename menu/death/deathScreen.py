import pygame as pg
from utils.clearscreen import clearScreen
from utils.constants import FRAME, HEIGHT, SURF, WIDTH
from utils.screens import Screens
from utils.updatescreen import updateScreen
from widgets.button import Button
from game.view.surfaces import deathSurf

def deathScreen(backgroundBytes: bytes) -> Screens:  
    titleFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 48)
    buttonFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 36)
    
    buttonTextColour = (240, 240, 240)
    textShadow = (20, 20, 20, 160)
    titleColour = (255, 0, 0)
    
    background = pg.image.frombytes(backgroundBytes, FRAME.size, 'RGB')
    background = pg.transform.smoothscale(background, (FRAME.width // 15, FRAME.height // 15))
    background = pg.transform.smoothscale(background, FRAME.size)

    overlay = pg.Surface(FRAME.size, pg.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    background.blit(overlay, (0, 0))
    
    buttonWidth, buttonHeight = 400, 50
    buttonX = (WIDTH - buttonWidth) // 2
    spacing = 24
    startY = HEIGHT // 2
    
    buttons = {
        'menu': Button(buttonX, startY + spacing, buttonWidth, buttonHeight, "Return to Menu"),
        'quit': Button(buttonX, startY + buttonHeight + spacing * 2, buttonWidth, buttonHeight, "Quit Game")
    }
    
    while True:
        clearScreen()
        mouse_pos = pg.mouse.get_pos()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return Screens.QUIT
                
            if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                for button in buttons.values():
                    button.handleEvent(event, mouse_pos)
                    
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if buttons['menu'].rect.collidepoint(mouse_pos):
                    return Screens.MENU
                elif buttons['quit'].rect.collidepoint(mouse_pos):
                    return Screens.QUIT
        
        for button in buttons.values():
            button.update(mouse_pos)
        
        deathSurf.blit(background, (0, 0))
        
        gameOverText = titleFont.render("Game Over!", True, titleColour)
        textRect = gameOverText.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        deathSurf.blit(gameOverText, textRect)
        
        SURF.blit(deathSurf, (0, 0))
        
        for button in buttons.values():
            button.draw(buttonFont, buttonTextColour, textShadow)
            
        updateScreen()