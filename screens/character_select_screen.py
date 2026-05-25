import pygame
import math
from resource_path import resource_path


CHARACTERS = [
    {"name": "JOSE"},
    {"name": "BONG"},
    {"name": "MARIA"},
    {"name": "GUARD"},
]

# Normal card dimensions
CARD_W  = 100
CARD_H  = 150
# Hovered card dimensions
HOV_W   = 120
HOV_H   = 180
# Gap between cards
GAP     = 28
# Vertical center for cards
CARD_Y  = 390


class CharacterSelectScreen:

    def __init__(self, game):
        self.game    = game
        self.assets  = game.assets
        self.selected = 0
        self.hovered  = -1        # which card the mouse is over
        self._hover_angle = 0.0

        self.name_font     = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 20)
        self.name_font_hov = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 26)
        self.hint_font     = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 14)

        self._left_held  = False
        self._right_held = False
        self._space_held = True

        # backdrop — load once, scale per use
        self._raw_backdrop = pygame.image.load(resource_path("ASSETS/CHARACTER/Group 144.png")).convert_alpha()

        # board — load once, scale per use
        self._raw_board = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()

        # player portrait — forward facing frame 0
        sheet = pygame.image.load(resource_path("ASSETS/PLAYER/downward walk.png")).convert_alpha()
        fw = sheet.get_width() // 6
        fh = sheet.get_height()
        self._raw_portrait = sheet.subsurface((0, 0, fw, fh)).copy()

        self.padlock = self.assets.padlock

        # pre-scale normal sizes
        self._bd_normal  = pygame.transform.scale(self._raw_backdrop, (CARD_W - 24, CARD_H - 44))
        self._bd_hov     = pygame.transform.scale(self._raw_backdrop, (HOV_W  - 24, HOV_H  - 44))

        # board scaled to match card sizes (width forced narrower than natural aspect)
        self._board_normal = pygame.transform.scale(self._raw_board, (CARD_W + 14, CARD_H + 14))
        self._board_hov    = pygame.transform.scale(self._raw_board, (HOV_W  + 14, HOV_H  + 14))

        fw2 = self._raw_portrait.get_width()
        fh2 = self._raw_portrait.get_height()
        sc_n = min((CARD_W - 10) / fw2, (CARD_H - 20) / fh2)
        sc_h = min((HOV_W  - 10) / fw2, (HOV_H  - 30) / fh2)
        self._portrait_normal = pygame.transform.scale(self._raw_portrait, (int(fw2 * sc_n), int(fh2 * sc_n)))
        self._portrait_hov    = pygame.transform.scale(self._raw_portrait, (int(fw2 * sc_h), int(fh2 * sc_h)))

        # compute total width and starting x so cards are centered
        total_w = 4 * CARD_W + 3 * GAP
        self._start_x = (800 - total_w) // 2

    def reset_input(self):
        self._space_held = True
        self._left_held  = False
        self._right_held = False

    def _card_cx(self, index):
        return self._start_x + CARD_W // 2 + index * (CARD_W + GAP)

    def _card_rect(self, index):
        cx = self._card_cx(index)
        return pygame.Rect(cx - CARD_W // 2, CARD_Y - CARD_H // 2, CARD_W, CARD_H)

    def _outlined(self, font, text, color, outline=(0, 0, 0)):
        base = font.render(text, True, color)
        w, h = base.get_width() + 2, base.get_height() + 2
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    surf.blit(font.render(text, True, outline), (dx + 1, dy + 1))
        surf.blit(base, (1, 1))
        return surf

    def update(self, mouse_pos, clicked):
        keys = pygame.key.get_pressed()
        mx, my = mouse_pos

        # detect which card is hovered by mouse
        self.hovered = -1
        for i in range(len(CHARACTERS)):
            if self._card_rect(i).collidepoint(mx, my):
                self.hovered = i
                break

        # keyboard navigation selects
        if keys[pygame.K_LEFT] and not self._left_held:
            self.selected = (self.selected - 1) % len(CHARACTERS)
            self._hover_angle = 0.0
        self._left_held = keys[pygame.K_LEFT]

        if keys[pygame.K_RIGHT] and not self._right_held:
            self.selected = (self.selected + 1) % len(CHARACTERS)
            self._hover_angle = 0.0
        self._right_held = keys[pygame.K_RIGHT]

        # mouse click selects
        if clicked and self.hovered >= 0:
            self.selected = self.hovered
            self._hover_angle = 0.0

        space_or_enter = keys[pygame.K_SPACE] or keys[pygame.K_RETURN]
        if space_or_enter and not self._space_held:
            if self.game.manager.is_character_unlocked(self.selected):
                self._confirm()
        self._space_held = space_or_enter

        if keys[pygame.K_ESCAPE]:
            self.game.manager.change_state("menu")

        self._hover_angle += 2.5

    def _confirm(self):
        self.game.manager.selected_character = self.selected
        self.game.manager.change_state("level_select")

    def draw(self, surface):
        a = self.assets
        surface.blit(a.esc_banner, (8, 8))
        surface.blit(a.title, a.title.get_rect(center=(400, 110)))

        # active card = only when mouse is hovering over a card
        active = self.hovered  # -1 means nothing active

        for i, char in enumerate(CHARACTERS):
            is_active = (i == active)
            cx = self._card_cx(i)
            locked = not self.game.manager.is_character_unlocked(i)

            if is_active:
                cw, ch, cy = HOV_W, HOV_H, CARD_Y - 10
                board    = self._board_hov
                backdrop = self._bd_hov
                portrait = self._portrait_hov
            else:
                cw, ch, cy = CARD_W, CARD_H, CARD_Y
                board    = self._board_normal
                backdrop = self._bd_normal
                portrait = self._portrait_normal

            # draw order: board first (bamboo frame + dark interior)
            # then backdrop covers the dark interior
            # then portrait on top of backdrop
            surface.blit(board, board.get_rect(center=(cx, cy)))
            surface.blit(backdrop, backdrop.get_rect(center=(cx, cy - 8)))

            # portrait or padlock
            if locked:
                pl = self.padlock
                surface.blit(pl, pl.get_rect(center=(cx, cy - 12)))
            else:
                if is_active:
                    angle = math.sin(math.radians(self._hover_angle)) * 10
                    rotated = pygame.transform.rotate(portrait, angle)
                    surface.blit(rotated, rotated.get_rect(center=(cx, cy - 18)))
                else:
                    surface.blit(portrait, portrait.get_rect(center=(cx, cy - 12)))

            # name
            if is_active:
                name_surf = self._outlined(self.name_font_hov, char["name"], (255, 255, 255))
                # inside card at bottom
                surface.blit(name_surf, name_surf.get_rect(center=(cx, cy + ch // 2 - 20)))
            else:
                name_surf = self._outlined(self.name_font, char["name"], (200, 200, 200))
                # below card
                surface.blit(name_surf, name_surf.get_rect(center=(cx, cy + ch // 2 + 14)))

        hint = self._outlined(self.hint_font,
                              "ARROW KEYS or CLICK to select   |   SPACE / ENTER to confirm",
                              (180, 180, 180))
        surface.blit(hint, hint.get_rect(center=(400, 570)))
