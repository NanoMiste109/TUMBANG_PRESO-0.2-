import pygame
from resource_path import resource_path


class NameEntryScreen:

    MAX_LEN = 12

    def __init__(self, game):
        self.game   = game
        self.assets = game.assets
        self.name   = ""
        self._done  = False
        self._enter_held = False  # prevent instant confirm on screen entry

        raw = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()
        self.board = pygame.transform.scale(raw, (
            int(raw.get_width()  * 0.58),
            int(raw.get_height() * 0.55)
        ))
        self.board_rect = self.board.get_rect(center=(400, 330))

        self.header_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 28)
        self.input_font  = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 32)
        self.hint_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 16)

    def reset(self):
        self.name  = ""
        self._done = False
        self._enter_held = True  # block ENTER until it's released first

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

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not self._enter_held and self.name.strip():
                    self._confirm()
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            else:
                self._enter_held = False  # any other key releases the hold
                if len(self.name) < self.MAX_LEN:
                    ch = event.unicode
                    if ch.isprintable() and ch != " " or (ch == " " and self.name):
                        self.name += ch
        if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            self._enter_held = False

    def _confirm(self):
        self.game.manager.player_name = self.name.strip()
        self.game.screens["character_select"].reset_input()
        self.game.manager.change_state("character_select")

    def update(self, mouse_pos, clicked):
        pass  # input handled via handle_event in main loop

    def draw(self, surface):
        a = self.assets
        cx = self.board_rect.centerx

        surface.blit(a.title, a.title.get_rect(center=(400, 90)))
        surface.blit(self.board, self.board_rect)

        header = self._outlined(self.header_font, "ENTER YOUR NAME", (255, 220, 80))
        surface.blit(header, header.get_rect(center=(cx, self.board_rect.top + 45)))

        # input box
        box_rect = pygame.Rect(0, 0, 260, 44)
        box_rect.center = (cx, self.board_rect.centery - 10)
        pygame.draw.rect(surface, (30, 30, 30), box_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 220, 50), box_rect, 2, border_radius=6)

        display = self.name + ("|" if pygame.time.get_ticks() % 800 < 400 else "")
        name_surf = self._outlined(self.input_font, display, (255, 255, 255))
        surface.blit(name_surf, name_surf.get_rect(center=box_rect.center))

        hint = self._outlined(self.hint_font, "ENTER to confirm", (180, 180, 180))
        surface.blit(hint, hint.get_rect(center=(cx, self.board_rect.bottom - 35)))
