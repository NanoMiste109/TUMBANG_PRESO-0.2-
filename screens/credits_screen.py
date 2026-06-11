import pygame
from resource_path import resource_path


# Each page is a dict with a title and list of (role_or_label, name) tuples.
# role_or_label = None means render only the name line (used for resource lists).
PAGES = [
    {
        "title": "MAIN TEAM",
        "entries": [
            ("TEAM LEADER",     "Trisha Lagbo"),
            ("GAME DEVELOPER",  "Elgvin Ruiz"),
            ("SPRITE ARTIST",   "Janryl Bautista"),
        ],
    },
    {
        "title": "",  # no title — continuation page
        "subtitle_after": 2,  # insert "ALSO BY" label after entry index 2
        "subtitle": "ALSO BY",
        "entries": [
            ("UI / LEVEL ARTIST", "Braeden Alfonso"),
            ("SFX ARTIST",        "Michael Prande"),
            (None, "Charles Cruz"),
            (None, "Johannes Afable"),
        ],
    },
    {
        "title": "ASSET SOURCES",
        "entries": [
            (None, "Bongseng"),
            (None, "Dream Mix"),
            (None, "Free Game Assets"),
            (None, "GrumpyDiamond"),
        ],
    },
    {
        "title": "ASSET SOURCES",
        "entries": [
            (None, "Karsiori"),
            (None, "Kuramarushka"),
            (None, "Leo Red"),
            (None, "Mewily"),
        ],
    },
    {
        "title": "ASSET SOURCES",
        "entries": [
            (None, "Random Eye Vector"),
            (None, "Sagy"),
            (None, "Scigho"),
            (None, "TheStarvingArtificer"),
            (None, "Tiny Worlds"),
        ],
    },
]

ARROW_SCALE = 0.45


