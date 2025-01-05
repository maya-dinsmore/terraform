RES = (1280,720)
FPS = 60

MAP_SIZE = (200,75) 
TILE_SIZE = 12

# key = numpy array value in procgen.py
TILE_VARIANTS = {0: {'variant': 'dirt', 'graphic': None}, 
                 1: {'variant': 'stone', 'graphic': None}, 
                 2: {'variant': 'sandstone', 'graphic': None}, 
                 3: {'variant': 'ice', 'graphic': None}, 
                 4: {'variant': 'coal', 'graphic': None, 'frequency': 5},
                 5: {'variant': 'copper', 'graphic': None, 'frequency': 4}, 
                 6: {'variant': 'iron', 'graphic': None, 'frequency': 3}, 
                 7: {'variant': 'silver', 'graphic': None, 'frequency': 2}, 
                 8: {'variant': 'gold', 'graphic': None, 'frequency': 1},
                 9: {'variant': 'snow', 'graphic': None}    
                }

Z_LAYERS = {'clouds': 0,
            'bg': 1,
            'main': 2,
            'player': 3,
        }