import pygame
from resource_path import resource_path
from entities.game_object import GameObject


# Sprite sheet paths per character index.
# Drop the named files into ASSETS/PLAYER/ and they will be picked up automatically.
# When a file is absent the loader falls back to Jose's existing working assets.
CHARACTER_SHEETS = {
    0: {  # Jose — uses existing working assets via fallback
        "right": "ASSETS/PLAYER/jose_right.png",
        "up":    "ASSETS/PLAYER/jose_up.png",
        "down":  "ASSETS/PLAYER/jose_down.png",
        "throw": "ASSETS/PLAYER/jose_throw.png",
    },
    1: {  # Bong
        "right": "ASSETS/PLAYER/bong_horizontal.png",
        "up":    "ASSETS/PLAYER/bong_upward.png",
        "down":  "ASSETS/PLAYER/bong_downward.png",
        "throw": "ASSETS/PLAYER/bong_throw.png",
    },
    2: {  # Maria
        "right": "ASSETS/PLAYER/maria_horizontal.png",
        "up":    "ASSETS/PLAYER/maria_upward.png",
        "down":  "ASSETS/PLAYER/maria_downward.png",
        "throw": "ASSETS/PLAYER/maria_throw.png",
    },
    3: {  # Guard
        "right": "ASSETS/PLAYER/guard walking (1).png",
        "up":    "ASSETS/PLAYER/guard upward (1).png",
        "down":  "ASSETS/PLAYER/guard downward (1).png",
        "throw": "ASSETS/PLAYER/guard rotation (2).png",
    },
}

# Fallback paths — Jose's existing working assets used when a named file is absent.
_JOSE_FALLBACK = {
    "right": "ASSETS/PLAYER/59c4581d-e891-4fba-a679-041e4ac54a34-removebg-preview.png",
    "up":    "ASSETS/PLAYER/upward walk.png",
    "down":  "ASSETS/PLAYER/downward walk.png",
    "throw": "ASSETS/PLAYER/throw.png",
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

        # Target height — match Jose's existing sprite height after 2x scale
        # Jose's sheets are 68px tall → rendered at 68*2 = 136px
        JOSE_H = 68
        TARGET_H = int(JOSE_H * self.SCALE)

        def load_sheet(path):
            sheet = pygame.image.load(resource_path(path)).convert_alpha()
            sh = sheet.get_height()
            # Detect frame count: width must divide evenly — try common counts
            sw_raw = sheet.get_width()
            # frame count = width / height (square frames), clamped to reality
            frames = round(sw_raw / sh) if sh > 0 else 6
            frames = max(1, frames)
            fw = sw_raw // frames
            # Scale so height matches Jose's target height
            scale = TARGET_H / sh if sh > 0 else self.SCALE
            dsw, dsh = int(fw * scale), int(sh * scale)
            return [pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, sh)), (dsw, dsh))
                    for i in range(frames)]

        def load_sheet_with_fallback(key):
            """Try the character-specific path; fall back to Jose's working asset."""
            try:
                return load_sheet(sheets[key])
            except (FileNotFoundError, pygame.error):
                return load_sheet(_JOSE_FALLBACK[key])

        self.frames_right = load_sheet_with_fallback("right")
        self.frames_up    = load_sheet_with_fallback("up")
        self.frames_down  = load_sheet_with_fallback("down")
        self.frames_throw = load_sheet_with_fallback("throw")
        self.frame_w = self.frames_right[0].get_width()
        self.frame_h = self.frames_right[0].get_height()
        self.rect    = pygame.Rect(self.x, self.y, self.frame_w, self.frame_h)

        # Some character throw sheets face left by default — flip them on load
        # Character indices whose throw sheet faces left: 2 (Maria)
        _throw_faces_left = {2}
        if character in _throw_faces_left:
            self.frames_throw = [pygame.transform.flip(f, True, False) for f in self.frames_throw]

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
        prev_dir = self._move_dir
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

        # reset frame counter when switching direction to avoid out-of-range index
        if self._move_dir != prev_dir:
            self.anim_frame = 0

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
        # Only advance animation timer when actually moving or throwing
        if not self.moving and not self.is_throwing:
            self.anim_frame = 0
            self.anim_timer = 0
            return
        self.anim_timer += 1
        if self.anim_timer >= self.FRAME_DELAY:
            self.anim_timer = 0
            self.anim_frame += 1
            if self.is_throwing:
                if self.anim_frame >= len(self.frames_throw):
                    self.is_throwing = False
                    self.anim_frame  = 0
            else:
                # wrap based on actual frame count of the current walk direction
                if self._move_dir == "up":
                    self.anim_frame %= len(self.frames_up)
                elif self._move_dir == "down":
                    self.anim_frame %= len(self.frames_down)
                else:
                    self.anim_frame %= len(self.frames_right)
                
    def draw(self, surface):
        self._update_anim()
        if self.is_throwing:
            frame_list = self.frames_throw
        elif self.moving:
            if self._move_dir == "up":
                frame_list = self.frames_up
            elif self._move_dir == "down":
                frame_list = self.frames_down
            else:
                frame_list = self.frames_right
        else:
            frame_list = self.frames_right
        # clamp anim_frame to the actual length of the current strip
        idx = self.anim_frame % len(frame_list)
        frame = frame_list[idx]
        if not self.facing_right and not self.is_throwing:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (self.x, self.y))
