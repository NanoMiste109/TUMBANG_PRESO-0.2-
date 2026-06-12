import json
import os
from resource_path import resource_path

SAVE_FILE = resource_path("scores.json")
PROFILE_FILE = resource_path("profile.json")

DEFAULT_PROFILE = {
    "achievements": {
        "clear_level_1": False,
        "clear_level_2": False,
        "clear_level_4": False,
        "slipper_v2":    False,
        "slipper_v3":    False,
        "slipper_v4":    False,
    },
    "unlocked_levels":     [1],
    "unlocked_characters": [0],
    "unlocked_slippers":   [0],
    "special_hits":        0,
}


def load_scores():
    """Load leaderboard from disk. Returns list of {name, score} dicts sorted by score desc."""
    if not os.path.exists(SAVE_FILE):
        return []
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x["score"], reverse=True)
    except Exception:
        return []


def save_score(name, score):
    """Add score to a player's cumulative leaderboard total. Keeps top 10 only."""
    scores = load_scores()
    for entry in scores:
        if entry["name"].lower() == name.lower():
            entry["score"] = entry["score"] + score  # cumulative — always add
            scores = sorted(scores, key=lambda x: x["score"], reverse=True)
            _write(scores)
            return
    # new player
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    _write(scores)


def _write(scores):
    with open(SAVE_FILE, "w") as f:
        json.dump(scores, f, indent=2)


def load_profile():
    """Load persistent profile (unlocks/achievements)."""
    if not os.path.exists(PROFILE_FILE):
        return {}
    try:
        with open(PROFILE_FILE, "r") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def save_profile(profile):
    """Persist profile to disk."""
    try:
        with open(PROFILE_FILE, "w") as f:
            json.dump(profile, f, indent=2)
    except Exception:
        # best-effort: game should still run even if save fails
        pass


def reset_profile() -> None:
    """Overwrite profile.json with the canonical default profile."""
    save_profile(DEFAULT_PROFILE)
