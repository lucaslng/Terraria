from math import ceil, dist, floor
import time
from game.model.entity.hasphysics import HasPhysics
from game.model.items.item import Item
from game.model.world import World


class Entity(HasPhysics):
    '''Base class for all entities'''
    def __init__(
        self,
        x: float,
        y: float,
        mass: float,
        width: float,
        height: float,
        walkForce: float,
        walkSpeed: float,
        jumpImpulse: float,
        jumpSpeed: float,
        friction: float,
        maxHealth: int,
        world: World,
    ):
        super().__init__(x, y, mass, width, height)
        
        self.walkForce = walkForce
        self.walkSpeed = walkSpeed
        self.jumpImpulse = jumpImpulse
        self.jumpSpeed = jumpSpeed
        self.previousJumpTime = 0
        self.friction = friction
        self.maxHealth = maxHealth
        self.health = maxHealth
        self.world = world
        self.minyvelo = 100
        self.updateDistance = 1
        self.pathFindToPlayer = True
        self.droppedItem: Item | None = None

        self.lastVerticalVelocity = 0
        self.fallDamageThreshold = 15  		#Minimum velocity to start taking damage
        self.fallDamageMultiplier = 0.8  	#Damage per unit of excess velocity
        self.invulnerabilityFrames = 0

    def walkLeft(self) -> None:
        '''Walk the entity to the left using walkForce'''
        if -self.velocity.x < self.walkSpeed:
            self.apply_force_at_local_point((-self.walkForce, 0))

    def walkRight(self) -> None:
        '''Walk the entity to the right using walkForce'''
        if self.velocity.x < self.walkSpeed:
            self.apply_force_at_local_point((self.walkForce, 0))

    def jump(self) -> None:
        '''Jump the entity using jumpForce'''
        if self.isOnGround and time.time() - self.previousJumpTime > 0.1:
            self.apply_impulse_at_local_point((0, -self.jumpImpulse))
            self.previousJumpTime = time.time()

    @property
    def isOnGround(self) -> bool:
        if ceil(self.position.y) == self.world.height:
            return True
        if (self.position.y - self.height / 2) % 1 < 0.05: # at the bottom of a possibly empty block
            return (not self.world[ceil(self.position.y)][floor(self.position.x)].isEmpty) or (not self.world[ceil(self.position.y)][ceil(self.position.x)].isEmpty)
        return False

    @property
    def isAlive(self) -> bool:
        return self.health > 0
    
    def takeDamage(self, amount: int) -> None:
        '''Apply damage to the entity'''
        self.health = max(0, self.health - amount)

    def update(self, goal: tuple[float, float]) -> None:
        current_velocity = self.velocity.y
        if (
            self.lastVerticalVelocity > self.fallDamageThreshold
            and abs(current_velocity) < self.fallDamageThreshold * 0.5
            and self.invulnerabilityFrames == 0
        ):
            excess_velocity = self.lastVerticalVelocity - self.fallDamageThreshold
            damage = int(excess_velocity * self.fallDamageMultiplier)
            self.takeDamage(damage)
            self.invulnerabilityFrames = 10

        self.lastVerticalVelocity = current_velocity
        if self.invulnerabilityFrames > 0:
            self.invulnerabilityFrames -= 1

        #Pathfinding logic
        if dist(self.position, goal) > self.updateDistance:
            x, y = map(int, self.position)
            reachables = {(x, y)}
            if self.world[y][x - 1].isEmpty:
                reachables.add((x - 1, y))
            if self.world[y][x + 1].isEmpty:
                reachables.add((x + 1, y))
            best = min(reachables, key=lambda p: dist(p, goal)) if self.pathFindToPlayer else max(reachables, key=lambda p: dist(p, goal))
            if best != (x, y):
                if best[0] < x:
                    self.walkLeft()
                else:
                    self.walkRight()

    def interact(self) -> None:
        '''Interact with the entity using the interact key'''
        pass