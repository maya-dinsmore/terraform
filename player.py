import pygame as pg
pg.init()

from settings import *
from file_imports import *
from ui import UI

class Player(pg.sprite.Sprite):
    def __init__(self, pos, frames, z, groups, terrain_tiles):
        super().__init__(groups)
        self.terrain_tiles = terrain_tiles # storing for collision detection
        self.camera_offset = pg.Vector2() # configured in main.py
        
        self.health = 100
        self.inventory = {index: None for index in range(50)}
        self.inv_index = 1
        self.item_using = 'pickaxe'

        # graphics
        self.frames = frames
        self.frame_index = 0
        self.z = z # rendering layer 
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(center = pos).inflate(-3,0)
        self.animation_speed = 6
        self.facing_left = True
        self.screen = pg.display.get_surface()
        
        # movement
        self.direction = pg.Vector2()
        self.speed = 150
        self.gravity = 1200
        self.jump_height = 400
        self.jumping = False

        self.ui = UI(player = self)

    def keyboard_input(self):
        key = pg.key.get_just_pressed() 
        arrow_key = pg.key.get_pressed() # not using get_just_pressed since it resulted in choppy movement
        
        movement = pg.Vector2() # reset every frame

        if arrow_key[pg.K_LEFT]:
            movement.x -= 1
            if not self.facing_left:
                self.facing_left = True
                self.image = pg.transform.flip(self.image, True, False)

        if arrow_key[pg.K_RIGHT]:
            movement.x += 1
            if self.facing_left:
                self.facing_left = False
                self.image = pg.transform.flip(self.image, True, False)
        
        if movement.x:
            self.direction.x = movement.normalize().x
            self.state = 'walking'
        else:
            self.direction.x = 0
            if self.state != 'mining':
                self.state = 'idle' 

        if key[pg.K_SPACE]:
            self.jump()
        
        if key[pg.K_RSHIFT] or key[pg.K_LSHIFT]:
            self.ui.expand_inv = not self.ui.expand_inv # open/close inventory

        for num in range(pg.K_0, pg.K_9 + 1):
            if key[num]:
                num_pressed = num - pg.K_0 # convert the key's ascii value to the actual number pressed
                self.inv_index = num_pressed
        

    def mouse_input(self):
        clicking = pg.mouse.get_pressed()
        self.mouse_pos = (pg.mouse.get_pos()[0] + int(self.camera_offset[0]), pg.mouse.get_pos()[1] + int(self.camera_offset[1]))
        if clicking[0]: # right click
            self.tile_pos = (self.mouse_pos[0] // TILE_SIZE, self.mouse_pos[1] // TILE_SIZE) # convert the mouse position to the grid coordinate system
            # this will need to be more modular for the various items available but fine for now
            if self.item_using == 'pickaxe':
                self.mining()
            else:
                self.place_block()
    
    def movement(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.apply_physics(axis = 'x')

        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y * dt
        self.apply_physics(axis = 'y')  

    # get rects from the tiles within the player's current position for collision detection
    def get_colliding_rects(self):
        topleft = pg.Vector2(self.rect.topleft) // TILE_SIZE
        tile_rects = []
        # cycle through the tiles within the player's current position
        for x in range(int(topleft.x), int(topleft.x + (self.rect.width / TILE_SIZE)) + 1):
            for y in range(int(topleft.y), int(topleft.y + (self.rect.height / TILE_SIZE)) + 1):
                # look for tiles within the map dimensions that aren't air or grass (walking over grass tiles gave the impression that the player was floating)
                if 0 <= x < MAP_SIZE[0] and 0 <= y < MAP_SIZE[1] and self.terrain_tiles[x,y] not in (-1,9):
                    tile_rects.append(pg.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
 
        return tile_rects

    def apply_physics(self, axis):
        tiles_colliding = self.get_colliding_rects()
        for tile in tiles_colliding:
            if self.rect.colliderect(tile):
                if axis == 'x':
                    # moving right
                    if self.direction.x > 0:  
                        # determine whether the colliding tile has any tiles on top of it
                        player_topright = pg.Rect(self.rect.right, self.rect.bottom - (TILE_SIZE * 2), 1, TILE_SIZE)
                        if player_topright.colliderect(tile):
                            self.rect.right = tile.left 
                        else:
                            self.rect.bottomright = tile.topleft - pg.Vector2(0,1) # step over the tile
                    
                    # moving left
                    elif self.direction.x < 0: 
                        player_topleft = pg.Rect(self.rect.left, self.rect.bottom - (TILE_SIZE * 2), 1, TILE_SIZE)
                        if player_topleft.colliderect(tile):
                            self.rect.left = tile.right
                        else:
                            self.rect.bottomleft = tile.topright - pg.Vector2(0,1) 
        
                    self.direction.x = 0
                else:
                    # moving up
                    if self.direction.y < 0:
                        self.rect.top = tile.bottom
                    
                    # moving down
                    elif self.direction.y > 0: 
                        self.rect.bottom = tile.top
                        if self.jumping:
                            self.jumping = False
                
                    self.direction.y = 0
                
    def jump(self):
        if not self.jumping and self.direction.y == 0:
            self.direction.y = -self.jump_height
            self.jumping = True

    def mining(self):
        mine_radius = 60 # reachable area in pixels
        tile_center = pg.Vector2((self.tile_pos[0] * TILE_SIZE) + TILE_SIZE // 2, (self.tile_pos[1] * TILE_SIZE) + TILE_SIZE // 2)
        tile_distance = pg.Vector2(self.rect.center).distance_to(tile_center)
        if self.terrain_tiles[self.tile_pos] != -1 and tile_distance <= mine_radius: # mining a reachable, non-air tile 
            self.state = 'mining'
            tile_variant = TILE_VARIANTS[self.terrain_tiles[self.tile_pos]]['variant'] # keep this above the tile removal logic to retain its index before converting it to air
            
            # add the tile graphic fading away at a speed dependent on its strength
            if self.terrain_tiles[self.tile_pos] != 9: # snow tiles only serve an aesthetic purpose
                self.add_to_inventory(item = tile_variant)
            
            # remove the tile
            self.terrain_tiles[self.tile_pos] = -1 # becomes air
            tile_above = self.terrain_tiles[self.tile_pos[0], self.tile_pos[1] - 1]
            if tile_above == 9: # snow
                self.terrain_tiles[self.tile_pos[0], self.tile_pos[1] - 1] = -1

    def add_to_inventory(self, item):
        for index, content in self.inventory.items():
            if self.inventory[index] is None:
                self.inventory[index] = {item: 1}
                return
            elif item in content:
                self.inventory[index][item] += 1
                return

    def place_block(self):
        current_item = self.item_using
        for key, values in TILE_VARIANTS.items():
            if values['variant'] == current_item:
                self.terrain_tiles[self.tile_pos] = key # update the index of the tile clicked on
                break

    def animation(self, dt):
        if self.state != 'idle':
            self.frame_index += self.animation_speed * dt
            self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
            self.image = pg.transform.flip(self.image, True, False) if not self.facing_left else self.image
        else:
            self.frame_index = 0
    
    def update(self, dt):
        self.keyboard_input()
        self.mouse_input()
        self.movement(dt)
        self.animation(dt)
        self.ui.update()
