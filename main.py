import utils.installpackages
from menu.about.about import aboutScreen
from menu.gameOver.deathScreen import deathScreen
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
			case Screens.DEATH:
				state = deathScreen()
			case Screens.QUIT:
				sysexit()


if __name__ == '__main__':
	main()