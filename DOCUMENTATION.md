# TUMBANG PRESO — Game Development Documentation
## Final Version

---

## 1. Project Overview

**Game Title:** Tumbang Preso
**Engine/Framework:** Python 3.12 + Pygame 2.6.1
**Genre:** Arcade / Skill-based
**Platform:** Windows (Desktop)

Tumbang Preso is a digital adaptation of the classic Filipino street game. The player throws a slipper to knock down a tin can (lata) guarded by NPC guards. The game features 4 playable levels, 3 selectable characters (with a 4th unlockable), a special skill system, an achievement system, slipper customisation, a leaderboard, bilingual support (EN/TL), animated sprites, and a two-phase aiming mechanic.

---

## 2. Project Structure

```
TUMBANG_PRESO/
├── main.py                      — Entry point, game loop
├── game.py                      — Core Game class, screen manager, fade + BGM transitions
├── resource_path.py             — Portable asset path resolver
├── managers/
│   ├── asset_manager.py         — Loads and caches all game assets
│   ├── game_manager.py          — Global state: levels, characters, slippers, settings, profile
│   ├── save_manager.py          — Reads/writes profile.json and scores.json
│   └── achievement_manager.py  — Achievement definitions and unlock logic
├── entities/
│   ├── game_object.py           — Abstract base class for all entities
│   ├── player.py                — Player character with per-character sprite sheets
│   ├── guard.py                 — Guard NPC with waypoint patrol AI
│   ├── can.py                   — Tin can with idle/knock animations and optional patrol
│   ├── slipper.py               — Physics-based projectile with per-slipper sprite
│   ├── character.py             — Abstract Character class + JoseCharacter, BongCharacter,
│   │                               MariaCharacter, GuardCharacter with special skills
│   ├── score.py                 — Score class with operator overloading
│   ├── background.py            — Parallax scrolling background
│   ├── clouds.py                — Animated cloud entities
│   └── duck_typing.py           — render_all() helper for heterogeneous entity lists
├── screens/
│   ├── intro_screen.py          — Game intro / splash
│   ├── name_entry_screen.py     — Player name input (first run)
│   ├── menu_screen.py           — Main menu with icons for leaderboard and achievements
│   ├── character_select_screen.py — Character + slipper selection
│   ├── level_select_screen.py   — Level selection with lock/unlock
│   ├── gameplay_screen.py       — Core gameplay logic
│   ├── pause_screen.py          — In-game pause overlay
│   ├── settings_screen.py       — Audio + language settings
│   ├── how_to_play_screen.py    — Game instructions
│   ├── credits_screen.py        — Paginated credits with arrow navigation
│   ├── leaderboard_screen.py    — Cumulative leaderboard
│   └── achievement_screen.py   — Achievement progress screen
├── ui/
│   ├── power_meter.py           — Two-phase aiming mechanic UI
│   └── button.py                — Reusable button component
├── utils/
│   └── text.py                  — TextProvider (EN/TL strings) + render_label helper
├── profile.json                 — Persistent player profile (unlocks, achievements, progress)
└── ASSETS/                      — All game assets (sprites, audio, fonts, UI)
    ├── PLAYER/                  — Character sprite sheets (per-character named files)
    ├── SLIPPER/                 — Slipper sprite sheets (slipper.png, v2, v3, v4)
    ├── GUARD/                   — Guard sprite sheets
    ├── SOUND/BGM/               — Per-level background music
    ├── SOUND/GAME/              — In-game SFX
    ├── SOUND/                   — UI SFX + menu BGM
    └── ThaleahFat/              — ThaleahFat.ttf pixel font
```

---

## 3. Architecture

### 3.1 Game Loop (main.py + game.py)

The game runs at 60 FPS. The `Game` class manages a virtual canvas of **800×600** pixels scaled to the window. It owns an `AssetManager`, `GameManager`, `AchievementManager`, all screen objects, and a `PauseScreen` overlay.

```python
while True:
    game.update(mouse_pos, clicked)
    game.draw()
    scaled = pygame.transform.scale(game.surface, (SCREEN_W, SCREEN_H))
    screen.blit(scaled, (0, 0))
    clock.tick(60)
```

Fade transitions are handled by `Game.start_fade(target_state)` which also triggers BGM swaps between menu and gameplay music.

### 3.2 State Management (GameManager)

`GameManager` is a shared singleton holding all runtime state, loaded from `profile.json` on startup.

