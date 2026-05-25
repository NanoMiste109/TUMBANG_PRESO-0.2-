from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class AchievementDef:
    id: str
    name: str
    description: str
    unlocks_character: Optional[int] = None  # character index


DEFAULT_ACHIEVEMENTS = [
    AchievementDef(
        id="clear_level_1",
        name="Barangay Rookie",
        description="Clear Level 1.",
        unlocks_character=1,  # Bong
    ),
    AchievementDef(
        id="clear_level_2",
        name="Street Legend",
        description="Clear Level 2.",
        unlocks_character=2,  # Maria
    ),
    AchievementDef(
        id="clear_level_4",
        name="Tumbang Preso Master",
        description="Clear Level 4.",
        unlocks_character=3,  # Guard
    ),
]


class AchievementManager:
    """
    Stores achievement unlocks inside GameManager.profile and triggers character unlocks.
    Profile schema (stored in profile.json):
      {
        "unlocked_levels": [1,2],
        "unlocked_characters": [0,1],
        "achievements": {"clear_level_1": true, ...}
      }
    """

    def __init__(self, game_manager):
        self.mgr = game_manager
        self.defs: Dict[str, AchievementDef] = {a.id: a for a in DEFAULT_ACHIEVEMENTS}
        # ensure keys exist
        prof = self.mgr.profile
        prof.setdefault("achievements", {})
        for a in self.defs:
            prof["achievements"].setdefault(a, False)

    def is_unlocked(self, achievement_id: str) -> bool:
        return bool(self.mgr.profile.get("achievements", {}).get(achievement_id, False))

    def unlock(self, achievement_id: str) -> bool:
        if achievement_id not in self.defs:
            return False
        if self.is_unlocked(achievement_id):
            return False

        self.mgr.profile.setdefault("achievements", {})[achievement_id] = True

        ach = self.defs[achievement_id]
        if ach.unlocks_character is not None:
            self.mgr.unlock_character(ach.unlocks_character)

        self.mgr.save_profile()
        return True

    def on_level_cleared(self, level: int):
        if level == 1:
            self.unlock("clear_level_1")
        elif level == 2:
            self.unlock("clear_level_2")
        elif level == 4:
            self.unlock("clear_level_4")

