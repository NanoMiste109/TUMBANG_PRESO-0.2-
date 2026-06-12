import pygame
from resource_path import resource_path
from entities.game_object import GameObject


class Can(GameObject):

    FRAME_DELAY   = 8
    IDLE_FRAMES   = 3
    KNOCK_FRAMES  = 5
    SCALE         = 1.5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._origin_x = x
        self._origin_y = y
        self.knocked     = False
        self.anim_frame  = 0
        self.anim_timer  = 0

        # Moving can support (level 4)
        self._move_waypoints = []   # list of (x, y) targets
        self._move_speed     = 0.0
        self._move_wp_idx    = 0

        def load_sheet(path, frames):
            sheet = pygame.image.load(path).convert_alpha()
            fw = sheet.get_width() // frames
            fh = sheet.get_height()
            sw, sh = int(fw * self.SCALE), int(fh * self.SCALE)
            return [pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, fh)), (sw, sh))
                    for i in range(frames)]

        self.frames_idle  = load_sheet(resource_path("ASSETS/CAN/lata knocked v2 (1).png"), self.IDLE_FRAMES)
        self.frames_knock = load_sheet(resource_path("ASSETS/CAN/lata knocked.png"),        self.KNOCK_FRAMES)
        fw = self.frames_idle[0].get_width()
        fh = self.frames_idle[0].get_height()
        self.rect = pygame.Rect(x, y, fw, fh)
        self.mask = pygame.mask.from_surface(self.frames_idle[0])

    def set_patrol(self, waypoints, speed):
        """Enable vertical (or any) patrol movement for this can."""
        self._move_waypoints           = list(waypoints)
        self._move_speed               = speed
        self._move_wp_idx              = 0
        self._patrol_waypoints_default = list(waypoints)
        self._patrol_speed_default     = speed

    def clear_patrol(self):
        """Remove patrol — used when entering a non-moving-can level."""
        self._move_waypoints = []
        self._move_speed     = 0.0
        self._move_wp_idx    = 0
        self._patrol_waypoints_default = []
        self._patrol_speed_default     = 0.0

    def hit(self):
        if not self.knocked:
            self.knocked    = True
            self.anim_frame = 0
            self.anim_timer = 0

    # ── Method Overriding (GameObject.update) ───────────────────────────────
    def update(self, **kwargs):
        """Override: advance knock animation and patrol movement."""
        # Patrol movement when not knocked
        if not self.knocked and self._move_waypoints:
            tx, ty = self._move_waypoints[self._move_wp_idx]
            dx = tx - self.x
            dy = ty - self.y
            import math
            dist = math.hypot(dx, dy)
            if dist < self._move_speed:
                self.x = float(tx)
                self.y = float(ty)
                self._move_wp_idx = (self._move_wp_idx + 1) % len(self._move_waypoints)
            else:
                self.x += (dx / dist) * self._move_speed
                self.y += (dy / dist) * self._move_speed
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

        if not self.knocked:
            return
        self.anim_timer += 1
        if self.anim_timer >= self.FRAME_DELAY:
            self.anim_timer = 0
            if self.anim_frame < self.KNOCK_FRAMES - 1:
                self.anim_frame += 1

    # ── Method Overriding (GameObject.interact) ──────────────────────────────
    def interact(self, other=None):
        """Override: can reacts to being hit — triggers knock animation."""
        self.hit()

    def reset(self):
        self.knocked     = False
        self.anim_frame  = 0
        # Reset position
        self.x = float(self._origin_x)
        self.y = float(self._origin_y)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        # Restore patrol if one was set — so moving can resumes after reset
        if hasattr(self, '_patrol_waypoints_default') and self._patrol_waypoints_default:
            self._move_waypoints = list(self._patrol_waypoints_default)
            self._move_speed     = self._patrol_speed_default
            self._move_wp_idx    = 0
        else:
            self._move_waypoints = []
            self._move_speed     = 0.0
            self._move_wp_idx    = 0

    # ── Method Overriding (GameObject.draw) ─────────────────────────────────
    def draw(self, surface):
        """Override: render idle or knocked animation frame."""
        if self.knocked:
            frame = self.frames_knock[self.anim_frame]
        else:
            frame = self.frames_idle[0]
        surface.blit(frame, (self.x, self.y))
