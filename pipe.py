import random
from game import SCREENHEIGHT, SCREENWIDTH

class Pipe:
    def __init__(self, pipe_sprites, base_sprite, gap=150):
        self.pipe_sprites = pipe_sprites
        self.base_sprite = base_sprite
        self.gap = gap
        self.pipe_width = self.pipe_sprites[0].get_width()
        self.pipe_height = self.pipe_sprites[0].get_height()
        self.base_height = self.base_sprite.get_height()
        self.generate()

    def generate(self):
        import random
        self.upper = {}
        self.lower = {}
        offset = self.gap
        y2 = offset + random.randrange(0, int(SCREENHEIGHT - self.base_height - offset))
        pipeX = SCREENWIDTH + 10
        y1 = self.pipe_height - y2 + offset
        self.upper = {'x': pipeX, 'y': -y1}
        self.lower = {'x': pipeX, 'y': y2}

    def move(self, vel_x):
        self.upper['x'] += vel_x
        self.lower['x'] += vel_x

    def draw(self, screen):
        screen.blit(self.pipe_sprites[0], (self.upper['x'], self.upper['y']))
        screen.blit(self.pipe_sprites[1], (self.lower['x'], self.lower['y']))
