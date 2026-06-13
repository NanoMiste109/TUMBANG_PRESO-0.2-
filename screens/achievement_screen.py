import pygame
from resource_path import resource_path


# Maps achievement ID → (title, description, reward_text)
ACHIEVEMENT_DEFS = [
    ("clear_level_1", "Barangay Rookie",        "Clear Level 1",                            "Unlocks: Bong"),
    ("clear_level_2", "Street Legend",          "Clear Level 2",                            "Unlocks: Maria + Rocket Slipper"),
    ("clear_level_4", "Tumbang Preso Master",   "Clear Level 4",                            "Unlocks: Bolt Slipper"),
    ("slipper_v3",    "Special Master",         "Hit the can with a special 3 times",       "Unlocks: Triple Slipper"),
]


class AchievementScreen:

    def __init__(self, game):
        self.game   = game
        self.assets = game.assets

        board_src = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()
        bw = int(board_src.get_width()  * 0.6 * 1.05)
        bh = int(board_src.get_height() * 0.6 * 1.3)  # taller board
        self.board = pygame.transform.scale(board_src, (bw, bh))
        self.board_rect = self.board.get_rect(center=(400, 360))

        self.header_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 30)
        self.title_font  = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 20)
        self.desc_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 14)

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

        header = self._outlined(self.header_font, "ACHIEVEMENTS", (255, 220, 80))
        surface.blit(header, header.get_rect(center=(cx, self.board_rect.top + 46)))

        achievements = self.game.manager.profile.get("achievements", {})
        entry_h = 76  # more height per row
        start_y = self.board_rect.top + 96

        for i, (ach_id, title, desc, reward) in enumerate(ACHIEVEMENT_DEFS):
            unlocked = achievements.get(ach_id, False)
            y = start_y + i * entry_h

            # Row background
            row_color = (50, 90, 50, 180) if unlocked else (50, 50, 50, 180)
            row_surf = pygame.Surface((self.board_rect.width - 30, entry_h - 8), pygame.SRCALPHA)
            row_surf.fill(row_color)
            surface.blit(row_surf, (self.board_rect.left + 15, y))
            pygame.draw.rect(surface,
                             (100, 180, 100) if unlocked else (80, 80, 80),
                             (self.board_rect.left + 15, y, self.board_rect.width - 30, entry_h - 8),
                             2)

            # Status dot
            dot_color = (80, 220, 80) if unlocked else (160, 60, 60)
            pygame.draw.circle(surface, dot_color,
                               (self.board_rect.left + 32, y + (entry_h - 8) // 2), 7)

            # Title + desc
            text_x = self.board_rect.left + 50
            name_col = (200, 255, 200) if unlocked else (180, 180, 180)
            title_surf = self._outlined(self.title_font, title, name_col)
            surface.blit(title_surf, (text_x, y + 4))

            desc_surf = self._outlined(self.desc_font, desc, (160, 160, 160))
            surface.blit(desc_surf, (text_x, y + 4 + title_surf.get_height() + 1))

            # For slipper_v3 (special hits), show progress if not yet unlocked
            if ach_id == "slipper_v3" and not unlocked:
                hits = self.game.manager.profile.get("special_hits", 0)
                prog = self._outlined(self.desc_font, f"Progress: {min(hits, 3)}/3", (255, 180, 80))
                surface.blit(prog, (text_x, y + 4 + title_surf.get_height() + self.desc_font.get_height() + 3))

            # Reward
            rew_col = (255, 220, 80) if unlocked else (100, 100, 100)
            rew_surf = self._outlined(self.desc_font, reward, rew_col)
            surface.blit(rew_surf, rew_surf.get_rect(
                right=self.board_rect.right - 20,
                centery=y + (entry_h - 8) // 2
            ))

        # ESC hint
        hint = self._outlined(self.desc_font, "ESC to return", (140, 140, 140))
        surface.blit(hint, hint.get_rect(center=(cx, self.board_rect.bottom - 22)))
