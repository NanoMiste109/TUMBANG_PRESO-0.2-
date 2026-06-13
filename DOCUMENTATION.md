# TUMBANG PRESO — Game Development Documentation
## Final Version

---

## 1. Game Overview

**Game Title:** Tumbang Preso
**Engine / Framework:** Python 3.12 + Pygame 2.6.1
**Genre:** Arcade / Skill-based
**Platform:** Windows (Desktop)
**Target Audience:** Filipino students and casual gamers aged 10–25

Tumbang Preso is a digital adaptation of the classic Filipino street game. The player throws a slipper to knock down a tin can (lata) guarded by NPC guards. The game features 4 playable levels of increasing difficulty, 4 selectable characters (3 default + 1 unlockable), a special skill system per character, 4 slipper types (1 default + 3 unlockable), an achievement system, a persistent leaderboard, bilingual support (English / Tagalog), animated sprites, and a two-phase aiming mechanic.

---

## 2. Storyline and Objectives

### Storyline

In the streets and plazas of the Philippines, Tumbang Preso has been a beloved childhood game for generations. Players compete to knock down a tin can guarded by a designated "taga" (guard). You step into the shoes of a street-smart kid determined to master the throw and beat every level.

### Objectives

- Knock the tin can down enough times to meet the score target for each level.
- Avoid throwing the slipper into the guard — a missed throw deducts points.
- Clear all 4 levels to unlock every character and slipper type.
- Earn achievements and climb the leaderboard.

---

## 3. Gameplay Mechanics

### 3.1 Two-Phase Aiming

Throwing the slipper is a two-step process controlled with the SPACE key:

**Phase 1 — Direction:**
An arrow rotates ±60° around the player. Press SPACE to lock the throw direction.

**Phase 2 — Power:**
A power bar oscillates from 0% to 100%. Press SPACE again to lock the power and fire the slipper.

### 3.2 Scoring

| Power Range | Hit Category | Points |
|---|---|---|
| 1–33% | Weak | 5 pts |
| 34–66% | Medium | 10 pts |
| 67–100% | Strong | 20 pts |

Score cannot drop below 0. The score target must be reached before throws run out to clear the level.

### 3.3 Miss Penalty

Missing the can (slipper lands or hits a guard) deducts points. The penalty amount increases with each level and is affected by active special skills.

### 3.4 Special Skills

Each character has a unique special skill that can be activated up to 3 times per level. Pressing E arms the skill; pressing SPACE while armed activates it on the next throw.

### 3.5 Slipper Abilities

Unlockable slippers each have a one-time in-flight ability activated by pressing G while the slipper is airborne (or before throwing, for the Street Slipper).

### 3.6 Player Movement

The player character moves in 4 directions using the Arrow Keys. Repositioning allows different throw angles toward the can.

### 3.7 Controls

| Input | Action |
|---|---|
| Arrow Keys | Move player (4 directions) |
| E | Arm / disarm character special skill |
| SPACE (1st press) | Start aiming — lock throw direction |
| SPACE (2nd press) | Lock throw power and fire slipper |
| G | Activate slipper ability (mid-flight or before throw) |
| SPACE / ENTER | Confirm selection on menus |
| Mouse Click | Select cards, buttons, sliders |
| ESC | Pause during gameplay / return to previous screen |

---

## 4. Characters and Assets

### 4.1 Characters

| # | Name | Unlock Condition | Special Skill | Effect |
|---|---|---|---|---|
| 0 | Jose | Default (always available) | Steady Aim | Boosts throw power by 15 (capped at 110) for a higher-scoring hit |
| 1 | Bong | Clear Level 1 | Doble Hampas | Doubles hit points on a successful throw |
| 2 | Maria | Clear Level 2 | Tiyaga | Grants +1 bonus throw; miss penalty is doubled if activated |

All characters have 3 special uses per level. The miss penalty when a special is active (except Maria) is the would-have-scored points plus 10.

### 4.2 Character Sprites

Each character uses 4 directional sprite sheets:

| Direction | File Pattern |
|---|---|
| Horizontal (walk right) | `{name}_horizontal.png` |
| Upward walk | `{name}_upward.png` |
| Downward walk | `{name}_downward.png` |
| Throw animation | `{name}_throw.png` |

