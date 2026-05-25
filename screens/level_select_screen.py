import pygame


class LevelSelectScreen:

    def __init__(self, game):
        self.game = game
        self.assets = game.assets
        self._mouse_pos = (0, 0)
        self._clicked = False
        a = self.assets
        self.board_rect = a.board.get_rect(center=(400, 370))
        btn_h = a.level_btn_normal.get_height()
        gap = 14
        start_y = self.board_rect.top + 140
        self.slot_ys = [start_y + i * (btn_h + gap) for i in range(4)]

    def update(self, mouse_pos, clicked):
        self._mouse_pos = mouse_pos
        self._clicked = clicked
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.game.manager.change_state("menu")
        a = self.assets
        cx = self.board_rect.centerx
        unlocked = self.game.manager.unlocked_levels
        for i, lvl in enumerate([1, 2, 3, 4]):
            if lvl in unlocked:
                rect = a.level_btn_normal.get_rect(center=(cx, self.slot_ys[i]))
                if rect.collidepoint(mouse_pos) and clicked:
                    self.game.manager.current_level = lvl
                    self.game.start_fade("gameplay")

    def draw(self, surface):
        a = self.assets
        cx = self.board_rect.centerx
        unlocked = self.game.manager.unlocked_levels
        surface.blit(a.esc_banner, (8, 8))
        surface.blit(a.title, a.title.get_rect(center=(400, 100)))
        surface.blit(a.board, self.board_rect)
        header_y = self.board_rect.top + 75
        surface.blit(a.level_select_header, a.level_select_header.get_rect(center=(cx, header_y)))

        level_nums_normal  = [a.level_num_1,         a.level_num_2,         a.level_num_2,         a.level_num_2]
        level_nums_hovered = [a.level_num_1_hovered, a.level_num_2_hovered, a.level_num_2_hovered, a.level_num_2_hovered]

        for i, lvl in enumerate([1, 2, 3, 4]):
            cy = self.slot_ys[i]
            if lvl in unlocked:
                hit_rect = a.level_btn_normal.get_rect(center=(cx, cy))
                hov = hit_rect.collidepoint(self._mouse_pos)
                surface.blit(a.level_btn_hovered if hov else a.level_btn_normal,
                             (a.level_btn_normal if not hov else a.level_btn_hovered).get_rect(center=(cx, cy)))
                surface.blit(level_nums_hovered[i] if hov else level_nums_normal[i],
                             (level_nums_normal[i] if not hov else level_nums_hovered[i]).get_rect(center=(cx, cy)))
            else:
                surface.blit(a.level_btn_locked, a.level_btn_locked.get_rect(center=(cx, cy)))
                surface.blit(a.padlock, a.padlock.get_rect(center=(cx, cy)))
