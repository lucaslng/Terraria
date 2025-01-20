import os
import dill
from game.model.model import Model

fileName = 'game/saves/saveFile'

def clear() -> None:
	try:
		os.remove(fileName)
	except FileNotFoundError:
		pass

def save(model: Model) -> None:
	'''Save the model to saveFile'''
	file = open(fileName, 'wb')
	dill.dump(model, file)
	file.close()

def load() -> Model | None:
	try:
		file = open(fileName, 'rb')
		model = dill.load(file)
		file.close()
		return model
	except FileNotFoundError:
		return None