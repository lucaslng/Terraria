from pygame import Rect, Surface
from pygame.font import Font


def drawText(surface: Surface, text: str, rect: Rect, font: Font, lineSpacing: int=-2, colour=(0, 0, 0)) -> None:
	'''wrap and draw text within a given rect'''

	fontHeight = font.get_height()
	y = rect.top

	while text:
		i = 1

		if y + fontHeight > rect.bottom: # y does not fit
			break

		while font.size(text[:i])[0] < rect.width and i < len(text): # determine characters in this line
			i += 1
		
		# if i < len(text):
		# 	i = text.rfind(" ", 0, i) + i # wrap to the last word (find the last space)
		
		image = font.render(text[:i], True, colour)
		surface.blit(image, (rect.left, y))

		y += fontHeight + lineSpacing
		
		text = text[i:]