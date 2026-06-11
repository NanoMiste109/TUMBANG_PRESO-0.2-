import pygame
import math
from resource_path import resource_path
from entities.game_object import GameObject


# Maps slipper index → sprite path
SLIPPER_SPRITES = {
    0: "ASSETS/SLIPPER/slipper.png",
    1: "ASSETS/SLIPPER/slipper_v2.png",
    2: "ASSETS/SLIPPER/slipper_v3.png",
    3: "ASSETS/SLIPPER/slipper_v4.png",
}

# v3: first 7 frames = single, frames 7-15 = multiplied
V3_SINGLE_FRAMES     = 7
V3_MULTIPLIED_FRAMES = 9   # frames 7..15

# Rocket (v2) speed multiplier when ability is active
V2_SPEED_BOOST = 2.0

# Stun duration for v4 Pikachu (frames at 60fps)
V4_STUN_FRAMES = 180  # 3 seconds


class Slipper(GameObject):

    GRAVITY     = 0.08
    FRAME_DELAY = 4
    SCALE       = 0.8

    def __init__(self, x, y, angle, speed, power=50, ground_y=500, slipper_index=0):
        speed = min(speed, 12)
        self.slipper_index = slipper_index
        self.vel_x    = math.cos(angle) * speed
        self.vel_y    = math.sin(angle) * speed
        self.x        = float(x)
        self.y        = float(y)
        self.power    = power
        self.ground_y = ground_y
        self.landed   = False
        self.anim_frame = 0
        self.anim_timer = 0
        self.ability_used = False    # one-use flag per throw

        # Load frames based on slipper type
        sprite_path = SLIPPER_SPRITES.get(slipper_index, SLIPPER_SPRITES[0])
        try:
            sheet = pygame.image.load(resource_path(sprite_path)).convert_alpha()
        except Exception:
            sheet = pygame.image.load(resource_path(SLIPPER_SPRITES[0])).convert_alpha()

        fh = sheet.get_height()

        if slipper_index == 2:
            # v3 Multiplier: detect frames from sheet width
            total_frames = round(sheet.get_width() / fh)
            fw = sheet.get_width() // total_frames
            sw, sh = int(fw * self.SCALE), int(fh * self.SCALE)
            all_frames = [
                pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, fh)), (sw, sh))
                for i in range(total_frames)
            ]
            single_count     = min(V3_SINGLE_FRAMES, total_frames)
            multiplied_count = total_frames - single_count
            self.frames          = all_frames[:single_count]
            self.frames_split    = all_frames[single_count:] if multiplied_count > 0 else all_frames[:single_count]
            self._split_active   = False
            self._num_frames     = len(self.frames)
        else:
            # All other slippers: 4 frames
            total_frames = 4
            fw = sheet.get_width() // total_frames
            sw, sh = int(fw * self.SCALE), int(fh * self.SCALE)
            self.frames = [
                pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, fh)), (sw, sh))
                for i in range(total_frames)
            ]
            self._num_frames = total_frames

        self.rect = pygame.Rect(int(x), int(y), self.frames[0].get_width(), self.frames[0].get_height())
        self.mask = pygame.mask.from_surface(self.frames[0])

    # ── Ability activation ────────────────────────────────────────────────────

    def activate_ability(self, guards=None):
        """
        Activate this slipper's one-time ability.
        v2: boost speed.
        v3: switch to split frames (caller also spawns extra slippers).
        v4: mark for pikachu stun (stun applied in gameplay on guard hit).
        Returns True if ability was activated.
        """
        if self.ability_used:
            return False
        self.ability_used = True

        if self.slipper_index == 1:  # Rocket — speed boost
            self.vel_x *= V2_SPEED_BOOST

        elif self.slipper_index == 2:  # Multiplier — switch frames
            self._split_active = True
            self.anim_frame    = 0
            self.anim_timer    = 0
            self._num_frames   = len(self.frames_split)

        # v4 Pikachu: stun is applied in gameplay when this slipper hits a guard
        return True

    @property
    def is_pikachu(self):
        return self.slipper_index == 3

    @property
    def split_just_activated(self):
        """True on the frame split is activated — gameplay uses this to spawn extra slippers."""
        return self.slipper_index == 2 and self.ability_used and self._split_active

    # ── Method Overriding (GameObject.update) ───────────────────────────────
    def update(self, **kwargs):
        """Override: apply gravity, advance position, animate rotation."""
        self.anim_timer += 1
        if self.anim_timer >= self.FRAME_DELAY:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % self._num_frames
        if self.landed:
            return
        self.vel_y += self.GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        if self.y >= self.ground_y:
            self.y     = self.ground_y
            self.vel_x = 0
            self.vel_y = 0
            self.landed = True
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        cur_frames = self.frames_split if (self.slipper_index == 2 and getattr(self, '_split_active', False)) else self.frames
        self.mask = pygame.mask.from_surface(cur_frames[self.anim_frame])

    # ── Method Overriding (GameObject.draw) ─────────────────────────────────
    def draw(self, surface):
        """Override: render current animation frame."""
        cur_frames = self.frames_split if (self.slipper_index == 2 and getattr(self, '_split_active', False)) else self.frames
        surface.blit(cur_frames[self.anim_frame], (self.rect.x, self.rect.y))

    # ── Method Overriding (GameObject.interact) ──────────────────────────────
    def interact(self, other=None):
        """Override: slipper hits something — marks as landed."""
        self.landed = True
        self.vel_x  = 0
        self.vel_y  = 0
