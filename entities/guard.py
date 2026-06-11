import pygame
import math
from resource_path import resource_path
from entities.game_object import GameObject


class Guard(GameObject):

    FRAMES      = 6
    FRAME_DELAY = 7
    SCALE       = 2.0
    SPEED       = 1.8
    WAYPOINTS = [
        (680, 370),
        (680, 540),
        (380, 540),
        (380, 370),
    ]

    def __init__(self, x, y, waypoints=None, speed=1.8):
        if waypoints:
            self.WAYPOINTS = waypoints
        self.SPEED = speed
        self.anim_frame = 0
        self.anim_timer = 0
        self.dir        = 1
        self._move_dir  = "horizontal"
        self._stun_timer = 0   # frames remaining in stun (0 = not stunned)

        def load_sheet(path):
            sheet = pygame.image.load(resource_path(path)).convert_alpha()
            fw = sheet.get_width() // self.FRAMES
            fh = sheet.get_height()
            sw, sh = int(fw * self.SCALE), int(fh * self.SCALE)
            return [pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, fh)), (sw, sh))
                    for i in range(self.FRAMES)]

        self.frames_walk = load_sheet("ASSETS/GUARD/guard walking.png")
        self.frames_up   = load_sheet("ASSETS/GUARD/guard upward.png")
        self.frames_down = load_sheet("ASSETS/GUARD/guard downward.png")

        self.frame_w = self.frames_walk[0].get_width()
        self.frame_h = self.frames_walk[0].get_height()
        self.x = float(self.WAYPOINTS[0][0]) - self.frame_w // 2
        self.y = float(self.WAYPOINTS[0][1])
        self.wp_index = 1
        self.rect = pygame.Rect(int(self.x), int(self.y), self.frame_w, self.frame_h)
        # Initialise mask so mask_hit() works before the first update() call
        self.mask = pygame.mask.from_surface(self.frames_walk[0])

    def stun(self, frames: int = 180):
        """Freeze the guard for the given number of frames."""
        self._stun_timer = frames

    @property
    def is_stunned(self) -> bool:
        return self._stun_timer > 0

    # ── Method Overriding (GameObject.update) ───────────────────────────────
    def update(self, player=None, **kwargs):
        """Override: patrol waypoints and advance animation. Pauses when stunned."""
        if self._stun_timer > 0:
            self._stun_timer -= 1
            return  # frozen

        tx, ty = self.WAYPOINTS[self.wp_index]
        cx = self.x + self.frame_w // 2
        dx = tx - cx
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < self.SPEED:
            self.x = float(tx) - self.frame_w // 2
            self.y = float(ty)
            self.wp_index = (self.wp_index + 1) % len(self.WAYPOINTS)
        else:
            self.x += (dx / dist) * self.SPEED
            self.y += (dy / dist) * self.SPEED
            self.dir = 1 if dx > 0 else -1
            if abs(dy) > abs(dx):
                self._move_dir = "down" if dy > 0 else "up"
            else:
                self._move_dir = "horizontal"
        self.rect.x = int(self.x)
        self.rect.y = int(self.y) - self.frame_h
        self.mask = pygame.mask.from_surface(self.frames_walk[self.anim_frame])
        self.anim_timer += 1
        if self.anim_timer >= self.FRAME_DELAY:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % self.FRAMES

    # ── Method Overriding (GameObject.draw) ─────────────────────────────────
    def draw(self, surface):
        """Override: render guard sprite based on current movement direction."""
        if self._move_dir == "up":
            frame = self.frames_up[self.anim_frame]
        elif self._move_dir == "down":
            frame = self.frames_down[self.anim_frame]
        else:
            frame = self.frames_walk[self.anim_frame]
            if self.dir < 0:
                frame = pygame.transform.flip(frame, True, False)
        draw_y = int(self.y) - self.frame_h + 20
        surface.blit(frame, (int(self.x), draw_y))
        
    # ── Method Overriding (GameObject.interact) ──────────────────────────────
    def interact(self, other=None):
        """Override: guard reacts to being hit by a slipper."""
        pass  # stun is applied externally via guard.stun()

    def _draw_path(self, surface):
        pts = self.WAYPOINTS
        for i in range(len(pts)):
            a = pts[i]
            b = pts[(i + 1) % len(pts)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            dist = math.hypot(dx, dy)
            steps = int(dist / 12)
            for s in range(steps):
                t = s / max(steps, 1)
                px = int(a[0] + dx * t)
                py = int(a[1] + dy * t)
                if s % 2 == 0:
                    pygame.draw.circle(surface, (255, 255, 255), (px, py), 2)
