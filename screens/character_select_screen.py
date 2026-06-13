import pygame
import math
from resource_path import resource_path
from utils.text import TextProvider
from entities.character import character_from_index


CHARACTERS = [
    {"name": "JOSE"},
    {"name": "BONG"},
    {"name": "MARIA"},
]

SLIPPER_NAMES = ["Default", "Rocket", "Triple", "Bolt"]
SLIPPER_PATHS = [
    "ASSETS/SLIPPER/slipper.png",
    "ASSETS/SLIPPER/slipper_v2.png",
    "ASSETS/SLIPPER/slipper_v3.png",
    "ASSETS/SLIPPER/slipper_v4.png",
]
SLIPPER_DESCS = [
    "No special ability.",
    "Press G mid-flight to\ndouble the slipper's speed.",
    "Press G mid-flight to\nspawn 2 extra slippers\nin spread directions.",
    "Hit a guard to stun them\nfor 3 seconds instead of\ntaking a miss penalty.",
]

# Normal card dimensions
CARD_W  = 100
CARD_H  = 150
# Hovered card dimensions
HOV_W   = 120
HOV_H   = 180
# Gap between cards
GAP     = 28
# Vertical center for cards — moved up to create space for slipper row
CARD_Y  = 340


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
        self.skill_title_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 17)
        self.skill_desc_font  = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 13)

        self._left_held  = False
        self._right_held = False
        self._space_held = True

        # backdrop — load once, scale per use
        self._raw_backdrop = pygame.image.load(resource_path("ASSETS/CHARACTER/Group 144.png")).convert_alpha()

        from entities.player import CHARACTER_SHEETS, _JOSE_FALLBACK

        # board — load once, scale per use
        self._raw_board = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()

        # Per-character portraits — frame 0 of the "down" spritesheet
        # Falls back to Jose's downward walk if the file is absent
        JOSE_H = 68
        TARGET_H = JOSE_H * 2  # match in-game sprite height

        def _load_portrait(char_idx):
            path = CHARACTER_SHEETS.get(char_idx, CHARACTER_SHEETS[0]).get("down")
            try:
                sheet = pygame.image.load(resource_path(path)).convert_alpha()
            except Exception:
                sheet = pygame.image.load(resource_path(_JOSE_FALLBACK["down"])).convert_alpha()
            sh = sheet.get_height()
            sw = sheet.get_width()
            frames = round(sw / sh) if sh > 0 else 6
            frames = max(1, frames)
            fw = sw // frames
            scale = TARGET_H / sh if sh > 0 else 1.0
            dw, dh = int(fw * scale), int(sh * scale)
            raw = sheet.subsurface((0, 0, fw, sh)).copy()
            return pygame.transform.scale(raw, (dw, dh))

        # Load one portrait per character
        self._raw_portraits = [_load_portrait(i) for i in range(len(CHARACTERS))]

        self.padlock = self.assets.padlock

        # pre-scale normal sizes
        self._bd_normal  = pygame.transform.scale(self._raw_backdrop, (CARD_W - 24, CARD_H - 44))
        self._bd_hov     = pygame.transform.scale(self._raw_backdrop, (HOV_W  - 24, HOV_H  - 44))

        # board scaled to match card sizes (width forced narrower than natural aspect)
        self._board_normal = pygame.transform.scale(self._raw_board, (CARD_W + 14, CARD_H + 14))
        self._board_hov    = pygame.transform.scale(self._raw_board, (HOV_W  + 14, HOV_H  + 14))

        # Pre-scale portraits for each character at normal and hovered sizes
        self._portraits_normal = []
        self._portraits_hov    = []
        for raw in self._raw_portraits:
            fw2, fh2 = raw.get_width(), raw.get_height()
            sc_n = min((CARD_W - 10) / fw2, (CARD_H - 20) / fh2)
            sc_h = min((HOV_W  - 10) / fw2, (HOV_H  - 30) / fh2)
            self._portraits_normal.append(pygame.transform.scale(raw, (int(fw2 * sc_n), int(fh2 * sc_n))))
            self._portraits_hov.append(pygame.transform.scale(raw, (int(fw2 * sc_h), int(fh2 * sc_h))))

        # compute total width and starting x so 3 cards are centered
        total_w = 3 * CARD_W + 2 * GAP
        self._start_x = (800 - total_w) // 2

        # Slipper selector — small previews below cards
        self._slipper_font  = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 13)
        self._slipper_imgs  = []
        SLIP_SIZE = 40  # fit inside the 44px circle
        for path in SLIPPER_PATHS:
            try:
                img = pygame.image.load(resource_path(path)).convert_alpha()
                fh = img.get_height()
                fw = fh  # square frame
                frame = img.subsurface((0, 0, fw, fh)).copy()
                frame = pygame.transform.scale(frame, (SLIP_SIZE, SLIP_SIZE))
            except Exception:
                frame = pygame.Surface((SLIP_SIZE, SLIP_SIZE), pygame.SRCALPHA)
            self._slipper_imgs.append(frame)
        self._hovered_slipper = -1

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

        # mouse click selects (only if unlocked)
        if clicked and self.hovered >= 0:
            if self.game.manager.is_character_unlocked(self.hovered):
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

        # Slipper selector — click to equip
        SLIP_Y = 510
        SLIP_GAP = 56
        slip_start_x = 400 - (len(SLIPPER_PATHS) * SLIP_GAP) // 2 + SLIP_GAP // 2
        self._hovered_slipper = -1
        for i in range(len(SLIPPER_PATHS)):
            sx = slip_start_x + i * SLIP_GAP
            slip_rect = pygame.Rect(sx - 22, SLIP_Y - 22, 44, 44)
            if slip_rect.collidepoint(mx, my):
                self._hovered_slipper = i
                if clicked and self.game.manager.is_slipper_unlocked(i):
                    self.game.manager.selected_slipper = i

    def _confirm(self):
        self.game.manager.selected_character = self.selected
        self.game.manager.change_state("level_select")

    def _find_achievement_for_character(self, char_idx):
        """Return the AchievementDef whose unlocks_character == char_idx, or None."""
        for ach in self.game.achievements.defs.values():
            if ach.unlocks_character == char_idx:
                return ach
        return None

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
                portrait = self._portraits_hov[i]
            else:
                cw, ch, cy = CARD_W, CARD_H, CARD_Y
                board    = self._board_normal
                backdrop = self._bd_normal
                portrait = self._portraits_normal[i]

            # draw order: board first (bamboo frame + dark interior)
            # then backdrop covers the dark interior
            # then portrait on top of backdrop
            surface.blit(board, board.get_rect(center=(cx, cy)))
            surface.blit(backdrop, backdrop.get_rect(center=(cx, cy - 8)))

            # portrait or padlock
            if locked:
                pl = self.padlock
                surface.blit(pl, pl.get_rect(center=(cx, cy - 12)))
                # unlock hint when hovered
                if i == self.hovered:
                    ach = self._find_achievement_for_character(i)
                    lang = self.game.manager.settings.get("LANGUAGE", "EN")
                    hint_text = ach.description if ach else TextProvider.get("charselect.locked_hint", lang)
                    hint_surf = self._outlined(self.hint_font, hint_text, (255, 220, 80))
                    surface.blit(hint_surf, hint_surf.get_rect(center=(cx, cy + ch // 2 + 30)))
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

        lang = self.game.manager.settings.get("LANGUAGE", "EN")
        hint = self._outlined(self.hint_font,
                              TextProvider.get("charselect.hint", lang),
                              (180, 180, 180))
        surface.blit(hint, hint.get_rect(center=(400, 556)))

        # Slipper selector row
        self._draw_slipper_row(surface)

        # Hover info card — shows skill info above the hovered card (unlocked only)
        if self.hovered >= 0 and self.game.manager.is_character_unlocked(self.hovered):
            self._draw_skill_card(surface, self.hovered)

    def _draw_skill_card(self, surface, char_idx):
        """Draw a small info card above the hovered character card."""
        char_obj = character_from_index(char_idx)
        cx = self._card_cx(char_idx)

        skill_name = char_obj.SKILL_NAME or "No Special"
        desc = char_obj.SKILL_DESC or ""

        # Word-wrap description to fit within max_w pixels
        max_w = 200
        words = desc.split()
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if self.skill_desc_font.size(test)[0] <= max_w - 12:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        # Measure card dimensions based on actual content
        name_surf = self._outlined(self.skill_title_font, skill_name, (255, 220, 80))
        line_surfs = [self._outlined(self.skill_desc_font, l, (220, 220, 220)) for l in lines]

        all_w = max([name_surf.get_width()] + [s.get_width() for s in line_surfs])
        card_w = max(160, all_w + 20)
        line_h = self.skill_desc_font.get_height() + 3
        card_h = 14 + name_surf.get_height() + 6 + line_h * len(lines) + 8

        card_x = cx - card_w // 2
        card_y = CARD_Y - CARD_H // 2 - card_h - 10

        # Keep card within screen bounds horizontally
        card_x = max(4, min(card_x, 800 - card_w - 4))

        # Background + border
        bg = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 190))
        surface.blit(bg, (card_x, card_y))
        pygame.draw.rect(surface, (180, 140, 80), (card_x, card_y, card_w, card_h), 2)

        # Skill name
        card_cx = card_x + card_w // 2
        y = card_y + 8
        surface.blit(name_surf, name_surf.get_rect(centerx=card_cx, y=y))
        y += name_surf.get_height() + 6

        # Description lines
        for ls in line_surfs:
            surface.blit(ls, ls.get_rect(centerx=card_cx, y=y))
            y += line_h

    def _draw_slipper_row(self, surface):
        """Draw the slipper selection row below the character cards."""
        SLIP_Y    = 510  # pushed lower for breathing room
        SLIP_GAP  = 56
        n         = len(SLIPPER_PATHS)
        start_x   = 400 - (n * SLIP_GAP) // 2 + SLIP_GAP // 2
        selected  = self.game.manager.selected_slipper

        # Label
        lbl = self._outlined(self._slipper_font, "SLIPPER", (200, 200, 200))
        surface.blit(lbl, lbl.get_rect(center=(400, SLIP_Y - 32)))

        for i, img in enumerate(self._slipper_imgs):
            sx = start_x + i * SLIP_GAP
            unlocked = self.game.manager.is_slipper_unlocked(i)
            slip_rect = pygame.Rect(sx - 22, SLIP_Y - 22, 44, 44)

            # Background circle
            bg_color = (80, 160, 80) if i == selected else (40, 40, 40)
            pygame.draw.circle(surface, bg_color, (sx, SLIP_Y), 22)

            # Border
            border_col = (255, 220, 80) if i == selected else (
                (140, 200, 140) if self._hovered_slipper == i else (80, 80, 80)
            )
            pygame.draw.circle(surface, border_col, (sx, SLIP_Y), 22, 2)

            if unlocked:
                # index 1 (Rocket) sprite sits low in the frame — nudge it up
                y_offset = -4 if i == 1 else 0
                surface.blit(img, img.get_rect(center=(sx, SLIP_Y + y_offset)))
            else:
                # Padlock for locked slippers
                pl = pygame.transform.scale(self.padlock, (28, 28))
                surface.blit(pl, pl.get_rect(center=(sx, SLIP_Y)))
                # Dim overlay
                dim = pygame.Surface((44, 44), pygame.SRCALPHA)
                dim.fill((0, 0, 0, 120))
                surface.blit(dim, slip_rect)

            # Name label below
            name_col = (255, 255, 255) if unlocked else (100, 100, 100)
            name_s = self._outlined(self._slipper_font, SLIPPER_NAMES[i], name_col)
            surface.blit(name_s, name_s.get_rect(center=(sx, SLIP_Y + 28)))

        # Slipper ability tooltip on hover
        if self._hovered_slipper >= 0:
            hi = self._hovered_slipper
            is_unlocked = self.game.manager.is_slipper_unlocked(hi)
            lines = SLIPPER_DESCS[hi].split("\n") if is_unlocked else ["Clear the required level", "to unlock this slipper."]
            line_h = self._slipper_font.get_height() + 2
            tip_w = max(self._slipper_font.size(l)[0] for l in lines) + 16
            tip_h = line_h * len(lines) + 10
            sx = start_x + hi * SLIP_GAP
            tip_x = max(4, min(sx - tip_w // 2, 800 - tip_w - 4))
            tip_y = SLIP_Y - 32 - tip_h
            bg = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 190))
            surface.blit(bg, (tip_x, tip_y))
            pygame.draw.rect(surface, (180, 140, 80), (tip_x, tip_y, tip_w, tip_h), 1)
            for li, line in enumerate(lines):
                ls = self._outlined(self._slipper_font, line, (220, 220, 220))
                surface.blit(ls, ls.get_rect(centerx=tip_x + tip_w // 2, y=tip_y + 5 + li * line_h))