Frame count is auto-detected from the image dimensions. All characters are scaled to a uniform height (136 px). Maria's throw sprite is pre-flipped on load since it faces left by default.

### 4.3 Slippers

| # | Name | Unlock Condition | Special Ability (G key) |
|---|---|---|---|
| 0 | Default Slipper | Always available | None |
| 1 | Rocket Slipper | Clear Level 2 | Rocket boost — doubles speed mid-flight |
| 2 | Triple Slipper | Hit can with special 3× (persistent) | Split shot — spawns 2 extra slippers at spread angles |
| 3 | Bolt Slipper | Clear Level 4 | Pikachu Stun — stuns the guard on hit instead of taking a miss penalty |

### 4.4 Guard NPC

The guard (`entities/guard.py`) is an NPC that patrols a defined set of waypoints. It uses 3 directional sprite sheets (walk, upward, downward). If hit by the Champion Slipper's Pikachu Stun ability, the guard is frozen for 3 seconds (180 frames) with no miss penalty applied.

---

## 5. Level Design

| Level | Background | Score Target | Throws | Miss Penalty | Guards | Moving Can |
|---|---|---|---|---|---|---|
| 1 | Kalsada (Street) | 100 pts | 10 | −10 pts | 1, rectangular patrol | No |
| 2 | Park | 100 pts | 8 | −15 pts | 2, rectangular patrols | No |
| 3 | Market | 120 pts | 8 | −20 pts | 2, vertical oscillation (opposite phase) | No |
| 4 | Field | 100 pts | 6 | −25 pts | 1, fast vertical patrol | Yes (vertical) |

**Level 3 Detail:** Two guards patrol vertically in opposite directions — when one moves down, the other moves up, creating a gap-and-block rhythm the player must time their throw around.

**Level 4 Detail:** The tin can itself moves vertically between y=360 and y=480 at speed 1.2. A single fast guard (speed 3.8) also patrols vertically, making targeting significantly more difficult.

---

## 6. User Interface Design

### 6.1 Screen Flow

```
Intro Screen
    └── Name Entry (first launch only)
        └── Main Menu
            ├── PLAY → Character Select → Level Select → Gameplay
            │                                               ├── Pause Overlay
            │                                               ├── Level Cleared Overlay
            │                                               └── Level Failed Overlay
            ├── SETTINGS
            ├── HOW TO PLAY
            ├── CREDITS
            ├── GAME MODES (Coming Soon popup)
            ├── Leaderboard (trophy icon)
            └── Achievements (green trophy icon)
```

### 6.2 In-Game HUD

| Element | Position | Description |
|---|---|---|
| Score display | Top-left | "SCORE: X / TARGET" — uses Score.__str__ |
| Special indicator | Below score | Shows uses remaining, ARMED, ACTIVE, or NONE |
| Slipper ability indicator | Below special | Shows ability status (if slipper > 0) |
| Throw counter | Bottom-right | Turns red when ≤ 3 throws remain |
| ESC hint | Top-right | ESC key icon + "TO PAUSE" |
| Power meter | Near player | Direction arrow (phase 1) and power bar (phase 2) |

### 6.3 Parallax Background

The main menu uses a multi-layer parallax background (`entities/background.py`) with scrolling cloud layers (`entities/clouds.py`).

---

## 7. Development Process

### 7.1 Architecture Overview

The game follows a layered MVC-inspired architecture:

- **`main.py`** — Entry point. Handles the OS window, pygame event loop, and scales the 800×600 virtual canvas to the display window.
- **`game.py`** — Core `Game` class. Owns all screens, managers, and handles fade transitions and BGM swaps.
- **`managers/`** — Singleton-style managers for assets, game state, save data, and achievements.
- **`entities/`** — All game objects inheriting from the abstract `GameObject` base class.
- **`screens/`** — Each screen is a self-contained class with `update()` and `draw()` methods.
- **`ui/`** — Reusable UI components (power meter, button).
- **`utils/`** — Text rendering and bilingual string management.

### 7.2 Game Loop

The game runs at 60 FPS. A virtual 800×600 surface is scaled to the actual window size each frame:

