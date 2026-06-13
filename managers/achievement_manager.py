from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class AchievementDef:
    id: str
    name: str
    description: str
    unlocks_character: Optional[int] = None  # character index
    unlocks_slipper:   Optional[int] = None  # slipper index


DEFAULT_ACHIEVEMENTS = [
    # ── Character unlocks ────────────────────────────────────────────────────
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
    # ── Slipper unlocks ──────────────────────────────────────────────────────
    AchievementDef(
        id="slipper_v2",
        name="Proven on the Streets",
        description="Clear Level 2 to unlock the Street Slipper.",
        unlocks_slipper=1,
    ),
    AchievementDef(
        id="slipper_v3",
        name="Special Master",
        description="Hit the can using a special skill 3 times (across any sessions).",
        unlocks_slipper=2,
    ),
    AchievementDef(
        id="slipper_v4",
        name="Tumbang Preso Champion",
        description="Clear Level 4 to unlock the Champion Slipper.",
        unlocks_slipper=3,
    ),
]


class AchievementManager:
    """
    Stores achievement unlocks inside GameManager.profile and triggers unlocks.
    """

    def __init__(self, game_manager):
        self.mgr = game_manager
        self.defs: Dict[str, AchievementDef] = {a.id: a for a in DEFAULT_ACHIEVEMENTS}
        prof = self.mgr.profile
        prof.setdefault("achievements", {})
        for a in self.defs:
            prof["achievements"].setdefault(a, False)

        # Repair: if level-2 was already cleared but slipper 1 wasn't saved, grant it now
        if prof["achievements"].get("clear_level_2") and 1 not in self.mgr.unlocked_slippers:
            self.mgr.unlock_slipper(1)
        # Repair: if level-4 was already cleared but slipper 3 wasn't saved, grant it now
        if prof["achievements"].get("clear_level_4") and 3 not in self.mgr.unlocked_slippers:
            self.mgr.unlock_slipper(3)

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
        if ach.unlocks_slipper is not None:
            self.mgr.unlock_slipper(ach.unlocks_slipper)

        self.mgr.save_profile()
        return True

    def on_level_cleared(self, level: int):
        if level == 1:
            self.unlock("clear_level_1")
        elif level == 2:
            self.unlock("clear_level_2")
            self.unlock("slipper_v2")   # same condition
            # Always ensure slipper 1 is unlocked when level 2 is cleared
            self.mgr.unlock_slipper(1)
        elif level == 4:
            self.unlock("clear_level_4")
            self.unlock("slipper_v4")   # same condition
            # Always ensure slipper 3 is unlocked when level 4 is cleared
            self.mgr.unlock_slipper(3)

    def on_special_hit(self):
        """Call when the player hits the can with a special active."""
        prof = self.mgr.profile
        count = prof.get("special_hits", 0) + 1
        prof["special_hits"] = count
        self.mgr.save_profile()
        if count >= 3:
            self.unlock("slipper_v3")

