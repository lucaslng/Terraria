'''
TerraCraft
A game where you explore the world and defend yourself against monsaters!
By Lucas Leung and Ryan Cheung
20th January 2025
'''

import utils.installpackages
from menu.about.about import aboutScreen
from game.game import game
from game.utils.utils import sysexit
from menu.menu import mainMenu
from utils.screens import Screens
from utils.initialize import initialize


def main():
	'''Main loop'''
	
	initialize()

	state = Screens.MENU

	while True:
		match state:
			case Screens.MENU:
				state = mainMenu()
			case Screens.GAME:
				state = game()
			case Screens.ABOUT:
				state = aboutScreen()
			case Screens.QUIT:
				sysexit()


if __name__ == '__main__':
	main()