| Attribute | Description |
|---|---|
| `game_state` | Current active screen |
| `current_level` | Active level number (1–4) |
| `unlocked_levels` | Set of unlocked level numbers |
| `unlocked_characters` | Set of unlocked character indices |
| `unlocked_slippers` | Set of unlocked slipper indices |
| `selected_character` | Currently chosen character index |
| `selected_slipper` | Currently chosen slipper index |
| `settings` | Dict: MUSIC, SOUND, SFX, LANGUAGE |
| `player_name` | Name entered at first launch |
| `profile` | Full dict synced to profile.json |

### 3.3 Save System (save_manager.py)

Two files are persisted:

- **`profile.json`** — unlocked levels, characters, slippers, achievement flags, and `special_hits` counter. Loaded at startup via `load_profile()`, written via `save_profile()`. A `reset_profile()` function restores defaults.
- **`scores.json`** — leaderboard entries. Each player has a cumulative score that grows every time they complete a level. Top 10 players are kept.

`DEFAULT_PROFILE` in `save_manager.py` is the single source of truth for the initial profile schema.

---

## 4. Controls

| Input | Action |
|---|---|
| Arrow Keys (Left/Right) | Navigate character/slipper cards |
| Arrow Keys (gameplay) | Move player in 4 directions |
| E | Arm / disarm special skill (when available) |
| SPACE (1st press) | Start aiming — lock throw direction |
| SPACE (2nd press) | Lock throw power and fire slipper |
| SPACE / ENTER | Confirm selection on character screen |
| Mouse Click | Select cards, buttons, sliders |
| ESC | Pause during gameplay / return to previous screen |

---

## 5. Characters

### 5.1 Base Class (entities/character.py)

All characters inherit from the abstract `Character` class. Each has:
- `SPECIAL_USES = 3` — maximum uses per level
- `SKILL_NAME` / `SKILL_DESC` — shown on the character select hover card
- `uses_remaining` — tracked at runtime, resets on `setup_level()`
- `consume_special_use()` — decrements counter; returns False if empty
- `compute_hit_points(power, special_active)` — returns score for a hit
- `miss_penalty_amount(committed, special_active, normal_penalty)` — returns deduction on miss

### 5.2 Characters

| # | Name | Unlock | Special Skill | Effect |
|---|---|---|---|---|
| 0 | Jose | Default | Steady Aim | Boosts throw power by 15 (capped at 110) for higher scoring |
| 1 | Bong | Clear Level 1 | Doble Hampas | Doubles hit points on a successful throw |
| 2 | Maria | Clear Level 2 | Tiyaga | Grants +1 bonus throw; miss penalty is doubled |

### 5.3 Player Sprites (entities/player.py)

Each character has 4 sprite sheets defined in `CHARACTER_SHEETS`:

| Key | File Pattern | Frames |
|---|---|---|
| right | `{name}_horizontal.png` | Auto-detected |
| up | `{name}_upward.png` | Auto-detected |
| down | `{name}_downward.png` | Auto-detected |
| throw | `{name}_throw.png` | Auto-detected |

Frame count is auto-detected from image dimensions (width ÷ height). All characters are scaled to match Jose's height (136px). Missing files fall back to Jose's existing assets. Maria's throw sheet faces left by default and is pre-flipped on load.

---

## 6. Slippers

| # | Name | Unlock | Behaviour |
|---|---|---|---|
| 0 | Default | Always | `slipper.png` |
| 1 | Street | Clear Level 2 | `slipper_v2.png` |
| 2 | Pro | Hit can with special 3× | `slipper_v3.png` |
| 3 | Champion | Clear Level 4 | `slipper_v4.png` |

Slippers are cosmetic — they look different but behave identically. The selected slipper index is passed to `Slipper.__init__` which loads the matching sheet. Falls back to default if the file is missing.

---

## 7. Achievement System

Achievements are defined in `AchievementManager` and flags are stored in `profile.json`.

| ID | Name | Condition | Reward |
|---|---|---|---|
| clear_level_1 | Barangay Rookie | Clear Level 1 | Unlocks Bong |
| clear_level_2 | Street Legend | Clear Level 2 | Unlocks Maria + Street Slipper |
| clear_level_4 | Tumbang Preso Master | Clear Level 4 | Unlocks Guard + Champion Slipper |
| slipper_v3 | Special Master | Hit can with special 3× (persistent) | Unlocks Pro Slipper |

Progress toward Special Master (`special_hits`) is shown on the Achievements screen with a `Progress: X/3` indicator.

---

## 8. Level Design

| Level | Background | Guards | Throws | Score Target | Moving Can | Miss Penalty |
|---|---|---|---|---|---|---|
| 1 | Kalsada (Street) | 1 (rect patrol) | 10 | 100 | No | −10 |
| 2 | Park | 2 (rect patrols) | 8 | 100 | No | −15 |
| 3 | Market | 2 (horizontal sweeps) | 8 | 120 | No | −20 |
| 4 | Field | 3 (top/bottom/vertical) | 6 | 100 | Yes (vertical) | −25 |