class CreditsScreen:

    def __init__(self, game):
        self.game   = game
        self.assets = game.assets
        self._page  = 0

        board_src = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()
        # Match the mockup — same width as menu, moderate height
        bw = int(board_src.get_width()  * 0.6 * 0.78)
        bh = int(board_src.get_height() * 0.6 * 0.78)
        self.board = pygame.transform.scale(board_src, (bw, bh))
        self.board_rect = self.board.get_rect(center=(400, 360))

        self.role_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 16)
        self.name_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 26)
        self.header_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 34)

        # Arrows — unhovered: plain=right, (3)=left  |  hovered: (1)=right, (2)=left
        def load_arrow(path):
            img = pygame.image.load(resource_path(path)).convert_alpha()
            return pygame.transform.scale(img, (
                int(img.get_width()  * ARROW_SCALE),
                int(img.get_height() * ARROW_SCALE),
            ))

        self._arrow_right_normal  = load_arrow("ASSETS/CREDITS/UNHOVERED/chevron_arrow 1.png")
        self._arrow_left_normal   = load_arrow("ASSETS/CREDITS/UNHOVERED/chevron_arrow 1 (3).png")
        self._arrow_right_hovered = load_arrow("ASSETS/CREDITS/HOVERED/chevron_arrow 1 (1).png")
        self._arrow_left_hovered  = load_arrow("ASSETS/CREDITS/HOVERED/chevron_arrow 1 (2).png")

        # Place arrows vertically centred on the board, OUTSIDE the board edges
        aw = self._arrow_right_normal.get_width()
        ah = self._arrow_right_normal.get_height()
        mid_y = self.board_rect.centery - ah // 2
        GAP = 12  # gap between board edge and arrow
        self._right_rect = pygame.Rect(self.board_rect.right + GAP, mid_y, aw, ah)
        self._left_rect  = pygame.Rect(self.board_rect.left  - aw - GAP, mid_y, aw, ah)

        self._key_cooldown = 0

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
        if keys[pygame.K_ESCAPE]:
            self.game.manager.change_state("menu")
            return

        mx, my = mouse_pos

        # Arrow key navigation (with cooldown to avoid flying through pages)
        if self._key_cooldown > 0:
            self._key_cooldown -= 1
        else:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self._page = (self._page + 1) % len(PAGES)
                self._key_cooldown = 15
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self._page = (self._page - 1) % len(PAGES)
                self._key_cooldown = 15

        # Mouse click navigation
        if clicked:
            if self._right_rect.collidepoint(mx, my):
                self._page = (self._page + 1) % len(PAGES)
            elif self._left_rect.collidepoint(mx, my):
                self._page = (self._page - 1) % len(PAGES)

    def draw(self, surface):
        a = self.assets
        mx, my = pygame.mouse.get_pos()
        mx = mx * self.game.WIDTH / self.game.SCREEN_WIDTH
        my = my * self.game.HEIGHT / self.game.SCREEN_HEIGHT

        surface.blit(a.esc_banner, (8, 8))
        surface.blit(a.title, a.title.get_rect(center=(400, 85)))
        surface.blit(self.board, self.board_rect)

        page = PAGES[self._page]
        cx = self.board_rect.centerx

        # Page title — skip if empty (continuation page)
        if page.get("title"):
            title_surf = self._outlined(self.header_font, page["title"], (255, 220, 80))
            surface.blit(title_surf, title_surf.get_rect(center=(cx, self.board_rect.top + 58)))
            content_top = self.board_rect.top + 90
        else:
            content_top = self.board_rect.top + 24

        # Page indicator dots
        dot_y = self.board_rect.bottom - 18
        total_dots = len(PAGES)
        dot_gap = 14
        dot_start = cx - (total_dots - 1) * dot_gap // 2
        for i in range(total_dots):
            color = (255, 220, 80) if i == self._page else (100, 100, 100)
            pygame.draw.circle(surface, color, (dot_start + i * dot_gap, dot_y), 4)

        # Entries
        entries = page["entries"]
        subtitle_after = page.get("subtitle_after", -1)
        subtitle_text  = page.get("subtitle", "")

        # Use content_top set above by title logic (don't overwrite it here)
        content_bottom = self.board_rect.bottom - 30

        role_h     = self.role_font.get_height()
        name_h     = self.name_font.get_height()
        sub_h      = self.role_font.get_height() + 4
        GAP        = 8

        entry_heights = [(role_h + 3 + name_h) if role else name_h for role, _ in entries]
        extra_for_sub = (sub_h + GAP) if subtitle_after >= 0 else 0
        block_h = sum(entry_heights) + GAP * (len(entries) - 1) + extra_for_sub
        content_h = content_bottom - content_top
        y = content_top + max(0, (content_h - block_h) // 2)

        for idx, ((role, name), eh) in enumerate(zip(entries, entry_heights)):
            if idx == subtitle_after and subtitle_text:
                sub_surf = self._outlined(self.role_font, f"— {subtitle_text} —", (255, 220, 80))
                surface.blit(sub_surf, sub_surf.get_rect(centerx=cx, y=y))
                y += sub_h + GAP

            if not name:
                y += eh + GAP
                continue
            if role:
                role_surf = self._outlined(self.role_font, role, (180, 180, 180))
                surface.blit(role_surf, role_surf.get_rect(centerx=cx, y=y))
                name_surf = self._outlined(self.name_font, name, (255, 255, 255))
                surface.blit(name_surf, name_surf.get_rect(centerx=cx, y=y + role_h + 3))
            else:
                name_surf = self._outlined(self.name_font, name, (255, 255, 255))
                surface.blit(name_surf, name_surf.get_rect(centerx=cx, y=y))
            y += eh + GAP

        # Navigation arrows — only show relevant ones
        right_hov = self._right_rect.collidepoint(mx, my)
        left_hov  = self._left_rect.collidepoint(mx, my)

        # Always show right arrow (wraps)
        right_img = self._arrow_right_hovered if right_hov else self._arrow_right_normal
        surface.blit(right_img, self._right_rect)

        # Only show left arrow when not on first page
        if self._page > 0:
            left_img = self._arrow_left_hovered if left_hov else self._arrow_left_normal
            surface.blit(left_img, self._left_rect)
