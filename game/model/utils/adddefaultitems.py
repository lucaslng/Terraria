from game.model.entity.entities.player import Player
from game.model.items.bucket import Bucket
from game.model.items.craftingtableitem import CraftingTableItem
from game.model.items.flowers import PoppyItem
from game.model.items.furnaceitem import FurnaceItem
from game.model.items.helmets import DiamondHelmet, GoldHelmet, IronHelmet
from game.model.items.ingots import CoalItem
from game.model.items.ores import IronOreItem
from game.model.items.planksitem import PlanksItem
from game.model.items.rabbitmeat import RabbitMeat
from game.model.items.rpg import Rpg
from game.model.items.tools import DiamondAxe, DiamondPickaxe
from game.model.items.torchitem import TorchItem
from game.model.liquids.liquid import Water


def addDefaultItems(player: Player) -> None:
	'''Add default items to the player's inventory'''
	
	player.inventory.addItems(
		*[TorchItem() for _ in range(64)],
		*[RabbitMeat() for _ in range(64)],
		CraftingTableItem(),
		DiamondPickaxe(),
		*[PlanksItem() for _ in range(64)],
		Bucket(liquid=Water, filledAmount=1),
		Rpg(),
		DiamondHelmet(),
		FurnaceItem(),
		*[CoalItem() for _ in range(64)],
		*[IronOreItem() for _ in range(8)]
		)