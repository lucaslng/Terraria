import pygame as pg, math, random, threading

from customqueue import Queue
from constants import *
from blocks import *
from sprites import *
from utils.direction import direction
from utils.utils import *
from entities import *
from menus import LoadingScreen


player = Player()


@dataclass
class Edge:
  x: int
  y: int
  ex: int
  ey: int
  
  def draw(self):
    # if self.x != self.ex and self.y != self.ey: print("diagonal wtf")
    pg.draw.line(SURF,(0,0,0),relativeCoord(self.x*BLOCK_SIZE, self.y*BLOCK_SIZE),relativeCoord(self.ex*BLOCK_SIZE, self.ey*BLOCK_SIZE), 3)
    # pg.draw.circle(SURF,(0,255,0),relativeCoord(self.x*BLOCK_SIZE,self.y*BLOCK_SIZE), 3)
    # pg.draw.circle(SURF,(0,255,0),relativeCoord(self.ex*BLOCK_SIZE,self.ey*BLOCK_SIZE), 3)
  def __repr__(self):
    return str((self.x, self.y, self.ex, self.ey))

class ProgressTracker:
    def __init__(self, callback):
        self.callback = callback
        self.current_step = ""
        
    def update(self, step: str, progress: float):
        self.current_step = str(step)
        self.callback(self.current_step, progress)

