from game.game import game
from game.utils.utils import sysexit
from menu.menu import menu
from screens import Screens
from initialize import initialize


def main():
	'''Main loop'''

	initialize()

	state = Screens.MENU

	while True:
		match state:
			case Screens.MENU:
				state = menu()
			case Screens.GAME:
				state = game()
			case Screens.QUIT:
				sysexit()


main()