import pygame
import math
from resource_path import resource_path
from entities.game_object import GameObject


class Slipper(GameObject):

    GRAVITY     = 0.08
    FRAME_DELAY = 4
    FRAMES      = 4
    SCALE       = 0.8

    def __init__(self, x, y, angle, speed, power=50, ground_y=500):
        speed = min(speed, 12)
        self.vel_x    = math.cos(angle) * speed
        self.vel_y    = math.sin(angle) * speed
        self.x        = float(x)
        self.y        = float(y)
        self.power    = power
        self.ground_y = ground_y
        self.landed   = False
        self.anim_frame = 0
        self.anim_timer = 0
        sheet = pygame.image.load(resource_path("ASSETS/SLIPPER/slipper.png")).convert_alpha()
        fw = sheet.get_width() // self.FRAMES
        fh = sheet.get_height()
        sw, sh = int(fw * self.SCALE), int(fh * self.SCALE)
        self.frames = [
            pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, fh)), (sw, sh))
            for i in range(self.FRAMES)
        ]
        self.rect = pygame.Rect(int(x), int(y), sw, sh)
        self.mask = pygame.mask.from_surface(self.frames[0])
        
    # ── Method Overriding (GameObject.update) ───────────────────────────────
    def update(self, **kwargs):
        """Override: apply gravity, advance position, animate rotation."""
        self.anim_timer += 1
        if self.anim_timer >= self.FRAME_DELAY:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % self.FRAMES
        if self.landed:
            return
        self.vel_y += self.GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        if self.y >= self.ground_y:
            self.y      = self.ground_y
            self.vel_x  = 0
            self.vel_y  = 0
            self.landed = True
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.mask = pygame.mask.from_surface(self.frames[self.anim_frame])
    # ── Method Overriding (GameObject.draw) ─────────────────────────────────
    def draw(self, surface):
        """Override: render current animation frame."""
        surface.blit(self.frames[self.anim_frame], (self.rect.x, self.rect.y))

    # ── Method Overriding (GameObject.interact) ──────────────────────────────
    def interact(self, other=None):
        """Override: slipper 'interacts' with whatever it hits — marks as landed."""
        self.landed = True
        self.vel_x  = 0
        self.vel_y  = 0
