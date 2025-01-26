from game.model.entity.entities.player import Player
from game.model.items.bucket import Bucket
from game.model.items.cobblestoneitem import CobblestoneItem
from game.model.items.craftingtableitem import CraftingTableItem
from game.model.items.dirtitem import DirtItem
from game.model.items.flowers import AlliumItem, CornflowerItem, DandelionItem, PoppyItem
from game.model.items.furnaceitem import FurnaceItem
from game.model.items.helmets import DiamondHelmet, GoldHelmet, IronHelmet
from game.model.items.ingots import CoalItem, DiamondItem, GoldIngotItem, IronIngotItem
from game.model.items.logitem import LogItem
from game.model.items.ores import GoldOreItem, IronOreItem
from game.model.items.planksitem import PlanksItem
from game.model.items.rabbitmeat import RabbitMeat
from game.model.items.rpg import Rpg
from game.model.items.sticksitem import SticksItem
from game.model.items.tools import DiamondSword, GoldPickaxe, IronAxe, StoneShovel
from game.model.items.torchitem import TorchItem
from game.model.liquids.liquid import Water


def add_default_items(player: Player) -> None:
	'''Add default items to the player's inventory'''
	
	player.inventory.addItems(
		DiamondSword(),
		GoldPickaxe(),
		IronAxe(),
		StoneShovel(),
		Rpg(),
		*[TorchItem() for _ in range(64)],
		*[RabbitMeat() for _ in range(64)],
		CraftingTableItem(),
		*[PlanksItem() for _ in range(64)],
		*[Bucket(liquid=Water, filledAmount=1) for _ in range(5)],
		DiamondHelmet(),
		GoldHelmet(),
		IronHelmet(),
		FurnaceItem(),
		*[CoalItem() for _ in range(64)],
		*[IronOreItem() for _ in range(64)],
		*[GoldOreItem() for _ in range(64)],
		*[GoldIngotItem() for _ in range(64)],
		*[DiamondItem() for _ in range(64)],
		*[IronIngotItem() for _ in range(64)],
		*[CobblestoneItem() for _ in range(64)],
		*[PoppyItem() for _ in range(64)],
		# *[CornflowerItem() for _ in range(64)],
		# *[DandelionItem() for _ in range(64)],
		# *[AlliumItem() for _ in range(64)],
		# *[LogItem() for _ in range(64)],
		# *[SticksItem() for _ in range(64)],
		*[Bucket() for _ in range(2)],
		# *[DirtItem() for _ in range(64)],
		)