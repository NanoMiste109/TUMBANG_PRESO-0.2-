import pygame
from managers.asset_manager import AssetManager
from managers.game_manager import GameManager
from managers.achievement_manager import AchievementManager
from screens.menu_screen import MenuScreen
from screens.level_select_screen import LevelSelectScreen
from screens.gameplay_screen import GameplayScreen
from screens.how_to_play_screen import HowToPlayScreen
from screens.credits_screen import CreditsScreen
from screens.settings_screen import SettingsScreen
from screens.pause_screen import PauseScreen
from screens.character_select_screen import CharacterSelectScreen
from screens.name_entry_screen import NameEntryScreen
from screens.leaderboard_screen import LeaderboardScreen
from screens.achievement_screen import AchievementScreen
from screens.intro_screen import IntroScreen
from entities.clouds import Clouds
from entities.background import ParallaxBackground

class Game:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.assets = AssetManager()
        self.manager = GameManager()
        self.achievements = AchievementManager(self.manager)
        self.parallax_bg = ParallaxBackground(self.assets.bg_layers)
        self.clouds = Clouds(self.WIDTH, self.HEIGHT, self.assets.cloud_images)
        self.screens = {
            "intro": IntroScreen(self),
            "menu": MenuScreen(self),
            "name_entry": NameEntryScreen(self),
            "character_select": CharacterSelectScreen(self),
            "level_select": LevelSelectScreen(self),
            "gameplay": GameplayScreen(self),
            "how_to_play": HowToPlayScreen(self),
            "credits": CreditsScreen(self),
            "settings": SettingsScreen(self),
            "leaderboard": LeaderboardScreen(self),
            "achievements": AchievementScreen(self),
        }
        self.pause = PauseScreen(self)
        self._fade_alpha   = 0
        self._fade_state   = None
        self._fade_target  = None
        self._fade_speed   = 12
        self.time = 0

    def start_fade(self, target_state):
        """Trigger a fade-to-black then fade-in transition to target_state."""
        # BGM transition — swap music before the visual fade begins
        try:
            if target_state == "gameplay":
                lvl = self.manager.current_level
                bgm_path = self.assets.bgm_level_paths.get(lvl, self.assets.bgm_gameplay_path)
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.play(-1)
            elif self.manager.game_state == "gameplay":
                # leaving gameplay → restore menu BGM
                pygame.mixer.music.load(self.assets.bgm_menu_path)
                pygame.mixer.music.play(-1)
        except Exception:
            pass  # best-effort; never crash on audio
        self._fade_target = target_state
        self._fade_state  = "out"
        self._fade_alpha  = 0

    def update(self, mouse_pos, clicked):
        self.time += 0.05
        if self._fade_state == "out":
            self._fade_alpha = min(255, self._fade_alpha + self._fade_speed)
            if self._fade_alpha >= 255:
                self.manager.change_state(self._fade_target)
                if self._fade_target == "gameplay":
                    self.screens["gameplay"].setup_level()
                self._fade_state = "in"
            return

        elif self._fade_state == "in":
            self._fade_alpha = max(0, self._fade_alpha - self._fade_speed)

            if self._fade_alpha <= 0:
                self._fade_state = None
        self.parallax_bg.update()
        self.clouds.update(self.time)
        current_state = self.manager.game_state

        if current_state == "gameplay":
            gameplay = self.screens["gameplay"]
            if gameplay.state == "playing":
                self.pause.update(mouse_pos, clicked)
                if self.pause.active:
                    return

        if current_state in self.screens:
            self.screens[current_state].update(mouse_pos, clicked)

    def draw(self):
        self.parallax_bg.draw(self.surface)
        self.clouds.draw(self.surface)
        current_state = self.manager.game_state
        if current_state in self.screens:
            self.screens[current_state].draw(self.surface)

        if current_state == "gameplay":
            self.pause.draw(self.surface)
            
        if self._fade_alpha > 0:
            fade_surf = pygame.Surface((self.WIDTH, self.HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self._fade_alpha)
            self.surface.blit(fade_surf, (0, 0))
