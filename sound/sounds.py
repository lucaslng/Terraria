from pygame.mixer import Sound

directory = 'assets/sounds'

sounds = {
	"player":
	{
		"hurt": Sound(f'{directory}/player/hurt.mp3'),
		"consume": Sound(f'{directory}/player/consume.mp3'),
	},
	"rabbit":
	{
		"hurt":
		(
			Sound(f'{directory}/rabbit/hurt1.ogg'),
			Sound(f'{directory}/rabbit/hurt2.ogg'),
			Sound(f'{directory}/rabbit/hurt3.ogg'),
			Sound(f'{directory}/rabbit/hurt4.ogg'),
		)
	},
}
