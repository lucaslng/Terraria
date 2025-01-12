import utils.installpackages  # noqa: F401
from game.game import Game
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
				state = Game()
			case Screens.QUIT:
				sysexit()


if __name__ == '__main__':
	main()