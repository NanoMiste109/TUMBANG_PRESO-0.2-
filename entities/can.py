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
        self.knocked     = False
        self.anim_frame  = 0
        self.anim_timer  = 0

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

    def hit(self):
        if not self.knocked:
            self.knocked    = True
            self.anim_frame = 0
            self.anim_timer = 0

    # ── Method Overriding (GameObject.update) ───────────────────────────────
    def update(self, **kwargs):
        """Override: advance knock animation frame."""
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
        self.knocked    = False
        self.anim_frame = 0
        
    # ── Method Overriding (GameObject.draw) ─────────────────────────────────
    def draw(self, surface):
        """Override: render idle or knocked animation frame."""
        if self.knocked:
            frame = self.frames_knock[self.anim_frame]
        else:
            frame = self.frames_idle[0]
        surface.blit(frame, (self.x, self.y))
