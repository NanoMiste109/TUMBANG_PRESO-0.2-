# Design Document — game-completion-checklist

## Overview

This document describes the technical design for bringing the Tumbang Preso pygame game to 100% completion. The work covers seven areas: code quality, character spritesheets, profile reset, achievement-driven character unlocks, bilingual language support, level 3/4 rework, and audio completion.

The game is a 2-D pygame application running at an internal resolution of 800×600 (scaled to a resizable window). All state is owned by `Game`, which holds an `AssetManager`, a `GameManager`, an `AchievementManager`, and a dictionary of screen objects. Persistence is handled by `SaveManager` via `profile.json` and `scores.json`.

---

## Architecture

```
main.py
  └─ Game (game.py)
       ├─ AssetManager          — images, fonts, sounds
       ├─ GameManager           — global state, settings, profile
       ├─ AchievementManager    — achievement defs, unlock logic
       ├─ screens{}             — one object per screen state
       │    ├─ MenuScreen
       │    ├─ CharacterSelectScreen
       │    ├─ LevelSelectScreen
       │    ├─ GameplayScreen
       │    ├─ SettingsScreen
       │    ├─ PauseScreen
       │    └─ … (credits, how_to_play, leaderboard, intro, name_entry)
       └─ utils/text.py         — TextProvider (new)
```

Key data flows:

- `GameManager.settings["LANGUAGE"]` drives `TextProvider` lookups across all screens.
- `AchievementManager.on_level_cleared(level)` → `GameManager.unlock_character(idx)` → `SaveManager.save_profile()`.
- `AssetManager` is constructed once at startup; all screens hold a reference to it.
- `SettingsScreen` / `PauseScreen` sliders write directly into `GameManager.settings` and call `pygame.mixer` APIs.

---

## Components and Interfaces

### 1. SaveManager (`managers/save_manager.py`)

Add `reset_profile()`:

```python
DEFAULT_PROFILE = {
    "achievements": {
        "clear_level_1": False,
        "clear_level_2": False,
        "clear_level_4": False,
    },
    "unlocked_levels": [1],
    "unlocked_characters": [0],
}

def reset_profile() -> None:
    """Overwrite profile.json with the canonical default profile."""
    save_profile(DEFAULT_PROFILE)
```

`load_profile()` already returns `{}` on missing/malformed files; `GameManager.__init__` must apply the same defaults via `DEFAULT_PROFILE` when the loaded dict is empty.

---

### 2. GameManager (`managers/game_manager.py`)

Changes:
- Import `DEFAULT_PROFILE` from `save_manager` and use it to fill missing keys on startup.
- Add `settings["LANGUAGE"] = "EN"` to the default settings dict.
- `previous_state` already exists; no change needed.

```python
from managers.save_manager import load_profile, save_profile, DEFAULT_PROFILE

class GameManager:
    def __init__(self):
        raw = load_profile() or {}
        # merge defaults so missing keys are always present
        self.profile = {**DEFAULT_PROFILE, **raw}
        self.profile["achievements"] = {
            **DEFAULT_PROFILE["achievements"],
            **raw.get("achievements", {}),
        }
        self.settings = {
            "MUSIC": 100, "SOUND": 100, "SFX": 100,
            "SENSITIVITY": 100, "LANGUAGE": "EN",
        }
        self.unlocked_levels = set(self.profile.get("unlocked_levels", [1])) or {1}
        self.unlocked_characters = set(self.profile.get("unlocked_characters", [0])) or {0}
        # … rest unchanged
```

---

### 3. TextProvider (`utils/text.py`)

Replace the existing `draw_text_outline` helper with a module that also houses `TextProvider`. The old helper is kept for backward compatibility.

