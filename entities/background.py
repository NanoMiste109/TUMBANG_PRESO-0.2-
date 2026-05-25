import pygame


class ParallaxBackground:

    def __init__(self, layers):
        self.width  = 800
        self.height = 600
        self.layers = [(surf, y, speed, 0.0) for surf, y, speed in layers]

    def update(self):
        updated = []
        for surf, y, speed, x in self.layers:
            if speed > 0:
                x -= speed
                if x < -surf.get_width():
                    x = 0
            updated.append((surf, y, speed, x))
        self.layers = updated
        
    def draw(self, surface):
        for surf, y, speed, x in self.layers:
            img_w = surf.get_width()
            cx = x
            while cx < self.width:
                surface.blit(surf, (cx, y))
                cx += img_w
