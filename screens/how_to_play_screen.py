import pygame
from resource_path import resource_path


class HowToPlayScreen:

    INSTRUCTIONS = [
        ("MOVE",       "Arrow Keys to move\nin all 4 directions"),
        ("AIM",        "Press SPACE to lock direction\nPress SPACE again to set power"),
        ("THROW",      "Throw the slipper\nto knock down the can"),
        ("SCORING",    "Weak hit: 5pts  Medium: 10pts\nStrong hit: 20pts"),
        ("WATCH OUT",  "Hitting the guard or missing\ndeducts points"),
        ("LEVEL UP",   "Reach the score target\nto proceed to the next level"),
    ]

    def __init__(self, game):
        self.game   = game
        self.assets = game.assets

        # load a board sized to fit content without blocking the title
        raw = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()
        self.board = pygame.transform.scale(raw, (
            int(raw.get_width()  * 0.58),
            int(raw.get_height() * 0.62)
        ))
        self.board_rect = self.board.get_rect(center=(400, 370))

        self.header_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 28)
        self.label_font  = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 14)
        self.text_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 15)

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
            self.game.manager.change_state(self.game.manager.previous_state)

    def draw(self, surface):
        a = self.assets
        cx = self.board_rect.centerx
        surface.blit(a.esc_banner, (8, 8))
        surface.blit(a.title, a.title.get_rect(center=(400, 100)))
        surface.blit(self.board, self.board_rect)

        header = self._outlined(self.header_font, "HOW TO PLAY", (255, 255, 255))
        surface.blit(header, header.get_rect(center=(cx, self.board_rect.top + 48)))

        label_h = self.label_font.get_height()
        text_h  = self.text_font.get_height()
        row_h   = max(label_h, text_h * 2 + 1) + 8

        content_top = self.board_rect.top + 70
        content_bottom = self.board_rect.bottom - 30
        total_h = row_h * len(self.INSTRUCTIONS)
        y = content_top + (content_bottom - content_top - total_h) // 2

        left_x  = self.board_rect.left + 30
        right_x = self.board_rect.left + 140

        for label, desc in self.INSTRUCTIONS:
            label_surf = self._outlined(self.label_font, label, (255, 220, 80))
            surface.blit(label_surf, label_surf.get_rect(right=right_x - 10, centery=y + row_h // 2))
            line_y = y + (row_h - text_h * len(desc.split("\n")) - (len(desc.split("\n")) - 1)) // 2
            for line in desc.split("\n"):
                ls = self._outlined(self.text_font, line, (255, 255, 255))
                surface.blit(ls, (right_x, line_y))
                line_y += text_h + 1
            y += row_h