```python
class TextProvider:
    """
    Returns UI strings in the active language.
    Falls back to EN if a TL key is missing.
    """
    _STRINGS: dict[str, dict[str, str]] = {
        # key: {"EN": "...", "TL": "..."}
        "menu.play":          {"EN": "PLAY",          "TL": "MAGLARO"},
        "menu.gamemodes":     {"EN": "GAME MODES",    "TL": "MGA LARO"},
        "menu.howtoplay":     {"EN": "HOW TO PLAY",   "TL": "PAANO MAGLARO"},
        "menu.settings":      {"EN": "SETTINGS",      "TL": "MGA SETTING"},
        "menu.credits":       {"EN": "CREDITS",       "TL": "MGA KREDITO"},
        "menu.exit":          {"EN": "EXIT",           "TL": "LUMABAS"},
        "pause.resume":       {"EN": "RESUME",         "TL": "ITULOY"},
        "pause.howtoplay":    {"EN": "HOW TO PLAY",   "TL": "PAANO MAGLARO"},
        "pause.settings":     {"EN": "SETTINGS",      "TL": "MGA SETTING"},
        "pause.exit":         {"EN": "EXIT",           "TL": "LUMABAS"},
        "settings.music":     {"EN": "MUSIC",          "TL": "MUSIKA"},
        "settings.sound":     {"EN": "SOUND",          "TL": "TUNOG"},
        "settings.sfx":       {"EN": "SFX",            "TL": "SFX"},
        "settings.sensitivity":{"EN": "SENSITIVITY",  "TL": "SENSITIVITY"},
        "settings.language":  {"EN": "LANGUAGE",       "TL": "WIKA"},
        "level.cleared":      {"EN": "LEVEL CLEARED!", "TL": "NATAPOS ANG ANTAS!"},
        "level.failed":       {"EN": "LEVEL FAILED!",  "TL": "NABIGO SA ANTAS!"},
        "charselect.hint":    {
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
            return key  # unknown key — return key itself as last resort
        return entry.get(language) or entry.get("EN") or key
```

**PNG-for-EN / font-for-TL hybrid rendering** is handled at the call site in each screen. Screens that currently blit a PNG label check `GameManager.settings["LANGUAGE"]`:

- `"EN"` → blit the existing PNG surface (no change to current code path).
- `"TL"` → call `TextProvider.get(key, "TL")` and render with `ThaleahFat.ttf` at the same size/position as the PNG would occupy.

A helper function `render_label(surface, key, game, rect, font, color=(255,255,255))` will be added to `utils/text.py` to centralise this logic:

```python
def render_label(surface, key, game, rect, font, png_surf=None, color=(255,255,255)):
    """
    Render a UI label respecting the active language.
    EN: blit png_surf at rect (if provided), else render text.
    TL: render text with font, centred on rect.
    """
    lang = game.manager.settings.get("LANGUAGE", "EN")
    if lang == "EN" and png_surf is not None:
        surface.blit(png_surf, rect)
    else:
        text = TextProvider.get(key, lang)
        surf = font.render(text, True, color)
        surface.blit(surf, surf.get_rect(center=rect.center))
```

---

### 4. AssetManager (`managers/asset_manager.py`)

#### 4a. Audio named slots

Add the following named attributes. Where a real file is absent, fall back to an existing sound and print a warning:

```python
# Named audio slots
self.bgm_menu_path     = resource_path("ASSETS/SOUND/moodmode-retro-game-arcade-236133.mp3")
self.bgm_gameplay_path = resource_path("ASSETS/SOUND/BGM_gameplay.mp3")   # placeholder

self.sfx_level_cleared = self._load_sfx_placeholder(
    "ASSETS/SOUND/sfx_level_cleared.mp3", fallback=self.sfx_can_hit, name="sfx_level_cleared")
self.sfx_level_failed  = self._load_sfx_placeholder(
    "ASSETS/SOUND/sfx_level_failed.mp3",  fallback=self.sfx_can_hit, name="sfx_level_failed")
self.sfx_miss          = self._load_sfx_placeholder(
    "ASSETS/SOUND/sfx_miss.mp3",          fallback=self.sfx_whoosh,  name="sfx_miss")
```

Helper:

```python
def _load_sfx_placeholder(self, path, fallback, name):
    full = resource_path(path)
    if not os.path.exists(full):
        print(f"[AssetManager] WARNING: placeholder used for '{name}' — file not found: {full}")
        return fallback
    return pygame.mixer.Sound(full)
```

Gameplay BGM path is stored as a string (not loaded as a Sound) because `pygame.mixer.music` streams from disk.

#### 4b. Gameplay BGM path fallback

```python
if not os.path.exists(self.bgm_gameplay_path):
    print("[AssetManager] WARNING: placeholder used for 'bgm_gameplay' — falling back to menu BGM")
    self.bgm_gameplay_path = self.bgm_menu_path
```

---

### 5. Player / CHARACTER_SHEETS (`entities/player.py`)

`CHARACTER_SHEETS` already has placeholder entries for all four characters. The design requires:

- Entries for indices 0–3 with keys `right`, `up`, `down`, `throw`.
- Placeholder paths reuse Jose's assets until real assets arrive.
- When real assets are dropped into `ASSETS/PLAYER/` with the agreed filenames, no code change is needed.

