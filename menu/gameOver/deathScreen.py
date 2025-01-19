import pygame as pg
from utils.constants import HEIGHT, SURF, WIDTH
from utils.screens import Screens
from utils.updatescreen import updateScreen
from widgets.button import Button

def deathScreen():
    '''Death screen for when the player dies'''
    
    titleFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 48)
    buttonFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 36)
    
    buttonTextColour = (240, 240, 240)
    textShadow = (20, 20, 20, 160)
    titleColor = (255, 0, 0)
    
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    
    buttonWidth, buttonHeight = 400, 50
    buttonX = (WIDTH - buttonWidth) // 2
    spacing = 24
    startY = HEIGHT // 2
    
    buttons = {
        'menu': Button(buttonX, startY + spacing, buttonWidth, buttonHeight, "Return to Menu"),
        'quit': Button(buttonX, startY + buttonHeight + spacing * 2, buttonWidth, buttonHeight, "Quit Game")
    }
    
    while True:
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
        
        SURF.blit(overlay, (0, 0))
        
        gameOverText = titleFont.render("Game Over!", True, titleColor)
        textRect = gameOverText.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        SURF.blit(gameOverText, textRect)
        
        for button in buttons.values():
            button.draw(buttonFont, buttonTextColour, textShadow)
        
        updateScreen()