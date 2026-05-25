import pygame
from resource_path import resource_path
from entities.game_object import GameObject


# Sprite sheet paths per character index.
# Replace the placeholder paths with real assets when they're ready.
CHARACTER_SHEETS = {
    0: {  # Jose — current character
        "right": "ASSETS/PLAYER/59c4581d-e891-4fba-a679-041e4ac54a34-removebg-preview.png",
        "up":    "ASSETS/PLAYER/upward walk.png",
        "down":  "ASSETS/PLAYER/downward walk.png",
        "throw": "ASSETS/PLAYER/throw.png",
    },
    1: {  # Maria — placeholder (reuses Jose until assets arrive)
        "right": "ASSETS/PLAYER/59c4581d-e891-4fba-a679-041e4ac54a34-removebg-preview.png",
        "up":    "ASSETS/PLAYER/upward walk.png",
        "down":  "ASSETS/PLAYER/downward walk.png",
        "throw": "ASSETS/PLAYER/throw.png",
    },
    2: {  # Bong — placeholder
        "right": "ASSETS/PLAYER/59c4581d-e891-4fba-a679-041e4ac54a34-removebg-preview.png",
        "up":    "ASSETS/PLAYER/upward walk.png",
        "down":  "ASSETS/PLAYER/downward walk.png",
        "throw": "ASSETS/PLAYER/throw.png",
    },
    3: {  # Guard — placeholder
        "right": "ASSETS/PLAYER/59c4581d-e891-4fba-a679-041e4ac54a34-removebg-preview.png",
        "up":    "ASSETS/PLAYER/upward walk.png",
        "down":  "ASSETS/PLAYER/downward walk.png",
        "throw": "ASSETS/PLAYER/throw.png",
    },
}


class Player(GameObject):

    SCALE       = 2.0
    Y_MIN       = 280
    X_MAX       = 310
    LINE_X_BOTTOM = 280
    LINE_X_TOP    = 340
    LINE_Y_BOTTOM = 600
    LINE_Y_TOP    = 355
    FRAME_DELAY = 6
    FOOT_OFFSET = 14

    def __init__(self, x, y, character=0):
        self.x = x
        self.y = y
        self.speed = 4
        self.facing_right = True
        self.moving       = False
        self.is_throwing  = False
        self.anim_frame   = 0
        self.anim_timer   = 0
        self._move_dir    = "right"

        sheets = CHARACTER_SHEETS.get(character, CHARACTER_SHEETS[0])

        def load_sheet(path, frames):
            sheet = pygame.image.load(resource_path(path)).convert_alpha()
            fw = sheet.get_width() // frames
            fh = sheet.get_height()
            sw, sh = int(fw * self.SCALE), int(fh * self.SCALE)
            return [pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, fh)), (sw, sh))
                    for i in range(frames)]

        self.frames_right = load_sheet(sheets["right"], 6)
        self.frames_up    = load_sheet(sheets["up"],    6)
        self.frames_down  = load_sheet(sheets["down"],  6)
        self.frames_throw = load_sheet(sheets["throw"], 6)
        self.frame_w = self.frames_right[0].get_width()
        self.frame_h = self.frames_right[0].get_height()
        self.rect    = pygame.Rect(self.x, self.y, self.frame_w, self.frame_h)

    def throw(self):
        self.is_throwing = True
        self.anim_frame  = 0
        self.anim_timer  = 0

    # ── Method Overloading ───────────────────────────────────────────────────
    # Python doesn't have true overloading, so we use default/optional args.
    # move(keys)       → normal keyboard-driven movement (gameplay)
    # move(dx=n, dy=n) → scripted/direct movement (cutscenes, testing)
    def move(self, keys=None, *, dx=None, dy=None):
        """
        Overloaded move:
          move(keys)        — reads arrow-key input, applies boundary limits
          move(dx=n, dy=n)  — moves by an explicit delta (no key input needed)
        """
        if dx is not None or dy is not None:
            # ── scripted movement branch ──
            if dx is not None:
                self.x = max(0, min(self.x + dx, self.X_MAX - self.frame_w))
                self.facing_right = dx >= 0
            if dy is not None:
                self.y = max(self.Y_MIN, min(self.y + dy, 600 - self.frame_h + self.FOOT_OFFSET))
            self.moving = True
            self.rect.topleft = (self.x, self.y)
            return

        # ── keyboard-driven movement branch ──
        self.moving = False
        if keys[pygame.K_UP] and self.y > self.Y_MIN:
            self.y -= self.speed
            self.moving    = True
            self._move_dir = "up"

        elif keys[pygame.K_DOWN] and self.y < 600 - self.frame_h + self.FOOT_OFFSET:
            self.y += self.speed
            self.moving    = True
            self._move_dir = "down"

        elif keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
            self.moving       = True
            self.facing_right = False
            self._move_dir    = "left"

        elif keys[pygame.K_RIGHT] and self.x + self.frame_w < self.X_MAX:
            self.x += self.speed
            self.moving       = True
            self.facing_right = True
            self._move_dir    = "right"

        if self.x + self.frame_w > self.X_MAX:
            self.x = self.X_MAX - self.frame_w
        self.rect.topleft = (self.x, self.y)

    # ── Method Overriding (GameObject.update) ───────────────────────────────
    def update(self, keys=None, **kwargs):
        """Override: advance animation state. Movement is driven by move()."""
        self._update_anim()

    # ── Method Overriding (GameObject.interact) ──────────────────────────────
    def interact(self, other=None):
        """Override: player reacts to hitting the can by triggering throw anim."""
        if other is not None:
            self.throw()

    def _update_anim(self):
        self.anim_timer += 1
        if self.anim_timer >= self.FRAME_DELAY:
            self.anim_timer = 0
            self.anim_frame += 1
            if self.is_throwing:
                if self.anim_frame >= len(self.frames_throw):
                    self.is_throwing = False
                    self.anim_frame  = 0
            else:
                self.anim_frame %= 6
                
    def draw(self, surface):
        self._update_anim()
        if self.is_throwing:
            frame = self.frames_throw[self.anim_frame]
        elif self.moving:
            if self._move_dir == "up":
                frame = self.frames_up[self.anim_frame]
            elif self._move_dir == "down":
                frame = self.frames_down[self.anim_frame]
            else:
                frame = self.frames_right[self.anim_frame]
        else:
            frame = self.frames_right[0]
        if not self.facing_right and not self.is_throwing:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (self.x, self.y))