Agreed filename convention (to be documented in `DOCUMENTATION.md`):

| Character | right | up | down | throw |
|-----------|-------|----|------|-------|
| Jose (0)  | `jose_right.png` | `jose_up.png` | `jose_down.png` | `jose_throw.png` |
| Bong (1)  | `bong_right.png` | `bong_up.png` | `bong_down.png` | `bong_throw.png` |
| Maria (2) | `maria_right.png` | `maria_up.png` | `maria_down.png` | `maria_throw.png` |
| Guard (3) | `guard_right.png` | `guard_up.png` | `guard_down.png` | `guard_throw.png` |

Each spritesheet is a horizontal strip of 6 frames.

---

### 6. AchievementManager (`managers/achievement_manager.py`)

No structural changes needed — the three achievements and their mappings are already defined. The `on_level_cleared` method already handles levels 1, 2, and 4.

The `CharacterSelectScreen` needs two additions:

1. **Padlock on locked cards** — already implemented via `self.padlock`.
2. **Unlock hint on hover** — when `hovered >= 0` and the character is locked, render the achievement description using `TextProvider.get("charselect.locked_hint", lang)` below the card.

```python
# In CharacterSelectScreen.draw(), after drawing the padlock:
if locked and i == self.hovered:
    ach = self._find_achievement_for_character(i)
    hint_text = ach.description if ach else TextProvider.get("charselect.locked_hint", lang)
    hint_surf = self._outlined(self.hint_font, hint_text, (255, 220, 80))
    surface.blit(hint_surf, hint_surf.get_rect(center=(cx, cy + ch // 2 + 30)))
```

A helper `_find_achievement_for_character(char_idx)` looks up `AchievementManager.defs` for the achievement whose `unlocks_character == char_idx`.

---

### 7. SettingsScreen — Language Toggle

Add a language toggle button below the sliders. The toggle cycles `"EN"` ↔ `"TL"` and immediately re-renders labels.

```python
# In SettingsScreen.__init__():
self.lang_btn_rect = pygame.Rect(0, 0, 120, 36)
self.lang_btn_rect.center = (cx, self.bar_rects[-1].bottom + 40)

# In SettingsScreen.update():
if clicked and self.lang_btn_rect.collidepoint(mx, my):
    current = self.game.manager.settings.get("LANGUAGE", "EN")
    self.game.manager.settings["LANGUAGE"] = "TL" if current == "EN" else "EN"

# In SettingsScreen.draw():
lang = self.game.manager.settings.get("LANGUAGE", "EN")
label = f"LANGUAGE: {lang}"
lang_surf = a.settings_font.render(label, True, (255, 255, 255))
surface.blit(lang_surf, lang_surf.get_rect(center=self.lang_btn_rect.center))
pygame.draw.rect(surface, (180, 140, 80), self.lang_btn_rect, 2)
```

The same toggle is available in `PauseScreen` settings panel.

---

### 8. GameplayScreen — Level 3 & 4 Rework

#### Level 3 (Market)

- 3 guards with non-overlapping paths covering horizontal and vertical axes.
- `throws_remaining = 8`, `score.target = 120`, `miss_penalty = 20`.

Guard waypoints (revised):

```python
# Guard 1 — wide horizontal sweep across the top of the play area
Guard(500, 390, [(760, 375), (760, 410), (390, 410), (390, 375)], speed=2.8)
# Guard 2 — vertical patrol on the right side
Guard(620, 430, [(620, 355), (620, 545), (660, 545), (660, 355)], speed=2.6)
# Guard 3 — horizontal sweep across the bottom
Guard(450, 510, [(760, 495), (760, 545), (390, 545), (390, 495)], speed=2.5)
```

#### Level 4 (Field)

- 3 guards with tighter, faster paths.
- `throws_remaining = 6`, `score.target = 150`, `miss_penalty = 25`.

Guard waypoints (revised):

```python
# Guard 1 — tight horizontal at mid-height
Guard(500, 390, [(750, 375), (750, 415), (390, 415), (390, 375)], speed=3.2)
# Guard 2 — vertical patrol, offset right
Guard(580, 450, [(580, 355), (580, 545), (620, 545), (620, 355)], speed=3.0)
# Guard 3 — diagonal-ish bottom sweep
Guard(390, 510, [(390, 490), (390, 545), (750, 545), (750, 490)], speed=3.1)
```

These waypoints are distinct from level 3 and provide a harder challenge through higher speed and tighter coverage.

---

### 9. BGM Transitions (`game.py` / `main.py`)

