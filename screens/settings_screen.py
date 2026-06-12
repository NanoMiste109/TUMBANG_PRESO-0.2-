import pygame
from utils.text import TextProvider


class SettingsScreen:

    SLIDERS = ["MUSIC", "SOUND", "SFX"]
    # Maps slider name → TextProvider key
    _SLIDER_KEYS = {
        "MUSIC": "settings.music",
        "SOUND": "settings.sound",
        "SFX":   "settings.sfx",
    }

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
            for i in range(3)
        ]
        # Language toggle button — centred below the last slider bar
        last_bar_bottom = self.bar_rects[-1].bottom
        self.lang_btn_rect = pygame.Rect(0, 0, 140, 36)
        self.lang_btn_rect.center = (cx, last_bar_bottom + 30)

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
                a = self.game.assets
                if self.SLIDERS[self.dragging] == "MUSIC":
                    pygame.mixer.music.set_volume(val / 100.0)
                elif self.SLIDERS[self.dragging] == "SOUND":
                    a.sfx_click.set_volume(val / 100.0)
                    a.sfx_hover.set_volume(val / 100.0)
                elif self.SLIDERS[self.dragging] == "SFX":
                    a.sfx_whoosh.set_volume(val / 100.0)
                    a.sfx_can_hit.set_volume(val / 100.0)
                    # new named SFX slots (added in task 8.1)
                    if hasattr(a, "sfx_level_cleared"):
                        a.sfx_level_cleared.set_volume(val / 100.0)
                    if hasattr(a, "sfx_level_failed"):
                        a.sfx_level_failed.set_volume(val / 100.0)
                    if hasattr(a, "sfx_miss"):
                        a.sfx_miss.set_volume(val / 100.0)
        else:
            self.dragging = None

        # Language toggle — single click
        if clicked and self.lang_btn_rect.collidepoint(mx, my):
            current = self.values.get("LANGUAGE", "EN")
            self.values["LANGUAGE"] = "TL" if current == "EN" else "EN"

    def draw(self, surface):
        a = self.assets
        lang = self.values.get("LANGUAGE", "EN")
        cx = self.board_rect.centerx
        surface.blit(a.esc_banner, (8, 8))
        surface.blit(a.title, a.title.get_rect(center=(400, 100)))
        surface.blit(a.board, self.board_rect)
        surface.blit(a.settings_header, a.settings_header.get_rect(center=(cx, self.board_rect.top + 55)))

        for i, name in enumerate(self.SLIDERS):
            bar_rect = self.bar_rects[i]
            label_y = bar_rect.top - 14
            val = self.values[name]
            # Use TextProvider key for the slider name; append the numeric value
            label_text = f"{TextProvider.get(self._SLIDER_KEYS[name], lang)}: {val}"
            label = a.settings_font.render(label_text, True, (255, 255, 255))
            surface.blit(label, (bar_rect.left, label_y))
            surface.blit(a.slider_bar, bar_rect)
            kx = self._knob_x(i)
            knob_rect = a.slider_knob.get_rect(center=(kx, bar_rect.centery))
            surface.blit(a.slider_knob, knob_rect)

        # Language toggle button
        lang_label = f"{TextProvider.get('settings.language', lang)}: {lang}"
        lang_surf = a.settings_font.render(lang_label, True, (255, 255, 255))
        surface.blit(lang_surf, lang_surf.get_rect(center=self.lang_btn_rect.center))
        pygame.draw.rect(surface, (180, 140, 80), self.lang_btn_rect, 2)
