from game.model.entity.entity import Entity
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.slot import Slot
from game.model.light import Light
from game.model.world import World
from sound import channels
from sound.sounds import sounds

class Player(Entity, Light):
    '''
    Player entity class with fall damage mechanics and inventory management.
    Overrides pathfinding behavior from Entity while maintaining other functionality.
    '''
    _heldSlotIndex = 0
    reach = 4
    inventory = Inventory(4, 9)
    helmetSlot = Slot()
    cursorSlot = Slot()
    defaultLightRadius = 0.8
    lightRadius = defaultLightRadius
    
    def __init__(self, x: float, y: float, world: World):
        super().__init__(x, y, 4, 1, 1, 20000, 7, 60, 20, 0.99, 18, world)
        
        #Fall damage
        self.lastVerticalVelo = 0
        self.fallDamageThreshold = 15
        self.fallDamageMultiplier = 0.8
        self.invulnerabilityFrames = 0   
    
    @property
    def hotbar(self) -> list[Slot]:
        '''Returns the hotbar, the first row of the player's inventory'''
        return self.inventory[0]
    
    @property
    def heldSlotIndex(self) -> int:
        return self._heldSlotIndex
    
    @heldSlotIndex.setter
    def heldSlotIndex(self, index: int) -> None:
        assert 0 <= index < self.inventory.cols  # raise error if index is not relevant
        if index != self._heldSlotIndex:
            self._heldSlotIndex = index
    
    @property
    def heldSlot(self) -> Slot:
        '''returns the held slot'''
        return self.hotbar[self._heldSlotIndex]
    
    @property
    def damage(self) -> int:
        '''returns the damage that the player does currently'''
        if self.heldSlot.item:
            return self.heldSlot.item.damage
        else:
            return 1
    
    def takeDamage(self, amount: int) -> bool:
        if super().takeDamage(amount):
            channels.playerHurt.play(sounds["player"]["hurt"])
            return True
        return False
    
    def consume(self) -> None:
        '''eat the item in the held slot'''
        self.health = min(self.maxHealth, self.health + self.heldSlot.item.healing)
        self.heldSlot.count -= 1
        if not self.heldSlot.count:
            self.heldSlot.clear()

    def update(self) -> None:
        '''Update player state including fall damage and light radius.'''       
        self.updateFallDamage()
        self.updateVerticalVelocityTime()
        #Update light radius based on held item
        if self.heldSlot.item and isinstance(self.heldSlot.item, Light):
            self.lightRadius = self.heldSlot.item.lightRadius
        else:
            self.lightRadius = self.defaultLightRadius