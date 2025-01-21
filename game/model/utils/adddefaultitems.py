from game.model.entity.entities.player import Player
from game.model.items.craftingtableitem import CraftingTableItem
from game.model.items.helmets import DiamondHelmet, GoldHelmet, IronHelmet
from game.model.items.planksitem import PlanksItem
from game.model.items.rabbitmeat import RabbitMeat
from game.model.items.tools import DiamondAxe, DiamondPickaxe
from game.model.items.torchitem import TorchItem


def addDefaultItems(player: Player) -> None:
	'''Add default items to the player's inventory'''
	
	player.inventory.addItems(
		*[TorchItem() for _ in range(64)],
		*[RabbitMeat() for _ in range(64)],
		CraftingTableItem(),
		DiamondAxe(),
		DiamondPickaxe(),
		*[PlanksItem() for _ in range(64)],
		IronHelmet(),
		GoldHelmet(),
		DiamondHelmet(),
		)