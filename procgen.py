import pygame as pg
import numpy as np
import noise
import random

from settings import *
from file_imports import *
from sprites import *

class ProcGen:
    def __init__(self, assets, all_sprites, cloud_sprites):
        self.assets = assets
        self.all_sprites = all_sprites
        self.cloud_sprites = cloud_sprites
    
        self.terrain_tiles = np.zeros((MAP_SIZE[0], MAP_SIZE[1]), dtype = int)
        self.biome = 'tundra'
        
        # load graphics
        for data in TILE_VARIANTS.values():
            data['graphic'] = load_img(f'../graphics/terrain/tiles/{data["variant"]}.png')

        self.gen_terrain()
                
    def gen_terrain(self, surface_scale = MAP_SIZE[0], surface_octaves = 3, seed = 1221):
        height_map = np.zeros(MAP_SIZE[0])
        for x in range(MAP_SIZE[0]):
            height_map[x] = noise.pnoise1(
                                x / surface_scale,  
                                octaves = surface_octaves, 
                                persistence = 0.5, # lower persistance = smoother terrain
                                lacunarity = 2.0, # rate of change for the frequency at each octave
                                repeat = MAP_SIZE[0], 
                                base = seed 
                            )
        # height_map - height_map.min(): convert negative values to positive
        # divide by ptp: keep the range of values between 0-1
        height_map = (height_map - height_map.min()) / np.ptp(height_map)
        height_map *= MAP_SIZE[1] // 2 # centered on the map's y-axis

        for x in range(MAP_SIZE[0]):
            surface_level = int(height_map[x])
            for y in range(MAP_SIZE[1]):
                # above ground
                if y < surface_level: 
                    if y == surface_level - 1:
                        self.terrain_tiles[x,y] = 9 # snow (this will have to become more modular for varying biomes)
                    else:
                        self.terrain_tiles[x,y] = -1 # air
                
                # ground level
                elif y == surface_level: 
                    self.terrain_tiles[x,y] = 0 # dirt
                    if random.randint(0,100) <= 10:
                        self.spawn_tree(pos = (x,y))
                
                # underground
                else:
                    # determine the tile's depth relative to the height of the map
                    rel_depth = (y - surface_level) / MAP_SIZE[1]
                    if rel_depth < 0.1:
                        self.terrain_tiles[x,y] = 0
                    elif rel_depth < 0.2:
                        self.terrain_tiles[x,y] = 1 if random.randint(0,100) <= 33 else 0
                    elif rel_depth < 0.4:
                        self.terrain_tiles[x,y] = random.choice((2,3)) if random.randint(0,100) <= 25 else random.choice((0,1))
                    else:
                        # potential for ore generation
                        if random.randint(0,10) < 2:
                            for index in range(4,9):
                                if random.randint(0,10) <= TILE_VARIANTS[index]['frequency']:
                                    self.terrain_tiles[x,y] = index
                                    break
                                else:
                                    self.terrain_tiles[x,y] = 1
                        else:
                            self.terrain_tiles[x,y] = 1 
                                
        return self.terrain_tiles

    def spawn_tree(self, pos):
        surf = load_img(f'../graphics/terrain/trees/{self.biome}_tree.png')
       
        if 1 < pos[0] < MAP_SIZE[0] - 1: # not on either edge of the map 
            # the width of the surface is 36px (3 tiles), so trees will only spawn at a coordinate with at least 1 tile on the same x-axis to its left & right  
            center_tile = self.terrain_tiles[pos[0], pos[1]]    
            left_tile = self.terrain_tiles[pos[0] - 1, pos[1]]
            right_tile = self.terrain_tiles[pos[0] + 1, pos[1]]
            if center_tile == 0 and left_tile == 0 and right_tile == 0: # dirt tiles
                Tree(
                    pos = (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE - surf.get_height()), 
                    surf = surf, z = Z_LAYERS['bg'], 
                    groups = self.all_sprites
                )
    
    def spawn_clouds(self, player_x, dt):
        if not self.cloud_sprites: 
            for cloud in range(random.randint(5,10)):
                surf = random.choice(self.assets['bg details']['clouds'])
                x = player_x + RES[0] / 2 + surf.get_width() + random.randint(0,1500) # start on the outskirts of the visible screen area
                y = random.randint(100,300) 
                Cloud(
                    pos = (x,-y), 
                    surf = surf, 
                    speed = random.randint(15,25), 
                    z = Z_LAYERS['clouds'], 
                    groups = [self.all_sprites, self.cloud_sprites],
                    player_x = player_x
                )

    def load_bg(self, bg_type, screen, offset): 
        img = self.assets[self.biome]['bg'][bg_type]
        underground_start = self.assets[self.biome]['bg']['landscape'].get_height()
        # loop the image if it doesn't cover the full screen width/height
        for x in range(int((MAP_SIZE[0]) / TILE_SIZE) + 1):
            for y in range(int((MAP_SIZE[1]) / TILE_SIZE) + 1):
                left = img.get_width() * x
                top = 0 if bg_type == 'landscape' else underground_start + img.get_height() * y
                screen.blit(img, (left, top) - offset)

    def render(self, screen, offset):
        self.load_bg('landscape', screen, offset)
        self.load_bg('underground', screen, offset)
        
        for x in range(MAP_SIZE[0]):
            for y in range(MAP_SIZE[1]):
                tile_index = self.terrain_tiles[x,y]
                if tile_index != -1: # not air
                    if tile_index == 9: 
                        img = TILE_VARIANTS[9]['graphic']
                        screen.blit(img, (x * TILE_SIZE, (y * TILE_SIZE) + (TILE_SIZE - img.get_height())) - offset)
                    else:
                        screen.blit(TILE_VARIANTS[tile_index]['graphic'], (x * TILE_SIZE, y * TILE_SIZE) - offset)
    
    def update(self, player_x, dt):
        self.spawn_clouds(player_x, dt)
