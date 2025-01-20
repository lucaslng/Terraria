import os
import dill
from game.model.model import Model

saveDirectory = 'game/saves'
saveFile = 'saveFile'
savePath = os.path.join(saveDirectory, saveFile)

def ensureSaveDirectory() -> None:
    '''Creates the saves directory if it doesn't exist'''
    os.makedirs(saveDirectory, exist_ok=True)

def clear() -> None:
	'''Removes the save file if it existsa'''
	try:
		os.remove(savePath)
		print("Clearing save...")
	except FileNotFoundError:
		pass

def save(model: Model) -> None:
	'''Saves game data to the file'''
	ensureSaveDirectory()
	with open(savePath, 'wb') as file:
		dill.dump(model, file)

def load() -> Model | None:
	'''Loads from the save file'''
	try:
		with open(savePath, 'rb') as file:
			return dill.load(file)
	except FileNotFoundError:
		return None