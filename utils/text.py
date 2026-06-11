import pygame


# ── Backward-compatible helper ───────────────────────────────────────────────

def draw_text_outline(surface, text, font, color, outline_color, pos):
    x, y = pos
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx != 0 or dy != 0:
                outline = font.render(text, True, outline_color)
                surface.blit(outline, (x + dx, y + dy))
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


# ── TextProvider ─────────────────────────────────────────────────────────────

class TextProvider:
    """
    Returns UI strings in the active language (EN or TL).
    Falls back to EN if a TL key is missing.
    """

    _STRINGS: dict = {
        "menu.play":              {"EN": "PLAY",            "TL": "MAGLARO"},
        "menu.gamemodes":         {"EN": "GAME MODES",      "TL": "MGA LARO"},
        "menu.howtoplay":         {"EN": "HOW TO PLAY",     "TL": "PAANO MAGLARO"},
        "menu.settings":          {"EN": "SETTINGS",        "TL": "MGA SETTING"},
        "menu.credits":           {"EN": "CREDITS",         "TL": "MGA KREDITO"},
        "menu.exit":              {"EN": "EXIT",             "TL": "LUMABAS"},
        "pause.resume":           {"EN": "RESUME",           "TL": "ITULOY"},
        "pause.howtoplay":        {"EN": "HOW TO PLAY",     "TL": "PAANO MAGLARO"},
        "pause.settings":         {"EN": "SETTINGS",        "TL": "MGA SETTING"},
        "pause.exit":             {"EN": "EXIT",             "TL": "LUMABAS"},
        "settings.music":         {"EN": "MUSIC",            "TL": "MUSIKA"},
        "settings.sound":         {"EN": "SOUND",            "TL": "TUNOG"},
        "settings.sfx":           {"EN": "SFX",              "TL": "SFX"},
        "settings.sensitivity":   {"EN": "SENSITIVITY",      "TL": "SENSITIVITY"},
        "settings.language":      {"EN": "LANGUAGE",         "TL": "WIKA"},
        "level.cleared":          {"EN": "LEVEL CLEARED!",   "TL": "NATAPOS ANG ANTAS!"},
        "level.failed":           {"EN": "LEVEL FAILED!",    "TL": "NABIGO SA ANTAS!"},
        "charselect.hint": {
            "EN": "ARROW KEYS or CLICK to select   |   SPACE / ENTER to confirm",
            "TL": "ARROW KEYS o I-CLICK para pumili   |   SPACE / ENTER para kumpirmahin",
        },
        "charselect.locked_hint": {
            "EN": "Complete an achievement to unlock",
            "TL": "Kumpletuhin ang isang tagumpay para i-unlock",
        },
    }

    @classmethod
    def get(cls, key: str, language: str = "EN") -> str:
        entry = cls._STRINGS.get(key)
        if entry is None:
            return key  # unknown key — return key itself so it's visible in UI
        return entry.get(language) or entry.get("EN") or key


# ── render_label ─────────────────────────────────────────────────────────────

def render_label(surface, key, game, rect, font, png_surf=None, color=(255, 255, 255)):
    """
    Render a UI label respecting the active language.

    EN + png_surf provided  → blit the PNG at rect (preserves original visual style).
    TL  (or EN without PNG) → render text with font, centred on rect.center.

    Parameters
    ----------
    surface   : pygame.Surface  — destination surface
    key       : str             — TextProvider key (e.g. "menu.play")
    game      : Game            — top-level game object (owns manager.settings)
    rect      : pygame.Rect     — position / size reference for the label
    font      : pygame.font.Font
    png_surf  : pygame.Surface | None — the original PNG image (EN only)
    color     : tuple           — text colour for font-rendered path
    """
    lang = game.manager.settings.get("LANGUAGE", "EN")
    if lang == "EN" and png_surf is not None:
        surface.blit(png_surf, rect)
    else:
        text = TextProvider.get(key, lang)
        surf = font.render(text, True, color)
        surface.blit(surf, surf.get_rect(center=rect.center))
