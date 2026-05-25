import pygame


class SettingsScreen:

    SLIDERS = ["MUSIC", "SOUND", "SFX", "SENSITIVITY"]

    def __init__(self, game):
        self.game   = game
        self.assets = game.assets
        self.board_rect = self.assets.board.get_rect(center=(400, 370))
        self.values = game.manager.settings
        self.dragging = None
        a = self.assets
        cx = self.board_rect.centerx
        top = self.board_rect.top + 100
        spacing = 56
        self.bar_rects = [
            a.slider_bar.get_rect(center=(cx, top + i * spacing))
            for i in range(4)
        ]

    def _knob_x(self, index):
        bar = self.bar_rects[index]
        val = self.values[self.SLIDERS[index]] / 100.0
        knob_w = self.assets.slider_knob.get_width()
        usable = bar.width - knob_w
        return bar.left + knob_w // 2 + int(val * usable)

    def update(self, mouse_pos, clicked):
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.game.manager.change_state(self.game.manager.previous_state)
        mx, my = mouse_pos
        mouse_held = pygame.mouse.get_pressed()[0]
        knob_w = self.assets.slider_knob.get_width()
        knob_h = self.assets.slider_knob.get_height()

        if mouse_held:
            if self.dragging is None:
                for i, bar in enumerate(self.bar_rects):
                    kx = self._knob_x(i)
                    knob_rect = pygame.Rect(kx - knob_w // 2, bar.centery - knob_h // 2, knob_w, knob_h)
                    if knob_rect.collidepoint(mx, my):
                        self.dragging = i
                        break

            if self.dragging is not None:
                bar = self.bar_rects[self.dragging]
                usable = bar.width - knob_w
                rel = mx - (bar.left + knob_w // 2)
                val = max(0, min(100, int(rel / usable * 100)))
                self.values[self.SLIDERS[self.dragging]] = val
                if self.SLIDERS[self.dragging] == "MUSIC":
                    pygame.mixer.music.set_volume(val / 100.0)
                elif self.SLIDERS[self.dragging] == "SOUND":
                    self.game.assets.sfx_click.set_volume(val / 100.0)
                    self.game.assets.sfx_hover.set_volume(val / 100.0)
                elif self.SLIDERS[self.dragging] == "SFX":
                    self.game.assets.sfx_whoosh.set_volume(val / 100.0)
                    self.game.assets.sfx_can_hit.set_volume(val / 100.0)
        else:
            self.dragging = None

    def draw(self, surface):
        a = self.assets
        cx = self.board_rect.centerx
        surface.blit(a.esc_banner, (8, 8))
        surface.blit(a.title, a.title.get_rect(center=(400, 100)))
        surface.blit(a.board, self.board_rect)
        surface.blit(a.settings_header, a.settings_header.get_rect(center=(cx, self.board_rect.top + 55)))
        
        for i, name in enumerate(self.SLIDERS):
            bar_rect = self.bar_rects[i]
            label_y = bar_rect.top - 14
            val = self.values[name]
            label = a.settings_font.render(f"{name}: {val}", True, (255, 255, 255))
            surface.blit(label, (bar_rect.left, label_y))
            surface.blit(a.slider_bar, bar_rect)
            kx = self._knob_x(i)
            knob_rect = a.slider_knob.get_rect(center=(kx, bar_rect.centery))
            surface.blit(a.slider_knob, knob_rect)
