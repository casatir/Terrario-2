import pygame, opensimplex, os, random
from Classes.player import Player
from Classes.tile import Tile, Cave
from Classes.props import *

biomes = {
    float("-inf"): ["forest", "desert", "snow"],
    16: ["cave", "sand_cave", "snowy_cave"],
    128: ["crystal_cave", "haunted_cave"],
    256: ["lush_cave"],
    512: ["hell"]
}

tile_palette = {
    "forest": {
        "background": "air",
        "primary_tile": "dirt",
        "top_tile": "grass"
    },

    "desert": {
        "background": "air",
        "primary_tile": "sand",
        "top_tile": "sand"
    },

    "snow": {
        "background": "air",
        "primary_tile": "dirt",
        "top_tile": "snowy_grass"
    }
}

props = {
    "forest": [generate_tree],
    "desert": [generate_cactus],
    "snow": [generate_snowy_tree]
}

ores = {
    "forest": [],
    "desert": [],
    "snow": []
}

class Map:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.tiles = {}
        self.player = Player((0, 0), self)

        self.scale = 0.1

        self.offset = pygame.Vector2()
        self.render_distance = 32

        opensimplex.random_seed()

    def get_tile(self, x: int, y: int) -> Tile:
        if not x in self.tiles or not y in self.tiles[x]:
            self.generate_tile(x, y)

        return self.tiles[x][y]

    def set_tile(self, tile: Tile, x:int , y: int) -> Tile:
        if not x in self.tiles or not y in self.tiles[x]:
            self.generate_tile(x, y)
        
        self.tiles[x][y] = tile
        return Tile

    def generate_tile(self, x, y):
        if not x in self.tiles:
            self.tiles[x] = {}

        if y in self.tiles[x]:
            return

        # Génération de la surface
        if y < 4:
            biome = "plains" if opensimplex.noise2(x * 0.0075, y * 0.0075) > 0 else "desert"
            tile_palette = {
                "surface_block": "grass" if biome == "plains" else "sand",
                "primary_block": "dirt" if biome == "plains" else "sand"
            }

            if y < 0:
                value = int(opensimplex.noise2(x * self.scale * 0.5, 0) * 10)

                self.tiles[x][y] = Tile("air", "air", minable=False, can_collide=False)
                if y == value:
                    self.tiles[x][y] = Tile(tile_palette["surface_block"], tile_palette["surface_block"])

                    if biome == "desert":
                        if random.randint(0, 10) == 0:
                            self.generate_tile(x, y-1)
                            generate_cactus(self, x, y - 1, random.randint(1, 4))

                    else:
                        if random.randint(0, 2) == 0:
                            self.generate_tile(x, y-1)
                            self.tiles[x][y-1].type = "tulip" if random.randint(0, 1) else "weed"

                        if random.randint(0, 10) == 0:
                            generate_tree(self, x, y-1)

                elif y > value: 
                    self.tiles[x][y] = Tile(tile_palette["primary_block"], tile_palette["primary_block"])

            elif y == 0:
                self.generate_tile(x, y-1)
                type = tile_palette["surface_block"] if self.tiles[x][y-1].type == "air" else tile_palette["primary_block"]
                self.tiles[x][y] = Tile(type, type)

                if self.tiles[x][y-1].type == "air":
                    if biome == "desert":
                        if random.randint(0, 10) == 0:
                            generate_snowman(self, x, y - 1)
                    else:
                        if random.randint(0, 2) == 0:
                            type = "tulip" if random.randint(0, 1) else "weed"
                            self.tiles[x][y-1] = Tile(type, type, minable=False, can_collide=False)
                            
            else:
                self.tiles[x][y] = Tile(tile_palette["primary_block"], tile_palette["primary_block"])

        # Génération des grottes
        else:
            biome = "plains" if opensimplex.noise2(x * 0.0075, y * 0.0025) > 0 else "desert"
            tile_palette = {
                "primary_block": "stone" if biome == "plains" else "sandstone",
                "cave_block": "cave" if biome == "plains" else "sandstone_cave"
            }

            if opensimplex.noise2(x * self.scale, y * self.scale) < 0:
                self.tiles[x][y] = Tile(tile_palette["primary_block"], tile_palette["primary_block"])
            else:
                self.tiles[x][y] = Cave("cave", tile_palette["primary_block"])
            
    def render(self):
        self.display_surface.fill(pygame.Color(77, 165, 217))

        self.offset.x = self.player.rect.centerx - self.display_surface.get_width() / 2
        self.offset.y = self.player.rect.centery - self.display_surface.get_height() / 2

        for x in range(int(self.player.position.x) - self.render_distance, int(self.player.position.x) + self.render_distance + 1):
            for y in range(int(self.player.position.y) - self.render_distance, int(self.player.position.y) + self.render_distance + 1):
                if not x in self.tiles or not y in self.tiles[x]:
                    self.generate_tile(x, y)

                offset_rect = pygame.Vector2(x, y) * 32 - self.offset
                self.tiles[x][y].update(offset_rect)

        offset_rect = self.player.rect.copy()
        offset_rect.center -= self.offset
        self.display_surface.blit(self.player.image, offset_rect)
        
        if self.player.going_up == True:
            self.player.climb()
        
        if self.player.falling:
            self.display_surface.blit(pygame.transform.scale(pygame.image.load("Images/PLayer/Parachute.png"), (32, 32)), (offset_rect[0], offset_rect[1] - 32))
