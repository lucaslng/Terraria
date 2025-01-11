from utils.installpackages import installPackages
installPackages()

from game.game import Game  # noqa: E402
from game.utils.utils import sysexit  # noqa: E402
from menu.menu import MainMenu  # noqa: E402
from screens import Screens  # noqa: E402
from initialize import initialize  # noqa: E402



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