`Game.start_fade(target_state)` is the natural hook for BGM transitions:

```python
def start_fade(self, target_state):
    # BGM transition
    if target_state == "gameplay":
        pygame.mixer.music.load(self.assets.bgm_gameplay_path)
        pygame.mixer.music.play(-1)
    elif self.manager.game_state == "gameplay":
        # leaving gameplay → restore menu BGM
        pygame.mixer.music.load(self.assets.bgm_menu_path)
        pygame.mixer.music.play(-1)
    # … existing fade logic
```

Volume is preserved because `pygame.mixer.music.set_volume()` is called by the settings sliders and persists across `load()` calls within the same session.

---

## Data Models

### profile.json schema

```json
{
  "achievements": {
    "clear_level_1": false,
    "clear_level_2": false,
    "clear_level_4": false
  },
  "unlocked_levels": [1],
  "unlocked_characters": [0]
}
```

`DEFAULT_PROFILE` in `save_manager.py` is the single source of truth for this schema.

### GameManager.settings

```python
{
    "MUSIC":       100,   # int 0–100
    "SOUND":       100,
    "SFX":         100,
    "SENSITIVITY": 100,
    "LANGUAGE":    "EN",  # "EN" | "TL"
}
```

### CHARACTER_SHEETS (player.py)

```python
{
    0: {"right": str, "up": str, "down": str, "throw": str},  # Jose
    1: {"right": str, "up": str, "down": str, "throw": str},  # Bong
    2: {"right": str, "up": str, "down": str, "throw": str},  # Maria
    3: {"right": str, "up": str, "down": str, "throw": str},  # Guard
}
```

### TextProvider._STRINGS

```python
{
    key: {"EN": str, "TL": str},
    ...
}
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Screen transitions never raise

*For any* valid `(from_state, to_state)` pair in the game's state graph, calling `GameManager.change_state(to_state)` from `from_state` shall complete without raising a Python exception.

**Validates: Requirements 1.2**

---

### Property 2: Player loads all character sheets without error

*For any* character index in `{0, 1, 2, 3}`, constructing a `Player` with that index shall load all four animation strips (right, up, down, throw) without raising a `FileNotFoundError` or `pygame.error`.

**Validates: Requirements 2.2, 2.3**

---

### Property 3: reset_profile is idempotent

*For any* arbitrary content previously written to `profile.json`, calling `reset_profile()` shall always produce a file whose parsed content equals `DEFAULT_PROFILE`, regardless of how many times it is called or what was there before.

**Validates: Requirements 3.2, 3.3**

---

### Property 4: Profile round-trip preserves unlocked characters

*For any* non-empty set of character indices, saving those indices to `profile.json` via `GameManager.save_profile()` and then loading a fresh `GameManager` shall restore exactly the same set of unlocked character indices.

**Validates: Requirements 4.8, 3.4**

---

### Property 5: Achievement unlock is idempotent

*For any* achievement ID in `AchievementManager.defs`, calling `unlock(id)` twice shall produce the same profile state as calling it once — the achievement flag is `true` and `unlock_character` is called exactly once.

**Validates: Requirements 4.4**

---

### Property 6: Level clear triggers correct achievement and character unlock

*For any* level in `{1, 2, 4}`, calling `AchievementManager.on_level_cleared(level)` on a fresh profile shall set the corresponding achievement flag to `true` and add the mapped character index to `unlocked_characters`.

**Validates: Requirements 4.2, 4.3**

---

### Property 7: Locked character selection is blocked

*For any* character index not present in `GameManager.unlocked_characters`, simulating a click or SPACE confirm on that character's card in `CharacterSelectScreen` shall not change `GameManager.selected_character`.

**Validates: Requirements 4.6**

---

### Property 8: TextProvider returns a non-empty string for every defined key and language

*For any* key in `TextProvider._STRINGS` and any language in `{"EN", "TL"}`, `TextProvider.get(key, language)` shall return a non-empty string.

**Validates: Requirements 5.3, 5.4, 5.5**

---

### Property 9: TextProvider uses font rendering for TL on PNG-backed labels

*For any* key that corresponds to a PNG-backed label, when `settings["LANGUAGE"]` is `"TL"`, the `render_label` helper shall produce a surface rendered via `ThaleahFat.ttf` rather than blitting the PNG asset.

**Validates: Requirements 5.10, 5.11**

---

### Property 10: Volume slider sets correct mixer volume

*For any* integer value `v` in `[0, 100]`, setting the MUSIC slider to `v` shall result in `pygame.mixer.music.get_volume()` returning a value within 0.01 of `v / 100.0`; setting the SFX slider to `v` shall result in all game SFX sounds reporting a volume within 0.01 of `v / 100.0`.

**Validates: Requirements 7.10, 7.12**

---

### Property 11: Miss penalty applied correctly for all levels

*For any* level in `{1, 2, 3, 4}`, when a slipper hits a guard or lands without hitting the can, the score shall decrease by exactly `miss_penalty` for that level (subject to floor at 0).

**Validates: Requirements 6.8**

---

## Error Handling

| Scenario | Handling |
|---|---|
| `profile.json` missing at startup | `load_profile()` returns `{}`; `GameManager` merges with `DEFAULT_PROFILE` |
| `profile.json` malformed JSON | `load_profile()` catches `Exception`, returns `{}`; same merge applies |
| Asset file missing at startup | `pygame.image.load` / `pygame.mixer.Sound` raises; `AssetManager` lets it propagate as `FileNotFoundError` with the path in the message |
| Audio placeholder missing | `_load_sfx_placeholder` prints a warning and returns the fallback `Sound` object |
| Gameplay BGM file missing | Falls back to menu BGM path; warning printed |
| `TextProvider.get` called with unknown key | Returns the key string itself (visible in UI, easy to spot during testing) |
| `TextProvider.get` called with unknown language | Falls back to `"EN"` entry |
| `save_profile` write failure | Caught silently; game continues (best-effort persistence) |
| Character index out of range in `CHARACTER_SHEETS` | `CHARACTER_SHEETS.get(character, CHARACTER_SHEETS[0])` falls back to Jose |

---

## Testing Strategy

### Unit Tests (pytest)

Focus on pure logic and data transformations where no pygame display is needed. Use `pygame.display.init()` with a null driver (`SDL_VIDEODRIVER=dummy`) for tests that need pygame surfaces.

Key unit test areas:

- `SaveManager.reset_profile()` — assert file contents match `DEFAULT_PROFILE`.
- `GameManager` default initialisation with missing/malformed `profile.json`.
- `TextProvider.get()` — all keys, both languages, missing key fallback, missing language fallback.
- `AchievementManager.unlock()` — first unlock, duplicate unlock (idempotence).
- `AchievementManager.on_level_cleared()` — levels 1, 2, 4 and a non-mapped level.
- `Score` operator overloading — add, subtract, clamp, `is_complete`.
- `render_label` helper — EN uses PNG surface, TL uses font-rendered surface.

### Property-Based Tests (Hypothesis)

Use [Hypothesis](https://hypothesis.readthedocs.io/) for the correctness properties above. Each test runs a minimum of 100 examples.

Tag format: `# Feature: game-completion-checklist, Property N: <property_text>`

