import pygame as pg

WIDTH = 1280
HEIGHT = 720
FPS = 60

pg.init()

SURF = pg.display.set_mode((WIDTH, HEIGHT))
FRAME = SURF.get_rect()

clock = pg.time.Clock()
pg.display.set_caption("Terraria")

font12 = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 12)
font16 = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 16)

BLOCK_SIZE = 32
BLOCK_RECT = pg.rect.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)
WORLD_HEIGHT = 100
WORLD_WIDTH = 200    #default is 1000

BIG = 2147483647

RABBIT_RARITY = 10 # 1 rabbit every 10 blocks on avg
NPC_RARITY = 30 # 1 npc every 20 blocks on avg
DOG_RARITY = 50

FIRST_MESSAGE = (
	"Welcome to TerraCraft!",
	"Mine trees to get wood!",
	"Use the crafting table to craft!",
	"Craft planks with logs!",
	"Craft sticks with 2 planks!",
	"Craft a pickaxe with 2 sticks and 3 planks!"
)