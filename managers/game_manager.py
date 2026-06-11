import pygame
import sys
from managers.save_manager import load_profile, save_profile, DEFAULT_PROFILE


class GameManager:

    def __init__(self):
        raw = load_profile() or {}
        # Merge defaults so missing keys are always present
        self.profile = {**DEFAULT_PROFILE, **raw}
        self.profile["achievements"] = {
            **DEFAULT_PROFILE["achievements"],
            **raw.get("achievements", {}),
        }
        self.profile.setdefault("special_hits", 0)

        self.game_state     = "intro"
        self.previous_state = "menu"
        self.current_level  = 1
        self.unlocked_levels     = set(self.profile.get("unlocked_levels",     [1])) or {1}
        self.unlocked_characters = set(self.profile.get("unlocked_characters", [0])) or {0}
        self.unlocked_slippers   = set(self.profile.get("unlocked_slippers",   [0])) or {0}

        self.settings = {
            "MUSIC": 100, "SOUND": 100, "SFX": 100,
            "LANGUAGE": "EN",
        }

        self.score              = 0   # int mirror used by legacy code
        self.selected_character = 0   # 0=Jose, 1=Bong, 2=Maria
        self.selected_slipper   = 0   # 0=default, 1=v2, 2=v3, 3=v4
        self.player_name        = ""

    # ── Persistence ──────────────────────────────────────────────────────────

    def save_profile(self):
        self.profile["unlocked_levels"]     = sorted(self.unlocked_levels)
        self.profile["unlocked_characters"] = sorted(self.unlocked_characters)
        self.profile["unlocked_slippers"]   = sorted(self.unlocked_slippers)
        save_profile(self.profile)

    # ── Unlock helpers ───────────────────────────────────────────────────────

    def unlock_level(self, lvl: int):
        self.unlocked_levels.add(int(lvl))
        self.save_profile()

    def unlock_character(self, character_index: int):
        self.unlocked_characters.add(int(character_index))
        self.save_profile()

    def unlock_slipper(self, slipper_index: int):
        self.unlocked_slippers.add(int(slipper_index))
        self.save_profile()

    def is_character_unlocked(self, character_index: int) -> bool:
        return int(character_index) in self.unlocked_characters

    def is_slipper_unlocked(self, slipper_index: int) -> bool:
        return int(slipper_index) in self.unlocked_slippers

    # ── State ────────────────────────────────────────────────────────────────

    def change_state(self, new_state: str):
        self.game_state = new_state

    # ── Quit ─────────────────────────────────────────────────────────────────

    def end_game(self):
        pygame.quit()
        sys.exit()
