from game.model.entity.entity import Entity
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.slot import Slot
from game.model.light import Light
from game.model.world import World

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

        self.updateDistance = None
        self.pathFindToPlayer = False
        
        #Fall damage
        self.last_vertical_velocity = 0
        self.fall_damage_threshold = 15
        self.fall_damage_multiplier = 0.8
        self.invulnerability_frames = 0   
    
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
    
    def consume(self) -> None:
        '''eat the item in the held slot'''
        self.health = min(self.maxHealth, self.health + self.heldSlot.item.healing)
        self.heldSlot.count -= 1
        if not self.heldSlot.count:
            self.heldSlot.clear()

    def update(self, goal: tuple[float, float] = None) -> None:
        '''Update player state including fall damage and light radius.'''

        current_velocity = self.velocity.y
        if (
            self.last_vertical_velocity > self.fall_damage_threshold
            and abs(current_velocity) < self.fall_damage_threshold * 0.5
            and self.invulnerability_frames == 0
        ):
            excess_velocity = self.last_vertical_velocity - self.fall_damage_threshold
            damage = int(excess_velocity * self.fall_damage_multiplier)
            self.takeDamage(damage)
            self.invulnerability_frames = 10

        self.last_vertical_velocity = current_velocity
        if self.invulnerability_frames > 0:
            self.invulnerability_frames -= 1
            
        #Update light radius based on held item
        if self.heldSlot.item and isinstance(self.heldSlot.item, Light):
            self.lightRadius = self.heldSlot.item.lightRadius
        else:
            self.lightRadius = self.defaultLightRadius