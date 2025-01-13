import utils.installpackages  # noqa: F401
from game.game import game
from game.utils.utils import sysexit
from menu.menu import mainMenu
from screens import Screens
from initialize import initialize


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
			case Screens.QUIT:
				sysexit()


if __name__ == '__main__':
	main()