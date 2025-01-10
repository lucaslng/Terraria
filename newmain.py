from game.game import game
from game.utils.utils import sysexit
from menu.menu import MainMenu
from screens import Screens
from initialize import initialize


def main():
	'''Main loop'''

	initialize()

	state = Screens.MENU

	while True:
		match state:
			case Screens.MENU:
				state = MainMenu()
			case Screens.GAME:
				state = game()
			case Screens.QUIT:
				sysexit()


main()