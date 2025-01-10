from dataclasses import dataclass

from main import Player, World


@dataclass
class GameState:
  world: World
  player: Player