| Property | Hypothesis strategy |
|---|---|
| P1: Screen transitions never raise | `st.sampled_from(valid_state_pairs)` |
| P2: Player loads all character sheets | `st.integers(min_value=0, max_value=3)` |
| P3: reset_profile is idempotent | `st.fixed_dictionaries(...)` for arbitrary profile content |
| P4: Profile round-trip | `st.frozensets(st.integers(0,3), min_size=1)` for character sets |
| P5: Achievement unlock idempotent | `st.sampled_from(list(defs.keys()))` |
| P6: Level clear → achievement + character | `st.sampled_from([1, 2, 4])` |
| P7: Locked character selection blocked | `st.integers(1, 3)` (indices 1–3 start locked) |
| P8: TextProvider non-empty | `st.sampled_from(keys) × st.sampled_from(["EN","TL"])` |
| P9: TL uses font rendering | `st.sampled_from(png_backed_keys)` |
| P10: Volume slider accuracy | `st.integers(0, 100)` |
| P11: Miss penalty correctness | `st.integers(1, 4)` for level |

### Integration Tests

- Full navigation flow: intro → menu → character select → level select → gameplay → level cleared → menu (scripted with `SDL_VIDEODRIVER=dummy`).
- BGM transition: assert correct music file is loaded when entering/leaving gameplay.
- Leaderboard persistence: save a score, reload, assert it appears.

### Manual / Visual Tests

- Language switch: toggle EN↔TL in settings, verify all PNG-backed labels switch to font rendering without layout shift.
- Character unlock flow: start fresh profile, clear level 1, verify Bong unlocks in character select.
- Audio: verify all named SFX play at the correct moments with no missing-file errors.
- Level 3 & 4: play through both levels, verify guard paths, throw counts, score targets, and backgrounds are correct.
