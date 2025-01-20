from pygame.mixer import Sound

directory = 'assets/sounds'

def soundFactory(fileName: str) -> Sound:
	sound = Sound(f'{directory}/{fileName}')
	sound.set_volume(0.6)
	return sound

sounds = {
	"player":
	{
		"hurt": soundFactory('player/hurt.mp3'),
		"consume": soundFactory('player/consume.mp3'),
	},
	"rabbit":
	{
		"hurt":
		(
			soundFactory('rabbit/hurt1.ogg'),
			soundFactory('rabbit/hurt2.ogg'),
			soundFactory('rabbit/hurt3.ogg'),
			soundFactory('rabbit/hurt4.ogg'),
		)
	},
	"dog":
	{
		"hurt":
		(
			soundFactory('dog/hurt/hurt1.ogg'),
			soundFactory('dog/hurt/hurt2.ogg'),
		),
		"growl":
		(
			soundFactory('dog/growl/growl1.ogg'),
			soundFactory('dog/growl/growl2.ogg'),
			soundFactory('dog/growl/growl3.ogg'),
		)
	}
}
