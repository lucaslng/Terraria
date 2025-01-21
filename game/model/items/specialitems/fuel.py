from dataclasses import dataclass


@dataclass
class Fuel:
    '''Items that can be used as fuel in furnaces'''

    burnTime: int              # How many game ticks this fuel burns for
    heatOutput: float          # Multiplier for burn effectiveness (1.0 is standard)
    
    def __post_init__(self):
        self.initialBurnTime = self.burnTime