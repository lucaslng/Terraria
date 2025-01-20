from math import dist
import time

from game.model.entity.hasphysics import HasPhysics
from game.model.items.item import Item
from game.model.world import World

from sound import channels

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
        self.updateDistance: int | None = None
        self.pathFindToPlayer = True
        self.droppedItem: Item | None = None

        self.lastVerticalVelocity = 0
        self.fallDamageThreshold = 15  		    #Minimum velocity to start taking damage
        self.fallDamageMultiplier = 0.8  	    #Damage per unit of excess velocity
        self.invulnerabilityFrames = 0
        self.invulnerabilityDuration = 10    #How long entity stays invulnerable after taking damage
        
        self.noVerticalVelocityTime = 0

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

    def updateVerticalVelocityTime(self) -> None:
        '''update the vertical velocity time'''
        if -0.01 < self.velocity.y < 0.01:
            self.noVerticalVelocityTime += 1
        else:
            self.noVerticalVelocityTime = 0

    @property
    def isOnGround(self) -> bool:
        return self.noVerticalVelocityTime > 1

    @property
    def isAlive(self) -> bool:
        return self.health > 0
    
    def takeDamage(self, amount: int) -> bool:
        '''Damage entity if not invulnerable. returns whether the entity actually took damage or did not due to invulnerability frames'''       
        if self.invulnerabilityFrames == 0:
            self.health = max(0, self.health - amount)
            self.invulnerabilityFrames = self.invulnerabilityDuration
            return True
        return False
        
    def updateFallDamage(self) -> bool:
        '''Handle fall damage logic. returns true or false depending on whether fall damage was taken'''
        tookDamage = False
        currentVelo = self.velocity.y
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
            if dist(self.position, goal) < self.updateDistance:
                x, y = map(int, self.position)
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