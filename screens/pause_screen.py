import pygame
from resource_path import resource_path
from utils.text import TextProvider


class PauseScreen:

    ITEMS   = ["resume", "howtoplay", "settings", "exit"]
    SLIDERS = ["MUSIC", "SOUND", "SFX"]

    def __init__(self, game):
        self.game   = game
        self.assets = game.assets
        self.active = False
        self.panel  = "main"
        self._last_hovered = None
        self._esc_held = False
        self.board_rect = self.assets.board.get_rect(center=(400, 300))
        self.spacing = 52
        btn_h   = max(self.assets.pause_normal[i].get_height() for i in self.ITEMS)
        n       = len(self.ITEMS)
        block_h = n * btn_h + (n - 1) * (self.spacing - btn_h)
        self._btn_start_y = self.board_rect.centery - block_h // 2 + btn_h // 2
        a  = self.assets
        cx = self.board_rect.centerx
        top     = self.board_rect.top + 100
        spacing = 56
        self.slider_values = game.manager.settings
        self.bar_rects = [
            a.slider_bar.get_rect(center=(cx, top + i * spacing))
            for i in range(3)
        ]

        self.dragging = None
        self.htp_header_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 34)
        self.htp_label_font  = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 13)
        self.htp_text_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 16)
        self.HTP = [
            ("MOVE",      "Arrow Up / Down"),
            ("THROW",     "Click to throw slipper"),
            ("SCORE",     "Hit the can to score points"),
            ("WATCH OUT", "Avoid the guard!"),
            ("LEVEL UP",  "Attain points to proceed\nto next level"),
        ]

    _SLIDER_KEYS = {
        "MUSIC": "settings.music",
        "SOUND": "settings.sound",
        "SFX":   "settings.sfx",
    }

    def toggle(self):
        self.active = not self.active
        self.panel  = "main"
        self._last_hovered = None

    def _knob_x(self, index):
        bar = self.bar_rects[index]
        val = self.slider_values[self.SLIDERS[index]] / 100.0
        kw  = self.assets.slider_knob.get_width()
        return bar.left + kw // 2 + int(val * (bar.width - kw))

    def _outlined(self, font, text, color, outline=(0, 0, 0)):
        base = font.render(text, True, color)
        w, h = base.get_width() + 2, base.get_height() + 2
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    surf.blit(font.render(text, True, outline), (dx+1, dy+1))
        surf.blit(base, (1, 1))
        return surf

    def _overlay(self, surface):
        ov = pygame.Surface((800, 600), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        surface.blit(ov, (0, 0))

    def update(self, mouse_pos, clicked):
        if not self.active:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            if not self._esc_held:
                if self.panel != "main":
                    self.panel = "main"
                    self._esc_held = True
                    return
            self._esc_held = True
            return
        else:
            self._esc_held = False
        if self.panel == "main":
            self._update_main(mouse_pos, clicked)
        elif self.panel == "settings":
            self._update_settings(mouse_pos)

    def _update_main(self, mouse_pos, clicked):
        mx, my = mouse_pos
        hovered_item = None
        for i, item in enumerate(self.ITEMS):
            normal = self.assets.pause_normal[item]
            rect = normal.get_rect(center=(
                self.board_rect.centerx,
                self._btn_start_y + i * self.spacing
            ))
            if rect.collidepoint(mx, my):
                hovered_item = item
                if clicked:
                    self.assets.sfx_click.play()
                    if item == "resume":
                        self.active = False
                    elif item == "howtoplay":
                        self.panel = "howtoplay"
                    elif item == "settings":
                        self.panel = "settings"
                    elif item == "exit":
                        self.active = False
                        self.game.start_fade("menu")
        if hovered_item != self._last_hovered and hovered_item is not None:
            self.assets.sfx_hover.play()
        self._last_hovered = hovered_item

    def _update_settings(self, mouse_pos):
        mx, my = mouse_pos
        mouse_held = pygame.mouse.get_pressed()[0]
        a  = self.assets
        kw = a.slider_knob.get_width()
        kh = a.slider_knob.get_height()
        if mouse_held:
            if self.dragging is None:
                for i, bar in enumerate(self.bar_rects):
                    kx = self._knob_x(i)
                    kr = pygame.Rect(kx - kw//2, bar.centery - kh//2, kw, kh)
                    if kr.collidepoint(mx, my):
                        self.dragging = i
                        break
            if self.dragging is not None:
                bar    = self.bar_rects[self.dragging]
                usable = bar.width - kw
                rel    = mx - (bar.left + kw // 2)
                val    = max(0, min(100, int(rel / usable * 100)))
                self.slider_values[self.SLIDERS[self.dragging]] = val
                if self.SLIDERS[self.dragging] == "MUSIC":
                    pygame.mixer.music.set_volume(val / 100.0)
                elif self.SLIDERS[self.dragging] == "SOUND":
                    a.sfx_click.set_volume(val / 100.0)
                    a.sfx_hover.set_volume(val / 100.0)
                elif self.SLIDERS[self.dragging] == "SFX":
                    a.sfx_whoosh.set_volume(val / 100.0)
                    a.sfx_can_hit.set_volume(val / 100.0)
                    if hasattr(a, "sfx_level_cleared"):
                        a.sfx_level_cleared.set_volume(val / 100.0)
                    if hasattr(a, "sfx_level_failed"):
                        a.sfx_level_failed.set_volume(val / 100.0)
                    if hasattr(a, "sfx_miss"):
                        a.sfx_miss.set_volume(val / 100.0)
        else:
            self.dragging = None

    def draw(self, surface):
        if not self.active:
            return
        self._overlay(surface)
        surface.blit(self.assets.board, self.board_rect)
        if self.panel == "main":
            self._draw_main(surface)
        elif self.panel == "howtoplay":
            self._draw_howtoplay(surface)
        elif self.panel == "settings":
            self._draw_settings(surface)

    def _draw_main(self, surface):
        mx, my = pygame.mouse.get_pos()
        mx *= self.game.WIDTH  / self.game.SCREEN_WIDTH
        my *= self.game.HEIGHT / self.game.SCREEN_HEIGHT
        cx = self.board_rect.centerx

        for i, item in enumerate(self.ITEMS):
            center = (cx, self._btn_start_y + i * self.spacing)
            normal = self.assets.pause_normal[item]
            is_hovered = normal.get_rect(center=center).collidepoint(mx, my)
            if is_hovered:
                hov = self.assets.pause_hovered[item]
                surface.blit(hov, hov.get_rect(center=center))
            else:
                surface.blit(normal, normal.get_rect(center=center))

    def _draw_howtoplay(self, surface):
        cx = self.board_rect.centerx
        header = self._outlined(self.htp_header_font, "HOW TO PLAY", (255, 255, 255))
        surface.blit(header, header.get_rect(center=(cx, self.board_rect.top + 56)))
        label_h = self.htp_label_font.get_height()
        text_h  = self.htp_text_font.get_height()
        entry_heights = []

        for _, desc in self.HTP:
            lines = desc.split("\n")
            entry_heights.append(label_h + 1 + text_h * len(lines) + (len(lines)-1))
        gap     = 8
        block_h = sum(entry_heights) + gap * (len(self.HTP) - 1)
        content_top    = self.board_rect.top + 52
        content_bottom = self.board_rect.bottom - 40
        block_top = content_top + ((content_bottom - content_top) - block_h) // 2
        y = block_top
        for label, desc in self.HTP:
            ls = self._outlined(self.htp_label_font, label, (255, 220, 80))
            surface.blit(ls, ls.get_rect(centerx=cx, y=y))
            y += label_h + 1
            for line in desc.split("\n"):
                ts = self._outlined(self.htp_text_font, line, (255, 255, 255))
                surface.blit(ts, ts.get_rect(centerx=cx, y=y))
                y += text_h + 1
            y += gap
        hint = self._outlined(self.htp_label_font, "ESC to go back", (150, 150, 150))
        surface.blit(hint, hint.get_rect(center=(cx, self.board_rect.bottom - 55)))

    def _draw_settings(self, surface):
        a  = self.assets
        cx = self.board_rect.centerx
        surface.blit(a.settings_header, a.settings_header.get_rect(center=(cx, self.board_rect.top + 55)))
        
        for i, name in enumerate(self.SLIDERS):
            bar_rect = self.bar_rects[i]
            val   = self.slider_values[name]
            lang  = self.game.manager.settings.get("LANGUAGE", "EN")
            label_text = f"{TextProvider.get(self._SLIDER_KEYS[name], lang)}: {val}"
            label = a.settings_font.render(label_text, True, (255, 255, 255))
            surface.blit(label, (bar_rect.left, bar_rect.top - 14))
            surface.blit(a.slider_bar, bar_rect)
            kx = self._knob_x(i)
            surface.blit(a.slider_knob, a.slider_knob.get_rect(center=(kx, bar_rect.centery)))
        hint = self._outlined(self.htp_label_font, "ESC to go back", (150, 150, 150))
        surface.blit(hint, hint.get_rect(center=(cx, self.board_rect.bottom - 55)))