```python
while True:
    game.update(mouse_pos, clicked)
    game.draw()
    scaled = pygame.transform.scale(game.surface, (SCREEN_W, SCREEN_H))
    screen.blit(scaled, (0, 0))
    clock.tick(60)
```

### 7.3 State Management

`GameManager` is a shared state object loaded from `profile.json` at startup. It tracks the current screen, selected character and slipper, unlocked content, settings, and player name.

### 7.4 Save System

Two JSON files are persisted locally:

- **`profile.json`** — Unlocked levels, characters, slippers, achievement flags, and special hit counter.
- **`scores.json`** — Leaderboard entries. Each player has a cumulative score; the top 10 players are kept.

### 7.5 OOP Design Principles

**Inheritance and Abstraction:**
- `GameObject` (ABC) → `Player`, `Guard`, `Can`, `Slipper` each override `update()`, `draw()`, `interact()`
- `Character` (ABC) → `JoseCharacter`, `BongCharacter`, `MariaCharacter`, `GuardCharacter` each override `attack()`, `special_skill()`, `compute_hit_points()`, `miss_penalty_amount()`

**Polymorphism:**
- `render_all()` in `duck_typing.py` calls `.draw(surface)` on any list of entities without type-checking — demonstrating duck typing
- Each `Character` subclass overrides `compute_hit_points()` and `miss_penalty_amount()` with its own behavior

**Operator Overloading (`entities/score.py`):**
- `Score` implements `__add__`, `__sub__`, `__ge__`, `__str__`, and `is_complete()` so score arithmetic reads naturally in gameplay code

**Method Overloading Pattern:**
- `Player.move()` uses Python's default argument pattern to support both keyboard-driven and scripted delta movement

### 7.6 Asset Pipeline

All asset paths are resolved through `resource_path()` which uses `sys.argv[0]` as the base directory. This ensures the game finds its files both in development and when packaged as an executable.

```python
def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)
```

---

## 8. Challenges Encountered and Solutions

| Challenge | Solution |
|---|---|
| Scaling assets across window resize | Render everything to a fixed 800×600 virtual surface, then scale to window each frame |
| Character sprites of different sizes | Auto-detect frame count from sheet width; scale all characters to a uniform height of 136 px |
| Maria's throw sprite faces left | Pre-flip the sprite sheet on load so it faces right consistently |
| Slipper and guard collision accuracy | Use per-pixel `pygame.mask` collision instead of rect-based checks |
| Achievement unlock on level clear | Achievement system flags `clear_level_4` and grants slipper unlocks via `AchievementManager.on_level_cleared()` |
| Special hit counter persisting across sessions | `special_hits` counter is stored in `profile.json` and incremented on every special hit across any session |
| BGM not transitioning smoothly between screens | `Game.start_fade()` triggers BGM swaps mid-fade so music changes are not jarring |
| Exe packaging with loose asset files | `resource_path()` resolves paths relative to the executable rather than the Python source file |

---

## 9. Future Improvements

- **Slipper passive perks** — Give each slipper a passive stat modifier beyond cosmetics
- **Game Modes screen** — Currently shows "Coming Soon"; planned modes include Time Attack and Endless
- **Real SFX** — Replace placeholder audio files for miss, level cleared, and level failed
- **Mobile port** — Touch input adaptation for Android
- **Multiplayer / local co-op** — Two players take turns, competing for score on the same can
- **Expanded levels** — Additional environments beyond the current 4

---

## 10. Team

| Role | Name |
|---|---|
| Team Leader | Thrisha Mae Lagbo |
| Programmer | Elgyin Roei Ruiz |
| Sprite Artist | Janryl Bautista |
| UI / Level Artist | Braeden Alfonso |
| SFX Artist | Michael Prande |
| Also By | Charles Andrei Cruz |
| Also By | Johannes Afable |

---

## 11. Development Tools and Technologies

| Tool / Technology | Purpose |
|---|---|
| Python 3.12 | Core programming language |
| Pygame 2.6.1 | Game engine (rendering, input, audio) |
| PyInstaller | Packaging game as a Windows .exe |
| VS Code / Kiro IDE | Development environment |
| Figma | UI mockups and sprite layout |
| Audacity / AudioMass | Audio editing and trimming |
| Git | Version control |

---

*Document prepared for PUP Parañaque — Final Project Presentation*
