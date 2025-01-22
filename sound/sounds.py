from pygame.mixer import Sound

directory = 'assets/sounds'

def soundFactory(fileName: str, volume: float=0.6) -> Sound:
	sound = Sound(f'{directory}/{fileName}')
	sound.set_volume(volume)
	return sound

sounds = {
	"rpg":
	{
		"reload": soundFactory('rpg/reload.mp3', 0.55),
		"explosion": soundFactory('rpg/explosion.mp3', 0.55),
	},
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
			soundFactory('dog/growl/growl1.ogg', 0.4),
			soundFactory('dog/growl/growl2.ogg', 0.4),
			soundFactory('dog/growl/growl3.ogg', 0.4),
		)
	}
}
