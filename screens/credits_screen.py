import pygame
from resource_path import resource_path


class CreditsScreen:

    LEFT_COL = [
        ("TEAM LEADER",    "Thrisha Mae Lagbo"),
        ("PROGRAMMER",     "Elgyin Roei Ruiz"),
        ("ARTIST",         "Janryl Bautista"),
    ]

    RIGHT_COL = [
        ("ASSET DESIGNER", "Braeden Alfonso"),
        ("PROJECT MANAGER","Charles Andrei Cruz"),
        ("QA",             "Johannes Afable"),
    ]

    def __init__(self, game):
        self.game   = game
        self.assets = game.assets
        board_src = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()
        bw = int(board_src.get_width()  * 0.6 * 1.3)
        bh = int(board_src.get_height() * 0.6 * 0.85)
        self.board = pygame.transform.scale(board_src, (bw, bh))
        self.board_rect = self.board.get_rect(center=(400, 360))
        hdr_src = pygame.image.load(resource_path("ASSETS/SETTINGS/SETTINGS (2).png")).convert_alpha()
        self.role_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 18)
        self.name_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 26)
        self.header_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 48)

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
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.game.manager.change_state("menu")

    def draw(self, surface):
        a = self.assets
        cx = self.board_rect.centerx
        surface.blit(a.esc_banner, (8, 8))
        surface.blit(a.title, a.title.get_rect(center=(400, 85)))
        surface.blit(self.board, self.board_rect)
        header = self._outlined(self.header_font, "CREDITS", (255, 255, 255))
        surface.blit(header, header.get_rect(center=(cx, self.board_rect.top + 52)))
        content_top    = self.board_rect.top + 70
        content_bottom = self.board_rect.bottom - 40
        content_h      = content_bottom - content_top
        entry_h = self.role_font.get_height() + 2 + self.name_font.get_height()
        gap     = 18
        n       = 3
        block_h = n * entry_h + (n - 1) * gap
        block_top = content_top + (content_h - block_h) // 2
        left_cx  = self.board_rect.left  + int(self.board_rect.width * 0.30)
        right_cx = self.board_rect.left  + int(self.board_rect.width * 0.70)

        for col_cx, entries in ((left_cx, self.LEFT_COL), (right_cx, self.RIGHT_COL)):
            for i, (role, name) in enumerate(entries):
                top = block_top + i * (entry_h + gap)
                role_surf = self._outlined(self.role_font, role, (180, 180, 180))
                name_surf = self._outlined(self.name_font, name, (255, 255, 255))
                surface.blit(role_surf, role_surf.get_rect(centerx=col_cx, y=top))
                surface.blit(name_surf, name_surf.get_rect(centerx=col_cx, y=top + role_surf.get_height() + 2))
