import pygame
import sys
from managers.save_manager import load_profile, save_profile, DEFAULT_PROFILE
import copy


class GameManager:

    def __init__(self):
        # Profile starts empty — loaded once player_name is set
        self.profile = copy.deepcopy(DEFAULT_PROFILE)

        self.game_state     = "intro"
        self.previous_state = "menu"
        self.current_level  = 1
        self.unlocked_levels     = {1}
        self.unlocked_characters = {0}
        self.unlocked_slippers   = {0}

        self.settings = {
            "MUSIC": 100, "SOUND": 100, "SFX": 100,
            "LANGUAGE": "EN",
        }

        self.score              = 0
        self.selected_character = 0
        self.selected_slipper   = 0
        self._player_name       = ""

    @property
    def player_name(self) -> str:
        return self._player_name

    @player_name.setter
    def player_name(self, name: str):
        self._player_name = name
        if name:
            self._load_player_profile(name)

    def _load_player_profile(self, name: str):
        """Load (or initialise) this player's profile from disk."""
        raw = load_profile(name) or {}
        self.profile = {**DEFAULT_PROFILE, **raw}
        self.profile["achievements"] = {
            **DEFAULT_PROFILE["achievements"],
            **raw.get("achievements", {}),
        }
        self.profile.setdefault("special_hits", 0)
        self.unlocked_levels     = set(self.profile.get("unlocked_levels",     [1])) or {1}
        self.unlocked_characters = set(self.profile.get("unlocked_characters", [0])) or {0}
        self.unlocked_slippers   = set(self.profile.get("unlocked_slippers",   [0])) or {0}
        # Reset selections to safe defaults for this profile
        self.selected_character = 0
        self.selected_slipper   = 0

    # ── Persistence ──────────────────────────────────────────────────────────

    def save_profile(self):
        self.profile["unlocked_levels"]     = sorted(self.unlocked_levels)
        self.profile["unlocked_characters"] = sorted(self.unlocked_characters)
        self.profile["unlocked_slippers"]   = sorted(self.unlocked_slippers)
        save_profile(self.profile, self._player_name)

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
