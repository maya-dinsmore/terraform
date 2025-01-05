import pygame as pg 
import sys

from settings import *
from file_imports import *
from procgen import ProcGen
from player import Player
from sprites import *

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((RES))
        self.clock = pg.time.Clock()
        self.camera_pos = pg.Vector2()
        self.running = True

        # sprite groups
        self.all_sprites = pg.sprite.Group()
        self.cloud_sprites = pg.sprite.Group()

        self.assets = {
            'forest': {
                'bg': {
                    'landscape': load_img('../graphics/backgrounds/Background_91.png'),
                    'underground': load_img('../graphics/backgrounds/Background_154.png'),     
                }
            },

            'tundra': {
                'bg': {
                    'landscape': load_img('../graphics/backgrounds/Background_101.png'),
                    'underground': load_img('../graphics/backgrounds/Background_32.png'),
                    }
                },

            'hell': {
                'bg': {
                    'landscape': load_img('../graphics/backgrounds/Background_175.png'),
                    'underground': load_img('../graphics/backgrounds/Background_125.png'), 
                }
            },

            'highlands': {
                'bg': {
                    'landscape': load_img('../graphics/backgrounds/Background_171.png'),
                    'underground': load_img('../graphics/backgrounds/Background_2.png'),
                }
            },

            'space': {
                'bg': {
                'landscape': load_img('../graphics/backgrounds/Background_180.png')
                }
            },
            
            'bg details': {
                'clouds': load_folder('../graphics/weather/clouds')
            },
        }

        self.map = ProcGen(self.assets, self.all_sprites, self.cloud_sprites)
        
        self.player = Player(
                        pos = ((1000,200)), 
                        frames = load_subfolders('../graphics/player'), 
                        z = Z_LAYERS['player'],
                        groups = self.all_sprites, 
                        terrain_tiles = self.map.terrain_tiles
                    )

    def camera(self):
        target = pg.Vector2(self.player.rect.centerx, self.player.rect.centery)
        self.camera_pos += (target - self.camera_pos) * 0.05 # move across the distance between the target and current position
        self.camera_offset = self.camera_pos - pg.Vector2(RES) / 2 # center the screen on the player
        self.player.camera_offset = self.camera_offset
        

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000 
            self.screen.fill(('lightblue'))
            
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
            
            self.camera()
            self.map.render(self.screen, self.camera_offset)
            self.map.update(player_x = self.player.rect.centerx, dt = dt)

            # render sprites by their z-level
            for sprite in sorted(self.all_sprites, key = lambda sprite: sprite.z):
                self.screen.blit(sprite.image, sprite.rect.topleft - self.camera_offset)
                sprite.update(dt)
          
            pg.display.update()  

if __name__ == '__main__':
    game = Game()
    game.run()