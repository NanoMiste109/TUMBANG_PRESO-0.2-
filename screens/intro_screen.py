import pygame
from resource_path import resource_path


class IntroScreen:
    """
    Phases:
      0 — player walks in from left (black bg)
      1 — throw animation plays, slipper launches
      2 — slipper flies, hits can
      3 — can knocked, title fades in
      4 — hold
      5 — fade out to menu
    """

    SCALE       = 2.5
    FRAME_DELAY = 6

    def __init__(self, game):
        self.game = game

        def load_sheet(path, frames):
            sheet = pygame.image.load(resource_path(path)).convert_alpha()
            fw = sheet.get_width() // frames
            fh = sheet.get_height()
            sw, sh = int(fw * self.SCALE), int(fh * self.SCALE)
            return [pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, fh)), (sw, sh))
                    for i in range(frames)]

        self.frames_walk  = load_sheet("ASSETS/PLAYER/59c4581d-e891-4fba-a679-041e4ac54a34-removebg-preview.png", 6)
        self.frames_throw = load_sheet("ASSETS/PLAYER/throw.png", 6)

        can_sheet = pygame.image.load(resource_path("ASSETS/CAN/lata knocked v2 (1).png")).convert_alpha()
        cfw = can_sheet.get_width() // 3
        cfh = can_sheet.get_height()
        csw, csh = int(cfw * 2.0), int(cfh * 2.0)
        self.can_idle = pygame.transform.scale(can_sheet.subsurface((0, 0, cfw, cfh)), (csw, csh))
        knock_sheet = pygame.image.load(resource_path("ASSETS/CAN/lata knocked.png")).convert_alpha()
        kfw = knock_sheet.get_width() // 5
        kfh = knock_sheet.get_height()
        self.can_knocked = [
            pygame.transform.scale(knock_sheet.subsurface((i*kfw, 0, kfw, kfh)), (csw, csh))
            for i in range(5)
        ]

        sl_sheet = pygame.image.load(resource_path("ASSETS/SLIPPER/slipper.png")).convert_alpha()
        sfw = sl_sheet.get_width() // 4
        sfh = sl_sheet.get_height()
        ssw, ssh = int(sfw * 1.5), int(sfh * 1.5)
        self.slipper_frames = [
            pygame.transform.scale(sl_sheet.subsurface((i*sfw, 0, sfw, sfh)), (ssw, ssh))
            for i in range(4)
        ]

        self.fw = self.frames_walk[0].get_width()
        self.fh = self.frames_walk[0].get_height()

        self.title_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 72)
        self.sub_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 20)

        self._skip_held = False
        self.reset()

    def reset(self):
        self.phase       = 0
        self.anim_frame  = 0
        self.anim_timer  = 0
        self.phase_timer = 0

        self.px = -self.fw
        self.py = 380

        self.can_x = 820   # starts off-screen right
        self.can_y = 390
        self.can_target_x  = 520
        self.can_knocked_frame = 0
        self.can_knocked_timer = 0
        self.can_is_knocked    = False

        self.sl_active = False
        self.sl_x = 0.0
        self.sl_y = 0.0
        self.sl_vx = 0.0
        self.sl_vy = 0.0
        self.sl_frame = 0
        self.sl_timer = 0

        self.title_alpha = 0
        self.fade_out    = 0
        self.hold_timer  = 0
        self._skip_held  = False

    def _advance_anim(self, frames):
        self.anim_timer += 1
        if self.anim_timer >= self.FRAME_DELAY:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(frames)

    def update(self, mouse_pos, clicked):
        keys = pygame.key.get_pressed()
        skip = any([keys[pygame.K_RETURN], keys[pygame.K_SPACE],
                    keys[pygame.K_ESCAPE], clicked])
        if skip and not self._skip_held:
            self._finish()
        self._skip_held = skip

        self.phase_timer += 1

        if self.phase == 0:
            self._advance_anim(self.frames_walk)
            self.px += 3
            if self.can_x > self.can_target_x:
                self.can_x = max(self.can_target_x, self.can_x - 3)
            if self.px >= 180:
                self.px = 180
                self.can_x = self.can_target_x
                self.phase = 1
                self.anim_frame = 0
                self.anim_timer = 0
                self.phase_timer = 0

        elif self.phase == 1:
            self.anim_timer += 1
            if self.anim_timer >= self.FRAME_DELAY:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.frames_throw):
                    self.anim_frame = len(self.frames_throw) - 1
                    if not self.sl_active:
                        self.sl_active = True
                        self.sl_x  = float(self.px + self.fw)
                        self.sl_y  = float(self.py + self.fh // 4)
                        self.sl_vx = 7.0
                        self.sl_vy = -2.5
                    self.phase = 2
                    self.phase_timer = 0

        elif self.phase == 2:
            if self.sl_active:
                self.sl_vy += 0.12
                self.sl_x  += self.sl_vx
                self.sl_y  += self.sl_vy
                self.sl_timer += 1
                if self.sl_timer >= 4:
                    self.sl_timer = 0
                    self.sl_frame = (self.sl_frame + 1) % 4
                if self.sl_x + 20 >= self.can_x and not self.can_is_knocked:
                    self.sl_active      = False
                    self.can_is_knocked = True
                    self.phase          = 3
                    self.phase_timer    = 0

        elif self.phase == 3:
            self.can_knocked_timer += 1
            if self.can_knocked_timer >= 8:
                self.can_knocked_timer = 0
                if self.can_knocked_frame < 4:
                    self.can_knocked_frame += 1
            self.title_alpha = min(255, self.title_alpha + 5)
            if self.phase_timer > 30:
                self.phase = 4
                self.phase_timer = 0

        elif self.phase == 4:
            self.title_alpha = min(255, self.title_alpha + 5)
            self.hold_timer += 1
            if self.hold_timer > 120:
                self.phase = 5

        elif self.phase == 5:
            self.fade_out = min(255, self.fade_out + 5)
            if self.fade_out >= 255:
                self._finish()

    def _finish(self):
        self.game.manager.change_state("menu")

    def draw(self, surface):
        surface.fill((0, 0, 0))

        # can
        frame = self.can_knocked[self.can_knocked_frame] if self.can_is_knocked else self.can_idle
        surface.blit(frame, (self.can_x, self.can_y))

        # slipper
        if self.sl_active:
            surface.blit(self.slipper_frames[self.sl_frame], (int(self.sl_x), int(self.sl_y)))

        # player
        if self.phase == 0:
            p_frame = self.frames_walk[self.anim_frame]
        else:
            idx = min(self.anim_frame, len(self.frames_throw) - 1)
            p_frame = self.frames_throw[idx]
        surface.blit(p_frame, (int(self.px), self.py))

        # title
        if self.phase >= 3 and self.title_alpha > 0:
            title = self.title_font.render("TUMBANG PRESO", True, (255, 220, 50))
            outline = self.title_font.render("TUMBANG PRESO", True, (0, 0, 0))
            title.set_alpha(self.title_alpha)
            outline.set_alpha(self.title_alpha)
            tx = 400 - title.get_width() // 2
            ty = 160
            for dx in (-2, 2):
                for dy in (-2, 2):
                    surface.blit(outline, (tx + dx, ty + dy))
            surface.blit(title, (tx, ty))

            sub = self.sub_font.render("A Filipino Street Game", True, (200, 200, 200))
            sub.set_alpha(self.title_alpha)
            surface.blit(sub, sub.get_rect(center=(400, ty + title.get_height() + 10)))

        # skip hint
        if self.phase < 4:
            hint = self.sub_font.render("Press any key to skip", True, (80, 80, 80))
            surface.blit(hint, hint.get_rect(center=(400, 570)))

        # fade out overlay
        if self.fade_out > 0:
            ov = pygame.Surface((800, 600))
            ov.fill((0, 0, 0))
            ov.set_alpha(self.fade_out)
            surface.blit(ov, (0, 0))
