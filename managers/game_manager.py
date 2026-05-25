import pygame
import sys
from managers.save_manager import load_profile, save_profile


class GameManager:

    def __init__(self):
        self.profile = load_profile() or {}
        self.game_state     = "intro"
        self.previous_state = "menu"
        self.current_level  = 1
        self.unlocked_levels = set(self.profile.get("unlocked_levels", [1])) or {1}
        self.settings = {"MUSIC": 100, "SOUND": 100, "SFX": 100, "SENSITIVITY": 100}
        self.score     = 0
        self.game_over = False
        self.unlocked_characters = set(self.profile.get("unlocked_characters", [0])) or {0}
        self.selected_character = 0  # 0=Jose, 1=Bong, 2=Maria, 3=Guard
        self.player_name = ""

    def save_profile(self):
        self.profile["unlocked_levels"] = sorted(self.unlocked_levels)
        self.profile["unlocked_characters"] = sorted(self.unlocked_characters)
        save_profile(self.profile)

    def unlock_level(self, lvl):
        self.unlocked_levels.add(lvl)
        self.save_profile()

    def unlock_character(self, character_index: int):
        self.unlocked_characters.add(int(character_index))
        self.save_profile()

    def is_character_unlocked(self, character_index: int) -> bool:
        return int(character_index) in self.unlocked_characters

    def change_state(self, new_state):
        """Change the active screen/game state."""
        self.game_state = new_state

    def reset_game(self):
        """Reset all gameplay variables for a new game."""
        self.score = 0
        self.level = 1
        self.game_over = False

    def add_score(self, amount=1):
        """Increase score when the player hits the can."""
        self.score += amount

    def next_level(self):
        """Advance to the next level."""
        self.level += 1

    def set_game_over(self):
        """Mark the game as over."""
        self.game_over = True
        
    def end_game(self):
        """Quit Pygame and close the game."""
        pygame.quit()
        sys.exit()
