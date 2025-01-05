import pygame as pg
pg.init()

from file_imports import *

class UI:
    def __init__(self, player):
        self.player = player
        self.fonts = {
            'inventory': pg.font.Font('../graphics/fonts/Good Old DOS.ttf', 11)
        }

        self.expand_inv = False # whether to display the inventory's top row or its entirety

    def render_inventory(self):
        # initialize inventory  
        self.inv_box_width, self.inv_box_height = 48,48
        inv_rows = 1 if not self.expand_inv else 5
        inv_cols = 10
        # inventory background
        bg_surf = pg.Surface((self.inv_box_width * inv_cols, self.inv_box_height * inv_rows))
        bg_surf.fill('dark gray')
        bg_surf.set_alpha(200)
        bg_rect = bg_surf.get_rect(topleft = (5,5))
        self.player.screen.blit(bg_surf, bg_rect)
        pg.draw.rect(self.player.screen, 'black', bg_rect, 3)
        
        # individual boxes
        for x in range(inv_cols):
            left = self.inv_box_width * x + 5
            for y in range(inv_rows): 
                top = self.inv_box_height * y + 5
                box = pg.Rect(left, top, self.inv_box_width, self.inv_box_height)
                pg.draw.rect(self.player.screen, 'black', box, 2)

    # render the icons of the inventory contents
    def render_inv_icons(self):
        icons = {}
        for index, item_data in self.player.inventory.items():
            if item_data: # ignore empty slots
                item = list(item_data.keys())[0]
                amount = list(item_data.values())[0]
                if item not in icons:
                    icons[item] = pg.transform.scale2x(load_img(f'../graphics/terrain/tiles/{item}.png'))
                
                # determine which inventory slot the new item corresponds to
                inv_col = index % 10
                inv_row = index // 10
                
                # render the icon in the center of the inventory slot
                padding = 5
                x = ((inv_col * self.inv_box_width) + (self.inv_box_width - icons[item].get_width()) // 2) + padding
                y = ((inv_row * self.inv_box_height) + (self.inv_box_height - icons[item].get_height()) // 2) + padding
                self.player.screen.blit(icons[item], (x,y))
                
                # render the item quantity in the bottom right corner
                amount_surf = self.fonts['inventory'].render(str(amount), True, 'black')
                amount_rect = amount_surf.get_rect(center = (x + icons[item].get_width(), y + icons[item].get_height())) 
                
                text_bg_surf = pg.Surface(amount_surf.get_size())
                text_bg_surf.fill('dark gray')
                #text_bg_surf.set_alpha(200)
                
                text_bg_rect = text_bg_surf.get_rect(center = amount_rect.center)
                
                self.player.screen.blit(text_bg_surf, text_bg_rect)
                self.player.screen.blit(amount_surf, amount_rect)

    def update(self):
        self.render_inventory()
        self.render_inv_icons()