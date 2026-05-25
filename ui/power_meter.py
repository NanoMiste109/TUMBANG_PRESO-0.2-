import pygame
import math
from resource_path import resource_path

class PowerMeter:
  
    def __init__(self):
        self.phase    = None
        self.angle    = 0.0
        self.power    = 0
        self.timer    = 0.0
        self.charging = False
        self.font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 14)

    def start_direction(self):
       
        self.phase   = "direction"
        self.timer   = 0.0
        self.charging = True

    def lock_direction(self):
     
        if self.phase == "direction":
            self.phase = "power"
            self.timer = 0.0

    def lock_power(self):
        
        if self.phase == "power":
            raw   = (math.sin(self.timer * 2.0) + 1) / 2
            self.power = int(raw * 100)
            self.phase    = None
            self.charging = False
            return self.angle, self.power
        return None

    def reset(self):
        self.phase    = None
        self.charging = False

    def _current_angle(self):
     
        sweep = math.radians(60)
        return -sweep * math.sin(self.timer * 1.5)

    def _current_power(self):
        return int(((math.sin(self.timer * 2.0) + 1) / 2) * 100)

    def update(self):
        if self.phase in ("direction", "power"):
            self.timer += 0.05

    def draw(self, surface, player_x, player_y):
        if self.phase is None:
            return

        if self.phase == "direction":
            angle = self._current_angle()
            self._draw_arrow(surface, player_x, player_y, angle)
            hint = self.font.render("SPACE: lock dir  |  E: toggle special", True, (255, 255, 255))
            surface.blit(hint, (10, 558))

        elif self.phase == "power":
            self._draw_arrow(surface, player_x, player_y, self.angle)
            self._draw_power_bar(surface)
            hint = self.font.render("SPACE to throw", True, (255, 255, 255))
            surface.blit(hint, (10, 560))

    def _draw_arrow(self, surface, px, py, angle):
        length = 50
        tip_x = int(px + math.cos(angle) * length)
        tip_y = int(py + math.sin(angle) * length)
        pygame.draw.line(surface, (255, 255, 0), (px, py), (tip_x, tip_y), 3)
        head_len = 10
        left  = angle + math.radians(150)
        right = angle - math.radians(150)
        pygame.draw.line(surface, (255, 255, 0), (tip_x, tip_y),
                         (int(tip_x + math.cos(left)  * head_len),
                          int(tip_y + math.sin(left)  * head_len)), 3)
        pygame.draw.line(surface, (255, 255, 0), (tip_x, tip_y),
                         (int(tip_x + math.cos(right) * head_len),
                          int(tip_y + math.sin(right) * head_len)), 3)
                          
    def _draw_power_bar(self, surface):
        bar_x, bar_y = 10, 575
        bar_w, bar_h = 150, 14
        pwr = self._current_power()
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
        r = int(255 * pwr / 100)
        g = int(255 * (1 - pwr / 100))
        pygame.draw.rect(surface, (r, g, 0), (bar_x, bar_y, int(bar_w * pwr / 100), bar_h))
        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 1)
        label = self.font.render(f"PWR {pwr}", True, (255, 255, 255))
        surface.blit(label, (bar_x + bar_w + 6, bar_y))
