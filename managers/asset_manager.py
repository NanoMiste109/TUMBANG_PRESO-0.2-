import pygame
import os
from resource_path import resource_path


class AssetManager:

    TITLE_SCALE = 0.3
    BOARD_SCALE = 0.6
    BUTTON_SCALE = 0.55
    BG_SCALE = 0.6
    Y_MOUNTAIN  = -100
    Y_VILLAGE   = 140
    Y_RIVERFRONT = -180
    Y_RIVERFRONT2 = 480
    Y_WATER     = -34

    def __init__(self):
        self.font     = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 30)
        self.big_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 80)
        subtract_img = pygame.image.load(resource_path("ASSETS/BACKGROUND/Subtract.png")).convert_alpha()
        subtract = pygame.transform.scale(subtract_img, (800, 600))
        sky_img = pygame.image.load(resource_path("ASSETS/BACKGROUND/Cloud BG (1).png")).convert_alpha()
        sky_ratio = 600 / sky_img.get_height()
        sky_w = max(800, int(sky_img.get_width() * sky_ratio))
        sky = pygame.transform.scale(sky_img, (sky_w, 600))

        def load_parallax(path):
            img = pygame.image.load(resource_path(path)).convert_alpha()
            w = int(img.get_width()  * self.BG_SCALE)
            h = int(img.get_height() * self.BG_SCALE)
            return pygame.transform.scale(img, (w, h))
        mountain    = load_parallax("ASSETS/BACKGROUND/ruralparallaxmountain 2.png")
        village     = load_parallax("ASSETS/BACKGROUND/ruralparallaxvillage 2.png")
        riverfront  = load_parallax("ASSETS/BACKGROUND/ruralparallaxriverfront 3.png")
        riverfront2 = pygame.transform.flip(
                          load_parallax("ASSETS/BACKGROUND/ruralparallaxriverfront 3.png"),
                          False, True)
        water       = load_parallax("ASSETS/BACKGROUND/ruralparallaxriverskyredlex 2.png")

        self.bg_layers = [
            (subtract,    0,                     0.0),
            (sky,         0,                     0.0),
            (mountain,    self.Y_MOUNTAIN,        0.3),
            (village,     self.Y_VILLAGE,         0.8),
            (water,       self.Y_WATER,           2.0),
            (riverfront,  self.Y_RIVERFRONT,      1.5),
            (riverfront2, self.Y_RIVERFRONT2,     1.5),
        ]

        self.cloud_images = [
            pygame.image.load(resource_path(f"ASSETS/BACKGROUND/cloud{i}.png")).convert_alpha()
            for i in range(2, 9)
        ]

        board = pygame.image.load(resource_path("ASSETS/MENU/board.png")).convert_alpha()
        self.board = pygame.transform.scale(board, (
            int(board.get_width()  * self.BOARD_SCALE * 0.78),
            int(board.get_height() * self.BOARD_SCALE)
        ))
        # Larger bamboo board for level cleared / failed overlays
        LC_BOARD_SCALE = 0.92
        self.lc_board = pygame.transform.scale(board, (
            int(board.get_width() * LC_BOARD_SCALE * 0.78),
            int(board.get_height() * LC_BOARD_SCALE),
        ))

        title = pygame.image.load(resource_path("ASSETS/TEXT/TITLE.png")).convert_alpha()
        self.title = pygame.transform.scale(title, (
            int(title.get_width()  * self.TITLE_SCALE),
            int(title.get_height() * self.TITLE_SCALE * 1.4)
        ))

        LEVEL_SCALE = 0.65
        BTN_WIDTH_SCALE = 0.78
        def load_level(path):
            img = pygame.image.load(resource_path(path)).convert_alpha()
            return pygame.transform.scale(img, (int(img.get_width() * LEVEL_SCALE), int(img.get_height() * LEVEL_SCALE)))

        def load_btn(path):
            img = pygame.image.load(resource_path(path)).convert_alpha()
            return pygame.transform.scale(img, (int(img.get_width() * LEVEL_SCALE * BTN_WIDTH_SCALE), int(img.get_height() * LEVEL_SCALE)))

        self.level_select_header = load_btn("ASSETS/LEVEL/sELECT lEVEl.png")
        self.level_btn_normal    = load_btn("ASSETS/LEVEL/unlock_level 19.png")
        self.level_btn_hovered   = load_btn("ASSETS/LEVEL/unlock_level_highlight 1.png")
        self.level_btn_locked        = load_btn("ASSETS/LEVEL/locked_level 1.png")
        self.level_btn_locked_hover  = load_btn("ASSETS/LEVEL/locked_level_highlight 9.png")
        self.padlock                 = load_level("ASSETS/LEVEL/padlock - karsiori 4.png")
        self.esc_banner          = load_level("ASSETS/LEVEL/Group 54.png")
        self.level_num_1         = load_level("ASSETS/LEVEL/1.png")
        self.level_num_1_hovered = load_level("ASSETS/LEVEL/1(hovered).png")
        self.level_num_2         = load_level("ASSETS/LEVEL/2.png")
        self.level_num_2_hovered = load_level("ASSETS/LEVEL/2 (hovered).png")
        self.level_num_3         = load_level("ASSETS/LEVEL/3.png")
        self.level_num_3_hovered = load_level("ASSETS/LEVEL/3 (hovered).png")
        self.level_num_4         = load_level("ASSETS/LEVEL/4.png")
        self.level_num_4_hovered = load_level("ASSETS/LEVEL/4 (hovered).png")
        SETTINGS_SCALE = 0.38
        SLIDER_SCALE = 0.38

        def load_setting(path):
            img = pygame.image.load(resource_path(path)).convert_alpha()
            return pygame.transform.scale(img, (int(img.get_width() * SETTINGS_SCALE), int(img.get_height() * SETTINGS_SCALE)))

        def load_slider(path):
            img = pygame.image.load(resource_path(path)).convert_alpha()
            return pygame.transform.scale(img, (int(img.get_width() * SLIDER_SCALE), int(img.get_height() * SLIDER_SCALE)))

        self.settings_header = load_setting("ASSETS/SETTINGS/SETTINGS (2).png")
        self.slider_bar      = load_slider("ASSETS/SETTINGS/slider bar 3.png")
        self.slider_knob     = load_slider("ASSETS/SETTINGS/slider selector 2.png")
        self.settings_font   = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 18)

        PAUSE_SCALE = 0.32
        pause_normal_paths = {
            "resume":    resource_path("ASSETS/TEXT/NORMAL/GAME/RESUME.png"),
            "howtoplay": resource_path("ASSETS/TEXT/NORMAL/GAME/HOW TO PLAY (1).png"),
            "settings":  resource_path("ASSETS/TEXT/NORMAL/GAME/SETTINGS (3).png"),
            "exit":      resource_path("ASSETS/TEXT/NORMAL/GAME/EXIT (1).png"),
        }

        pause_hovered_paths = {
            "resume":    resource_path("ASSETS/TEXT/HOVERED/GAME/hovered_resume.png"),
            "howtoplay": resource_path("ASSETS/TEXT/HOVERED/GAME/hovered_howtoplay.png"),
            "settings":  resource_path("ASSETS/TEXT/HOVERED/GAME/hovered_settings.png"),
            "exit":      resource_path("ASSETS/TEXT/HOVERED/GAME/hovered_exit.png"),
        }

        self.pause_normal  = {}
        self.pause_hovered = {}

        for key, path in pause_normal_paths.items():
            img = pygame.image.load(path).convert_alpha()
            nw = int(img.get_width()  * PAUSE_SCALE)
            nh = int(img.get_height() * PAUSE_SCALE)
            self.pause_normal[key] = pygame.transform.scale(img, (nw, nh))

        for key, path in pause_hovered_paths.items():
            img = pygame.image.load(path).convert_alpha()
            # Match the height of the normal image, let width scale naturally
            # so the slipper icon doesn't get squished
            target_h = self.pause_normal[key].get_height()
            scale = target_h / img.get_height() if img.get_height() > 0 else PAUSE_SCALE
            self.pause_hovered[key] = pygame.transform.scale(img, (
                int(img.get_width() * scale),
                target_h
            ))

        # load per-level-cont UI assets
        CONT_SCALE = 0.55

        def load_cont(path):
            img = pygame.image.load(resource_path(path)).convert_alpha()
            return pygame.transform.scale(img, (int(img.get_width() * CONT_SCALE), int(img.get_height() * CONT_SCALE)))

        self.lc_cleared = load_cont("ASSETS/LEVELCONT/LEVEL CLEARED!.png")
        self.lc_failed  = load_cont("ASSETS/LEVELCONT/LEVEL failed!.png")

        # Unhovered: 145=menu(home), 150=next, 149=retry  |  Hovered: 146=menu, 148=next, 151=retry
        self.lc_btn_next_normal   = load_cont("ASSETS/LEVELCONT/UNHOVERED/Group 149.png")
        self.lc_btn_next_hovered  = load_cont("ASSETS/LEVELCONT/HOVERED/Group 146.png")
        self.lc_btn_menu_normal   = load_cont("ASSETS/LEVELCONT/UNHOVERED/Group 145.png")
        self.lc_btn_menu_hovered  = load_cont("ASSETS/LEVELCONT/HOVERED/Group 148.png")
        self.lc_btn_retry_normal  = load_cont("ASSETS/LEVELCONT/UNHOVERED/Group 150.png")
        self.lc_btn_retry_hovered = load_cont("ASSETS/LEVELCONT/HOVERED/Group 151.png")
        game_bg = pygame.image.load(resource_path("ASSETS/GAME/game_background.jpg")).convert()
        self.game_bg = pygame.transform.scale(game_bg, (800, 600))

        # Per-level backgrounds (keyed by level number)
        level_bg_paths = {
            1: "ASSETS/LEVELBG/kalsada level_full 1.png",
            2: "ASSETS/LEVELBG/LEVEL DESIGN 2 - PARK.png",
            3: "ASSETS/LEVELBG/LEVEL DESIGN 3 - MARKET.png",
            4: "ASSETS/LEVELBG/LEVEL DESIGN 4 - FIELD.png",
        }
        self.level_bgs = {}
        for lvl, path in level_bg_paths.items():
            img = pygame.image.load(resource_path(path)).convert()
            self.level_bgs[lvl] = pygame.transform.scale(img, (800, 600))
        esc_src = pygame.image.load(resource_path("ASSETS/GAME/Keyboard Extras - Dream Mix 1.png")).convert_alpha()
        self.esc_key = pygame.transform.scale(esc_src, (int(esc_src.get_width() * 0.7), int(esc_src.get_height() * 0.7)))
        self.pause_hint_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 18)
        self.sfx_click = pygame.mixer.Sound(resource_path("ASSETS/SOUND/audley_fergine-ui-button-click-8-341030.mp3"))
        self.sfx_hover = pygame.mixer.Sound(resource_path("ASSETS/SOUND/lesiakower-minimalist-button-hover-sound-effect-399749.mp3"))
        self.sfx_click.set_volume(1.0)
        self.sfx_hover.set_volume(1.0)
        self.sfx_whoosh  = pygame.mixer.Sound(resource_path("ASSETS/SOUND/GAME/floraphonic-fireball-whoosh-1-179125.mp3"))
        self.sfx_can_hit = pygame.mixer.Sound(resource_path("ASSETS/SOUND/GAME/audiomass-output.mp3"))
        self.sfx_whoosh.set_volume(1.0)
        self.sfx_can_hit.set_volume(1.0)
        # pre-decode to eliminate first-play latency
        self.sfx_whoosh.play().stop()
        self.sfx_can_hit.play().stop()
        self.text_normal  = {}
        self.text_hovered = {}
        buttons = ["play", "gamemodes", "howtoplay", "settings", "credits", "exit"]

        for btn in buttons:
            n = pygame.image.load(resource_path(f"ASSETS/TEXT/NORMAL/{btn}.png")).convert_alpha()
            h = pygame.image.load(resource_path(f"ASSETS/TEXT/HOVERED/hovered_{btn}.png")).convert_alpha()
            # Scale both at the same BUTTON_SCALE — hovered images are naturally wider
            # (they include a slipper icon) so they will appear bigger without distortion
            self.text_normal[btn] = pygame.transform.scale(n, (
                int(n.get_width() * self.BUTTON_SCALE),
                int(n.get_height() * self.BUTTON_SCALE)
            ))
            self.text_hovered[btn] = pygame.transform.scale(h, (
                int(h.get_width() * self.BUTTON_SCALE),
                int(h.get_height() * self.BUTTON_SCALE)
            ))

        # ── Named BGM paths (streamed via pygame.mixer.music) ────────────────
        self.bgm_menu_path = resource_path("ASSETS/SOUND/moodmode-retro-game-arcade-236133.mp3")

        # Per-level gameplay BGM
        self.bgm_level_paths = {
            1: resource_path("ASSETS/SOUND/BGM/sandbox-serenade-sky-toes-main-version-28029-02-39.mp3"),
            2: resource_path("ASSETS/SOUND/BGM/2019-12-09_-_Retro_Forest_-_David_Fesliyan.mp3"),
            3: resource_path("ASSETS/SOUND/BGM/2020-06-18_-_8_Bit_Retro_Funk_-_www.FesliyanStudios.com_David_Renda.mp3"),
            4: resource_path("ASSETS/SOUND/BGM/2020-03-22_-_8_Bit_Surf_-_FesliyanStudios.com_-_David_Renda.mp3"),
        }
        # Fallback for any level not in the dict
        self.bgm_gameplay_path = self.bgm_level_paths[1]

        # ── Named SFX slots (placeholder-safe) ───────────────────────────────
        self.sfx_level_cleared = self._load_sfx_placeholder(
            "ASSETS/SOUND/sfx_level_cleared.mp3", self.sfx_can_hit, "sfx_level_cleared")
        self.sfx_level_failed  = self._load_sfx_placeholder(
            "ASSETS/SOUND/sfx_level_failed.mp3",  self.sfx_can_hit, "sfx_level_failed")
        self.sfx_miss          = self._load_sfx_placeholder(
            "ASSETS/SOUND/sfx_miss.mp3",           self.sfx_whoosh,  "sfx_miss")

    def _load_sfx_placeholder(self, path, fallback, name):
        """Load a Sound from path; fall back to an existing Sound if the file is absent."""
        full = resource_path(path)
        if not os.path.exists(full):
            print(f"[AssetManager] WARNING: placeholder used for '{name}' — file not found: {full}")
            return fallback
        return pygame.mixer.Sound(full)
