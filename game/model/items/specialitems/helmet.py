class Helmet:
	'''Helmet item that can be worn to give protection'''

	multiplier: float
	startingDurability: int
	
	def __init__(self):
		self.durability = self.startingDurability