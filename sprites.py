import pygame as pg

from settings import *
from file_imports import *
from player import *

# base attributes
class Sprite(pg.sprite.Sprite):
    def __init__(self, pos, surf, z, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z # layer to render on

class Cloud(Sprite):
    def __init__(self, pos, surf, speed, z, groups, player_x): 
        super().__init__(pos, surf, z, groups)
        self.speed = speed
        self.player_x = player_x

    def move(self, dt):  
        self.rect.x -= self.speed * dt 
        if self.rect.right < self.player_x - RES[0] - self.image.get_width() or self.rect.left <= 0:
            self.kill()
        
    def update(self, dt):
        self.move(dt)
            
class Tree(Sprite):
    def __init__(self, pos, surf, z, groups):
        super().__init__(pos, surf, z, groups)
        self.strength = 50 # will be chopped down when this value reaches 0
  