Level 4 features a tin can that moves vertically between y=360 and y=480 at speed 1.2. The can's patrol is cleared on `reset()` so it does not carry over to other levels.

Score cannot drop below 0. Each level unlocks the next on completion.

---

## 9. Aiming Mechanic (ui/power_meter.py)

**Phase 1 — Direction:** An arrow oscillates ±60° next to the player. Press SPACE to lock.

**Phase 2 — Power:** A bar oscillates 0–100%. Press SPACE to lock and fire.

**Scoring:**

| Power | Points |
|---|---|
| 1–33 (Weak) | 5 |
| 34–66 (Medium) | 10 |
| 67–100 (Strong) | 20 |

Special skills modify these values via `character.compute_hit_points()`.

---

## 10. Audio

| Sound | Controlled By |
|---|---|
| Menu BGM | MUSIC slider |
| Level 1–4 BGM (per-level) | MUSIC slider |
| Throw SFX | SFX slider |
| Can Hit SFX | SFX slider |
| Miss SFX | SFX slider |
| Level Cleared SFX | SFX slider |
| Level Failed SFX | SFX slider |
| Button Click | SOUND slider |
| Button Hover | SOUND slider |

BGM transitions automatically on fade: entering gameplay loads the level-specific BGM; leaving gameplay restores the menu BGM.

---

## 11. Settings

| Option | Function |
|---|---|
| MUSIC slider | BGM volume |
| SOUND slider | UI click/hover volume |
| SFX slider | All in-game sound effects |
| Language toggle (EN / TL) | Switches UI text language |

---

## 12. Language Support (utils/text.py)

`TextProvider` holds all UI strings for English (`EN`) and Tagalog (`TL`). Falls back to EN for missing keys. The `render_label()` helper blits PNG assets in EN mode and renders ThaleahFat font in TL mode, preserving layout without requiring duplicate PNG assets per language.

Covered contexts: menu buttons, pause buttons, settings labels, level cleared/failed messages, character select hints.

---

## 13. Screens

| Screen | Access | Notes |
|---|---|---|
| Intro | Auto on launch | — |
| Name Entry | First run only | Name persists in GameManager |
| Main Menu | After intro / game | Trophy icons for leaderboard + achievements |
| Character Select | PLAY | Shows 3 characters + slipper selector row |
| Level Select | After character confirmed | ESC returns to character select |
| Gameplay | Level selected | Full HUD, special skill indicator, pause |
| Pause (overlay) | ESC in gameplay | Sub-panels: main, settings, how to play |
| Level Cleared | Score target reached | Next level or menu |
| Level Failed | Throws exhausted | Retry or menu |
| Settings | Menu or Pause | 3 sliders + language toggle |
| How To Play | Menu or Pause | Two-column instructions |
| Credits | Menu | Paginated, arrow navigation, 5 pages |
| Leaderboard | Trophy icon (menu) | Cumulative scores, top 10 |
| Achievements | Green trophy icon (menu) | 4 achievements with progress indicators |
| Game Modes | Menu button | Shows "Coming Soon" popup |

---

## 14. Polymorphism and OOP Design

The codebase uses Python's ABC (`Abstract Base Class`) pattern throughout:

- `GameObject` (abstract) → `Player`, `Guard`, `Can`, `Slipper` all override `update()`, `draw()`, `interact()`
- `Character` (abstract) → `JoseCharacter`, `BongCharacter`, `MariaCharacter`, `GuardCharacter` each override `attack()`, `special_skill()`, `compute_hit_points()`, `miss_penalty_amount()`
- `Score` uses operator overloading: `__add__`, `__sub__`, `__ge__`, `__str__`, `is_complete()`
- `Player.move()` uses Python's default-argument pattern to simulate method overloading (keyboard-driven vs. scripted delta)
- `render_all()` in `duck_typing.py` demonstrates duck typing by calling `.draw(surface)` on any entity list without type checks

---

## 15. Portable Asset Resolution (resource_path.py)

All asset paths pass through `resource_path()` to ensure the game finds its files regardless of where it is run from. This makes the packaged/distributed game work correctly.

```python
def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)
```

---

## 16. Team

| Role | Name |
|---|---|
| Team Leader | Thrisha Mae Lagbo |
| Programmer | Elgyin Roei Ruiz |
| Sprite Artist | Janryl Bautista |
| UI / Level Artist | Braeden Alfonso |
| SFX Artist | Michael Prande |
| Also By | Charles Andrei Cruz |
| Also By | Johannes Afable |
