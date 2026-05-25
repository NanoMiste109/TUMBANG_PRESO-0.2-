import pygame
from resource_path import resource_path
from managers.save_manager import load_scores


class LeaderboardScreen:

    def __init__(self, game):
        self.game   = game
        self.assets = game.assets

        raw = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()
        self.board = pygame.transform.scale(raw, (
            int(raw.get_width()  * 0.62),
            int(raw.get_height() * 0.75)
        ))
        self.board_rect = self.board.get_rect(center=(400, 360))

        self.header_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 34)
        self.row_font    = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 24)
        self.hint_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 20)
        self._scores = []

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
        # refresh scores each time we enter
        self._scores = load_scores()
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.game.manager.change_state("menu")

    def draw(self, surface):
        a = self.assets
        cx = self.board_rect.centerx

        surface.blit(a.title, a.title.get_rect(center=(400, 60)))
        surface.blit(self.board, self.board_rect)
        surface.blit(a.esc_banner, (8, 8))

        header = self._outlined(self.header_font, "LEADERBOARD", (255, 220, 80))
        surface.blit(header, header.get_rect(center=(cx, self.board_rect.top + 52)))

        if not self._scores:
            empty = self._outlined(self.row_font, "No scores yet!", (180, 180, 180))
            surface.blit(empty, empty.get_rect(center=(cx, self.board_rect.centery)))
        else:
            row_h   = self.row_font.get_height() + 10
            start_y = self.board_rect.top + 90
            left_x  = self.board_rect.left + 55
            right_x = self.board_rect.right - 55

            medal_colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]

            for i, entry in enumerate(self._scores[:10]):
                y = start_y + i * row_h
                rank_color = medal_colors[i] if i < 3 else (200, 200, 200)

                rank  = self._outlined(self.row_font, f"#{i+1}", rank_color)
                name  = self._outlined(self.row_font, entry["name"], (255, 255, 255))
                score = self._outlined(self.row_font, str(entry["score"]), (255, 220, 80))

                surface.blit(rank,  (left_x, y))
                surface.blit(name,  (left_x + 55, y))
                surface.blit(score, (right_x - score.get_width(), y))
