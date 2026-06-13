import json
import os
from resource_path import resource_path

SAVE_FILE    = resource_path("scores.json")
PROFILES_DIR = resource_path("profiles")

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


def _profile_path(name: str) -> str:
    os.makedirs(PROFILES_DIR, exist_ok=True)
    safe = "".join(c for c in name.lower().strip() if c.isalnum() or c in "-_")
    return os.path.join(PROFILES_DIR, f"{safe}.json")


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


def load_profile(name: str = ""):
    """Load persistent profile for the given player name."""
    if not name:
        return {}
    path = _profile_path(name)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def save_profile(profile: dict, name: str = ""):
    """Persist profile to disk for the given player name."""
    if not name:
        return
    path = _profile_path(name)
    try:
        with open(path, "w") as f:
            json.dump(profile, f, indent=2)
    except Exception:
        pass


def reset_profile(name: str = "") -> None:
    """Overwrite a player's profile with the canonical default."""
    save_profile(DEFAULT_PROFILE, name)
