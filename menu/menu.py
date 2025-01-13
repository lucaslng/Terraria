import math
import pygame as pg
import random

from constants import HEIGHT, SURF, WIDTH, clock
from screens import Screens
from menu.instructions.instructions import instructionsScreen
from menu.options.options import optionsScreen
from menu.splashtexts import splashTexts
from utils.updatescreen import updateScreen
from widgets.button import Button


def mainMenu():
	'''Main menu loop'''
	button_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 36)
	splash_font = pg.font.Font("MinecraftRegular-Bmg3.otf", 28)
	button_text_colour = (240, 240, 240)
	text_shadow = (20, 20, 20, 160)

	bg_panorama = pg.image.load("title screen background animation.jpg").convert()
	overlay = pg.Surface((WIDTH, HEIGHT))
	overlay.fill((0, 0, 0))
	overlay.set_alpha(40)

	title_image = pg.image.load("title screen title.png").convert_alpha()
	title_image_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))

	current_splash = random.choice(splashTexts)
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

	while True:
		dt = clock.get_time() / 1000.0  #delta time in seconds
		mouse_pos = pg.mouse.get_pos()

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT

			if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
				for button in buttons.values():
					button.handle_event(event, mouse_pos)

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

		bg_offset = (bg_offset + bg_scroll_speed * dt) % bg_panorama.get_width()

		#Draw background
		SURF.blit(bg_panorama, (-bg_offset, 0))
		SURF.blit(bg_panorama, (bg_panorama.get_width() - bg_offset, 0))
		SURF.blit(overlay, (0, 0))

		SURF.blit(title_image, title_image_rect)

		#Draw splash text
		splash_wave_offset += dt
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

		updateScreen()