class World:
  def __init__(self, progress_tracker=None):
    self.progress_tracker = progress_tracker
    self.progress_tracker.update("Generating terrain noise...", 0.0)
    
    self.array = [
        [AirBlock(x, y) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    
    #cannot deepcopy pygame surface so I have to loop over it again
    self.back = [
        [AirBlock(x, y, isBack=True) for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)
    ]
    
    self.mask = pg.mask.Mask((WORLD_WIDTH*BLOCK_SIZE, WORLD_HEIGHT*BLOCK_SIZE))
    self.lightmap = [
        [0 for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)]

    self.generateWorld()
    self.generateLight()

  class SimplexNoise:
    def __init__(self, scale: float, dimension: int, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT):
      if dimension == 1:
        self.noise = self.__noise1d(width, scale)
      elif dimension == 2:
        self.noise = self.__noise2d(width, height, scale)
      else:
        return None

    def __getitem__(self, x: int):
      return self.noise[x]

    @staticmethod
    def __fade(t):
      return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def __generatePermutation():
      random.seed(random.randint(0, BIG))
      p = list(range(256))
      random.shuffle(p)
      random.seed(SEED)
      return p + p  # Double for wraparound

    @staticmethod
    def __gradient1d(h):
      return 1 if h % 2 == 0 else -1

    @staticmethod
    def __gradient2d(h):
      """Compute 2D gradient direction based on hash value."""
      directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
      return directions[h % 4]

    def __noise1d(self, width, scale=1.0):
      perm = self.__generatePermutation()
      noise = []

      for i in range(width):
        x = i / scale
        x0 = math.floor(x)
        x1 = x0 + 1

        dx0 = x - x0
        dx1 = x - x1

        u = self.__fade(dx0)

        g0 = self.__gradient1d(perm[x0 % 256])
        g1 = self.__gradient1d(perm[x1 % 256])

        n0 = g0 * dx0
        n1 = g1 * dx1

        value = pg.math.lerp(n0, n1, u)
        noise.append(value)

      return noise

    def __noise2d(self, width, height, scale=1.0):
      perm = self.__generatePermutation()
      noise = []

      for y in range(height):
        row = []
        for x in range(width):
          sx = x / scale
          sy = y / scale

          x0 = math.floor(sx)
          y0 = math.floor(sy)

          x1 = x0 + 1
          y1 = y0 + 1

          dx0 = sx - x0
          dy0 = sy - y0
          dx1 = sx - x1
          dy1 = sy - y1

          u = self.__fade(dx0)
          v = self.__fade(dy0)

          g00 = self.__gradient2d(perm[(x0 + perm[y0 % 256]) % 256])
          g10 = self.__gradient2d(perm[(x1 + perm[y0 % 256]) % 256])
          g01 = self.__gradient2d(perm[(x0 + perm[y1 % 256]) % 256])
          g11 = self.__gradient2d(perm[(x1 + perm[y1 % 256]) % 256])

          n00 = g00[0] * dx0 + g00[1] * dy0
          n10 = g10[0] * dx1 + g10[1] * dy0
          n01 = g01[0] * dx0 + g01[1] * dy1
          n11 = g11[0] * dx1 + g11[1] * dy1

          nx0 = pg.math.lerp(n00, n10, u)
          nx1 = pg.math.lerp(n01, n11, u)

          value = pg.math.lerp(nx0, nx1, v)
          row.append(value)
        noise.append(row)

      return noise


  def generateWorld(self):
    phases = {
            'noise': 0.1,
            'terrain': 0.3,
            'caves': 0.2,
            'ores': 0.2, 
            'trees': 0.2
        }
    
    # Precompute noise
    grassHeightNoise = self.SimplexNoise(19, 1)
    stoneHeightNoise = self.SimplexNoise(30, 1)
    cavesNoise = self.SimplexNoise(9, 2)

    oresNoise = {
      ore.__name__: (self.SimplexNoise(ore.veinSize, 2), ore)
      for ore in ores
    }
    
    baseProgress = 0.0        
    if self.progress_tracker:
        baseProgress = phases['noise']
        self.progress_tracker.update("Creating base terrain...", baseProgress)

    # Generate terrain in batch
    for x in range(WORLD_WIDTH):     
      if self.progress_tracker and x % (WORLD_WIDTH // 20) == 0:
            terrain_progress = (x / WORLD_WIDTH) * phases['terrain']
            total_progress = min(baseProgress + terrain_progress, 1.0)
            self.progress_tracker.update("Creating base terrain...", total_progress)
      
      grassHeight = round(WORLD_HEIGHT * 0.58 + 9 * grassHeightNoise[x])
      stoneHeight = round(grassHeight + 5 + 5 * stoneHeightNoise[x])

      # Stone and Dirt pass in batch
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, -1):
          if y > stoneHeight:
              self.array[y][x] = StoneBlock(x, y)
              self.back[y][x] = StoneBlock(x, y, isBack=True)
          else:
              self.array[y][x] = DirtBlock(x, y)
              self.back[y][x] = DirtBlock(x, y, isBack=True)

      # Grass block
      self[grassHeight][x] = DirtBlock(
          x, grassHeight, DirtVariantGrass()
      )
      
      baseProgress += phases["terrain"]

      #Cave pass
      for y in range(WORLD_HEIGHT - 1, grassHeight - 1, -1):         
          if self.progress_tracker and x % (WORLD_WIDTH // 20) == 0:
            cave_progress = (x / WORLD_WIDTH) * phases['caves']
            total_progress = min(baseProgress + cave_progress, 1.0)
            self.progress_tracker.update("Carving caves...", total_progress)
          
          if cavesNoise[y][x] > 0.1:
              self.array[y][x] = AirBlock(x, y)

      baseProgress += phases['caves']
          
      #Ore pass
      total_ores = len(oresNoise)
      for ore_idx, (ore_name, (oreNoise, ore)) in enumerate(oresNoise.items()):   
        if self.progress_tracker and x % (WORLD_WIDTH // 10) == 0:
                # Calculate ore progress as a combination of current ore and position
                ore_portion = (ore_idx + (x / WORLD_WIDTH)) / total_ores
                ore_progress = ore_portion * phases['ores']
                total_progress = min(baseProgress + ore_progress, 1.0)
                self.progress_tracker.update(f"Placing {ore_name}...", total_progress)
          
        for y in range(WORLD_HEIGHT - 1, stoneHeight, -1):
              if oreNoise[y][x] > ore.rarity and not self[y][x].isAir:
                  self.array[y][x] = ore(x, y)

      baseProgress += phases['ores']
      
      # Tree pass
      if self.progress_tracker and x % (WORLD_WIDTH // 20) == 0:
            tree_progress = (x / WORLD_WIDTH) * phases['trees']
            total_progress = min(baseProgress + tree_progress, 1.0)
            self.progress_tracker.update("Growing trees...", total_progress)
      
      if isinstance(self[grassHeight][x], DirtBlock) and self[grassHeight][x].variant == "grass block":           
          if random.random() > 0.8:  # Simplified tree placement
              self.__generateTree(x, grassHeight - 1)
              
    if self.progress_tracker:
          self.progress_tracker.update("Almost", 1.0)           

  def generateMask(self):
    for row in self.array:
      for block in row:
        self.mask.draw(block.mask, block.rect.topleft)
        
  def __generateTree(self, x, y):
    if x < 3: return
    if x > WORLD_WIDTH - 3: return
    height = random.randint(3, 7)
    for r in range(y-height-1, y+1):
      for c in range(x-2, x+3):
        if not self[r][c].isAir: return
    for i in range(height):
      self[y-i][x] = OakLogBlock(x, y-i)
    self[y-height][x-2] = LeavesBlock(x-2, y-height)
    self[y-height][x-1] = LeavesBlock(x-1, y-height)
    self[y-height][x] = LeavesBlock(x, y-height)
    self[y-height][x+1] = LeavesBlock(x+1, y-height)
    self[y-height][x+2] = LeavesBlock(x+2, y-height)
    self[y-height-1][x-1] = LeavesBlock(x-1, y-height-1)
    self[y-height-1][x] = LeavesBlock(x, y-height-1)
    self[y-height-1][x+1] = LeavesBlock(x+1, y-height-1)
    self[y+1][x] = DirtBlock(x, y+1)
    
  
  def hoveredBlock(self) -> Block:
    mousepos = pg.mouse.get_pos()
    return self.blockAt(*pixelToCoord(*mousepos))

  def blockAt(self, x, y) -> Block:
    return self[y][x]

  def __getitem__(self, x: int):
    return self.array[x]
  
  def topBlock(self, x) -> Block:
    for i in range(0, WORLD_HEIGHT-1):
      if not self[i][x].isAir:
        return self[i][x]
  
  def getVisibleBlocks(self):
    self.visibleBlocks = [
      [(self[y][x], self.back[y][x], self.lightmap[y][x]) for x in range(player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1)]
            for y in range(player.camera.top // BLOCK_SIZE,
              (player.camera.bottom // BLOCK_SIZE) + 1)
    ]

  def draw(self):
    for row in self.visibleBlocks:
      for blockTuple in row:
        block, backBlock, light = blockTuple
        if not backBlock.isAir and block.isEmpty:
          backBlock.drawBlock()
        if not block.isAir:
          block.drawBlock()
        pg.draw.rect(SUNLIGHTSURF, (0,0,0,light), relativeRect(block.rect))
  
  def buildEdgePool(self):
    self.edgePool.clear()
    self.vertices.clear()
    # frame is 30 x 50 blocks
    for y in range(
        player.camera.top // BLOCK_SIZE,
        (player.camera.bottom // BLOCK_SIZE) + 1
    ):
      for x in range(
          player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1,
      ):
        for j in range(4):
          self[y][x].edgeExist[j] = False
    
    for y in range(
        player.camera.top // BLOCK_SIZE,
        (player.camera.bottom // BLOCK_SIZE) + 1
    ):
      for x in range(
          player.camera.left // BLOCK_SIZE,
          (player.camera.right // BLOCK_SIZE) + 1,
      ):
        cur = self[y][x]
        if not cur.isAir:
          # west
          if x-1 >= 0 and self[y][x-1].isAir:
            if y-1 >= 0 and self[y-1][x].edgeExist[direction.WEST] and self[y-1][x].edgeId[direction.WEST]<len(self.edgePool):
              # print("edge exists")
              self.edgePool[self[y-1][x].edgeId[direction.WEST]].ey += 1
              # print(self.edgePool[self[y-1][x].edgeId[Direction.WEST]])
              cur.edgeId[direction.WEST] = self[y-1][x].edgeId[direction.WEST]
              cur.edgeExist[direction.WEST] = True
            else:
              edge = Edge(x, y, x, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[direction.WEST] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[direction.WEST] = True
          # east
          if x+1 < (player.camera.right // BLOCK_SIZE) + 1 and self[y][x+1].isAir and self[y-1][x].edgeId[direction.EAST]<len(self.edgePool):
            if y-1 >= 0 and self[y-1][x].edgeExist[direction.EAST]:
              self.edgePool[self[y-1][x].edgeId[direction.EAST]].ey += 1
              cur.edgeId[direction.EAST] = self[y-1][x].edgeId[direction.EAST]
              cur.edgeExist[direction.EAST] = True
            else:
              edge = Edge(x+1, y, x+1, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[direction.EAST] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[direction.EAST] = True
          # north
          if y-1 >= 0 and self[y-1][x].isAir:
            if x-1 >= 0 and self[y][x-1].edgeExist[direction.NORTH] and self[y][x-1].edgeId[direction.NORTH]<len(self.edgePool):
              self.edgePool[self[y][x-1].edgeId[direction.NORTH]].ex += 1
              cur.edgeId[direction.NORTH] = self[y][x-1].edgeId[direction.NORTH]
              cur.edgeExist[direction.NORTH] = True
            else:
              edge = Edge(x, y, x+1, y)
              edgeId = len(self.edgePool)
              cur.edgeId[direction.NORTH] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[direction.NORTH] = True
          # south
          if y+1 < player.camera.bottom // BLOCK_SIZE + 1 and self[y+1][x].isAir and self[y][x-1].edgeId[direction.SOUTH]<len(self.edgePool):
            if x-1 >= 0 and self[y][x-1].edgeExist[direction.SOUTH]:
              self.edgePool[self[y][x-1].edgeId[direction.SOUTH]].ex += 1
              cur.edgeId[direction.SOUTH] = self[y][x-1].edgeId[direction.SOUTH]
              cur.edgeExist[direction.SOUTH] = True
            else:
              edge = Edge(x, y+1, x+1, y+1)
              edgeId = len(self.edgePool)
              cur.edgeId[direction.SOUTH] = edgeId
              self.edgePool.append(edge)
              cur.edgeExist[direction.SOUTH] = True
    for i in range(len(self.edgePool)):
      self.vertices.add(relativeCoord(self.edgePool[i].x*BLOCK_SIZE,self.edgePool[i].y*BLOCK_SIZE))
      self.vertices.add(relativeCoord(self.edgePool[i].ex*BLOCK_SIZE,self.edgePool[i].ey*BLOCK_SIZE))
      self.edgePool[i].draw()

  def generateLight(self, originr=None, originc=None):
    '''Generate lightmap for the entire world or specific part of world'''
    blockMap = [
      [False if not self[y][x].isEmpty or not self.back[y][x].isEmpty else True for x in range(WORLD_WIDTH)] for y in range(WORLD_HEIGHT)]
    
    if originr is None and originc is None:
      startr = startc = 0
      stopr = WORLD_HEIGHT
      stopc = WORLD_WIDTH
    else:
      startr = max(originr - 6, 0)
      startc = max(originc - 6, 0)
      stopr = min(originr + 7, WORLD_HEIGHT)
      stopc = min(originc + 7, WORLD_WIDTH)
    
    # loop over every block in the world
    for r in range(startr, stopr):
      for c in range(startc, stopc):
        # make queue to perform breadth first search to calculate the light at the block at row r and col c
        bfs = Queue()
        bfs.add((c, r)) # c is x and r is y
        bfs.add(None) # use Nones to track the level of the bfs
        level = 0 # keep track of level of bfs
        # set to store visited coordinates
        visited = set()
        visited.add((c, r))
        
        while bfs:
          
          if level > 6:
            self.lightmap[r][c] = 255
            break # exit after traversing 5 levels
          
          cur = bfs.poll()
          if cur is None:
            level += 1
            bfs.add(None)
            if bfs.peek is None: break
            else: continue
          
          x, y = cur
          
          if blockMap[y][x]:
            self.lightmap[r][c] = max(0, (level - 1) * 51)
            break
          
          # left block
          if x - 1 >= 0: # if block is inside world bounds
            new = (x - 1, y)
            if new not in visited: # if block has not been checked
              visited.add(new)
              bfs.add(new)

          # right block
          if x + 1 < WORLD_WIDTH: # if block is inside world bounds
            new = (x + 1, y)
            if new not in visited: # if block has not been checked
              visited.add(new)
              bfs.add(new)

          # upper block
          if y - 1 >= 0: # if block is inside world bounds
            new = (x, y - 1)
            if new not in visited: # if block has not been checked
              visited.add(new)
              bfs.add(new)
          
          # lower block
          if y + 1 < WORLD_HEIGHT: # if block is inside world bounds
            new = (x, y + 1)
            if new not in visited: # if block has not been checked
              visited.add(new)
              bfs.add(new)
    
  def update(self):
    self.getVisibleBlocks()
    self.draw()
    # self.buildEdgePool()
    
    self.visibleBlocks.clear()
    
    
class WorldLoader:
    def __init__(self, width, height):
        self.loadingScreen = LoadingScreen(width, height)
        self.world = None
        self.progress = 0.0
        self.targetProgress = 0.0
        self.progressUpdates = Queue()
        self.generationCompleteEvent = threading.Event()
        self.generationThread = None
        self.currentStep = ""
        self.lastUpdateTime = time.time()

    def _updateProgress(self, step, step_progress):
        self.progressUpdates.add((step, step_progress))

    def _generateWorld(self):
        try:
            progress_tracker = ProgressTracker(self._updateProgress)
            self.world = World(progress_tracker)
            self.generationCompleteEvent.set()
            
        except Exception as e:
            print(f"Error during world generation: {str(e)}")
            raise

    def startGeneration(self):
      self.generationCompleteEvent.clear()
      self.generationThread = threading.Thread(target=self._generateWorld, daemon=True)
      self.generationThread.start()

    def update(self):
        current_time = time.time()
        delta_time = current_time - self.lastUpdateTime
        self.lastUpdateTime = current_time

        while self.progressUpdates:
            step, progress = self.progressUpdates.poll()
            self.targetProgress = progress
            self.currentStep = step

        #Loading bar smoothing
        smoothing_speed = 5.0
        smoothing_factor = 1.0 - math.exp(-smoothing_speed * delta_time)
        self.progress += (self.targetProgress - self.progress) * smoothing_factor

        self.loadingScreen.update(self.progress, self.currentStep)
        self.loadingScreen.draw()

        progress_complete = abs(self.progress - self.targetProgress) < 0.01
        return self.generationCompleteEvent.is_set() and progress_complete