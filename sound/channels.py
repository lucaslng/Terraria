from pygame.mixer import Channel

playerHurt = Channel(0)
playerHurt.set_volume(0.7)
consume = Channel(1)
consume.set_volume(0.7)

rabbitHurt = Channel(2)
rabbitHurt.set_volume(0.6)