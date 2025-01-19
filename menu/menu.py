import math
import pygame as pg
import random

from utils.constants import HEIGHT, SURF, WIDTH, clock
from utils.screens import Screens
from menu.instructions.instructions import instructionsScreen
from menu.options.options import optionsScreen
from menu.splashtexts import splashTexts
from utils.updatescreen import updateScreen
from widgets.button import Button


def mainMenu():
	'''Main menu loop'''
	buttonFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 36)
	splashFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 28)
	buttonTextColour = (240, 240, 240)
	textShadow = (20, 20, 20, 160)

	bgPanorama = pg.image.load("assets/title screen background animation.jpg").convert()
	overlay = pg.Surface((WIDTH, HEIGHT))
	overlay.fill((0, 0, 0))
	overlay.set_alpha(40)

	titleImage = pg.image.load("assets/title screen title.png").convert_alpha()
	titleImageRect = titleImage.get_rect(center=(WIDTH // 2, HEIGHT // 4))

	currentSplash = random.choice(splashTexts)
	splashAngle = -15
	splashWaveOffset = 0
	splashScale = 1.0

	buttonWidth, buttonHeight = 400, 50
	buttonX = (WIDTH - buttonWidth) // 2
	spacing = 24
	startY = HEIGHT // 2

	buttons = {
		'play': Button(buttonX, startY, buttonWidth, buttonHeight, "Play"),
		'instructions': Button(buttonX, startY + buttonHeight + spacing, buttonWidth, buttonHeight, "Instructions"),
		'options': Button(buttonX, startY + (buttonHeight + spacing) * 2, buttonWidth, buttonHeight, "Options"),
		'quit': Button(buttonX, startY + (buttonHeight + spacing) * 3, buttonWidth, buttonHeight, "Quit"),
	}

	bgScrollSpeed = 20
	bgOffset = 0

	while True:
		dt = clock.get_time() / 1000.0  #delta time in seconds
		mouse_pos = pg.mouse.get_pos()

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT

			if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
				for button in buttons.values():
					button.handleEvent(event, mouse_pos)

			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				if buttons['play'].rect.collidepoint(mouse_pos):
					return Screens.GAME
				elif buttons['instructions'].rect.collidepoint(mouse_pos):
					return instructionsScreen()
				elif buttons['options'].rect.collidepoint(mouse_pos):
					# return optionsScreen()
					pass
				elif buttons['quit'].rect.collidepoint(mouse_pos):
					return Screens.QUIT

		for button in buttons.values():
			button.update(mouse_pos)

		bgOffset = (bgOffset + bgScrollSpeed * dt) % bgPanorama.get_width()

		#Draw background
		SURF.blit(bgPanorama, (-bgOffset, 0))
		SURF.blit(bgPanorama, (bgPanorama.get_width() - bgOffset, 0))
		SURF.blit(overlay, (0, 0))

		SURF.blit(titleImage, titleImageRect)

		#Draw splash text
		splashWaveOffset += dt
		splashScale = 1.0 + math.sin(splashWaveOffset * 0.5) * 0.03

		splashSurf = splashFont.render(currentSplash, True, (255, 255, 0))
		splashSurf = pg.transform.rotate(splashSurf, splashAngle)
		splashSurf = pg.transform.scale(splashSurf, (int(splashSurf.get_width() * splashScale), int(splashSurf.get_height() * splashScale)))

		splashYOffset = math.sin(splashWaveOffset) * 6
		splashPos = (WIDTH // 2 + 180, HEIGHT // 4 + splashYOffset)
		SURF.blit(splashSurf, splashPos)

		#Draw buttons
		for button in buttons.values():
			button.draw(buttonFont, buttonTextColour, textShadow)

		updateScreen()