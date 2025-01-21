from math import dist
import time

from pymunk import Space

from game.model.entity.hasphysics import HasPhysics
from game.model.items.item import Item
from game.model.world import World
from utils.constants import BIG

class Entity(HasPhysics):
    invulnerabilityDuration: int = 10 # How long entity stays invulnerable after taking damage
    fallDamageMultiplier: float = 0.8  	    #Damage per unit of excess velocity
    fallDamageThreshold: int = 15  	
    mass: float	    #Minimum velocity to start taking damage
    width: float = 1
    height: float = 1
    walkForce: float = 800
    walkSpeed: float
    jumpImpulse: float
    jumpSpeed: float
    friction: float = 0.99
    maxHealth: int
    miniyvelo: int = 100
    updateDistance: int | None = None
    pathFindToPlayer: bool = True
    droppedItem: Item | None = None

    '''Base class for all entities'''
    def __init__(self, x: float, y: float, world: World, space: Space):
        super().__init__(x, y, self.mass, self.friction, self.width, self.height, space)
        self.world = world
        self.lastVerticalVelocity = 0
        self.invulnerabilityFrames = 0
        self.noVerticalVelocityTime = 0
        self.health = self.maxHealth
        self.previousJumpTime = 0

    def walkLeft(self) -> None:
        '''Walk the entity to the left using walkForce'''
        if -self.body.velocity.x < self.walkSpeed:
            self.body.apply_force_at_local_point((-self.walkForce, 0))

    def walkRight(self) -> None:
        '''Walk the entity to the right using walkForce'''
        if self.body.velocity.x < self.walkSpeed:
            self.body.apply_force_at_local_point((self.walkForce, 0))

    def jump(self) -> None:
        '''Jump the entity using jumpForce'''
        if self.isOnGround and time.time() - self.previousJumpTime > 0.1:
            self.body.apply_impulse_at_local_point((0, -self.jumpImpulse))
            self.previousJumpTime = time.time()

    def updateVerticalVelocityTime(self) -> None:
        '''update the vertical velocity time'''
        if -0.01 < self.body.velocity.y < 0.01:
            self.noVerticalVelocityTime += 1
        else:
            self.noVerticalVelocityTime = 0

    @property
    def isOnGround(self) -> bool:
        return self.noVerticalVelocityTime > 1

    @property
    def isAlive(self) -> bool:
        return self.health > 0
    
    def takeDamage(self, amount: float) -> bool:
        '''Damage entity if not invulnerable. returns whether the entity actually took damage or did not due to invulnerability frames'''       
        if self.invulnerabilityFrames == 0:
            self.health = max(0, self.health - amount)
            self.invulnerabilityFrames = self.invulnerabilityDuration
            return True
        return False
        
    def updateFallDamage(self) -> bool:
        '''Handle fall damage logic. returns true or false depending on whether fall damage was taken'''
        tookDamage = False
        currentVelo = self.body.velocity.y
        if (self.lastVerticalVelocity > self.fallDamageThreshold and abs(currentVelo) < self.fallDamageThreshold * 0.5):
            excessVelo = self.lastVerticalVelocity - self.fallDamageThreshold
            damage = int(excessVelo * self.fallDamageMultiplier)
            tookDamage = self.takeDamage(damage)

        self.lastVerticalVelocity = currentVelo
        
        if self.invulnerabilityFrames > 0:
            self.invulnerabilityFrames -= 1
        return tookDamage

    def update(self, goal: tuple[float, float]) -> None:
        '''Update entity state'''      
        self.updateVerticalVelocityTime()
        if self.updateDistance is not None:
            if dist(self.body.position, goal) < self.updateDistance:
                x, y = map(int, self.body.position)
                if 0 <= x < self.world.width - 1 and 0 <= y < self.world.height - 1:
                    reachables = {(x, y)}
                    if x > 0 and self.world[y][x - 1].isEmpty:
                        reachables.add((x - 1, y))
                    if x < self.world.width - 2 and self.world[y][x + 1].isEmpty:
                        reachables.add((x + 1, y))
                    best = min(reachables, key=lambda p: dist(p, goal)) if self.pathFindToPlayer else max(reachables, key=lambda p: dist(p, goal))
                    if best != (x, y):
                        bestx, besty = best
                        if bestx < x:
                            if 0 <= bestx - 1 and (not self.world[besty][bestx - 2].isEmpty or not self.world[besty][bestx - 1].isEmpty):
                                self.jump()
                            self.walkLeft()
                        else:
                            if bestx + 1 < self.world.width and (not self.world[besty][bestx - 2].isEmpty or not self.world[besty][bestx - 1].isEmpty):
                                self.jump()
                            self.walkRight()

    def interact(self) -> bool:
        '''Interact with the entity using the interact key'''
        return False