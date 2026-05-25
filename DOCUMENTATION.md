TUMBANG PRESO — Game Development Documentation
 50% Progress Report

---

1. Project Overview

**Game Title:** Tumbang Preso
**Engine/Framework:** Python 3.12 + Pygame 2.6.1
**Genre:** Arcade / Skill-based
**Platform:** Windows (Desktop)

Tumbang Preso is a digital adaptation of the classic Filipino street game. The player throws a slipper to knock down a tin can (lata) guarded by an NPC. The game features two playable levels, a full menu system, animated sprites, and a two-phase aiming mechanic as of the making of this document.

---

2. Project Structure

```
TUMBANG_PRESO/
├── main.py                  — Entry point, game loop
├── game.py                  — Core Game class, screen manager, fade transitions
├── managers/
│   ├── asset_manager.py     — Loads and stores all game assets
│   └── game_manager.py      — Tracks game state, score, unlocked levels
├── entities/
│   ├── player.py            — Player character with sprite animation
│   ├── guard.py             — Guard NPC with waypoint AI
│   ├── can.py               — Tin can with idle and knocked animations
│   ├── slipper.py           — Projectile with physics and gravity
│   ├── background.py        — Parallax scrolling background
│   └── clouds.py            — Animated cloud entities
├── screens/
│   ├── menu_screen.py       — Main menu
│   ├── character_select_screen.py — Character selection before level select
│   ├── level_select_screen.py — Level selection with lock/unlock
│   ├── gameplay_screen.py   — Core gameplay logic
│   ├── pause_screen.py      — In-game pause menu
│   ├── settings_screen.py   — Audio settings with sliders
│   ├── credits_screen.py    — Developer credits
│   └── how_to_play_screen.py — Game instructions
├── ui/
│   ├── power_meter.py       — Two-phase aiming mechanic UI
│   └── button.py            — Reusable button component
├── resource_path.py         — Portable asset path resolver
└── ASSETS/                  — All game assets (sprites, audio, fonts, UI)
```

---

3. Architecture

3.1 Game Loop (main.py + game.py)

The game runs at 60 FPS using `pygame.time.Clock`. The `Game` class manages:
- A virtual canvas of **800×600** pixels scaled to the window size
- A dictionary of screen objects (`menu`, `gameplay`, `level_select`, etc.)
- A **fade transition system** that fades to black between screen changes
- A **parallax background** and animated clouds rendered on every screen

```python
while True:
    game.update(mouse_pos, clicked)
    game.draw()
    scaled_surface = pygame.transform.scale(game.surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))
    clock.tick(60)
```

 3.2 State Management (GameManager)

`GameManager` is a single shared object that tracks:

| Attribute | Description |
|---|---|
| `game_state` | Current active screen ("menu", "gameplay", etc.) |
| `current_level` | Which level is being played (1 or 2) |
| `unlocked_levels` | Set of levels the player has unlocked |
| `score` | Current session score |
| `settings` | Shared audio settings (Music, Sound, SFX, Sensitivity) |
| `selected_character` | Index of the chosen character (0–3, default 0) |
| `previous_state` | The screen that was active before navigating to Settings or How To Play, used to return correctly on ESC |

Level 2 unlocks automatically when the player completes Level 1 (reaches 100 points). This persists for the entire session. The selected character persists across level restarts within the same session.

---

4. Controls

| Input | Action |
|---|---|
| Arrow Keys (Left/Right) | Navigate character cards on select screen |
| Arrow Keys (gameplay) | Move the player in 4 directions |
| SPACE (1st press) | Start aiming — locks throw direction |
| SPACE (2nd press) | Locks throw power and fires the slipper |
| SPACE / ENTER | Confirm character selection |
| Mouse Click | Select a character card or confirm selection |
| ESC | Pause / unpause the game, or go back from a screen |

---

5. Sprites and Characters

5.1 Player (entities/player.py)

The player character is controlled with the arrow keys and uses four separate sprite sheets. The game supports 4 selectable characters — each character has its own set of sprite sheets defined in the `CHARACTER_SHEETS` dictionary at the top of `player.py`. When new character assets are ready, only the file paths in that dictionary need to be updated.

**Characters:**

| Index | Name | Status |
|---|---|---|
| 0 | Jose | Active — current sprite sheets |
| 1 | Maria | Placeholder — uses Jose sprites until assets arrive |
| 2 | Bong | Placeholder — uses Jose sprites until assets arrive |
| 3 | Guard | Placeholder — uses Jose sprites until assets arrive |

| Sprite Sheet | Frames | Used When |
|---|---|---|
| Horizontal Walk | 6 | Walking left or right |
| Upward Walk | 6 | Walking up |
| Downward Walk | 6 | Walking down |
| Throw | 6 | Throwing the slipper |

**Key Methods:**

- `__init__(x, y, character=0)` — Accepts a character index, looks up the matching sprite sheet paths from `CHARACTER_SHEETS`, and loads all four animation sets.
- `move(keys)` — Handles 4-directional movement. Enforces a diagonal boundary (`_x_limit()`) that follows the white court line in the background. The player cannot cross to the right side of this line.
- `_x_limit()` — Calculates the maximum allowed x position based on the player's current y, using linear interpolation between two points on the diagonal line.
- `throw()` — Triggers the throw animation (plays once, then returns to idle).
- `_update_anim()` — Advances the animation frame every `FRAME_DELAY` (6) game frames.
- `draw(surface)` — Selects the correct frame based on movement direction. The sprite is flipped horizontally when facing left, except during the throw animation, which always faces right regardless of the last movement direction.

**Constants:**

| Constant | Value | Purpose |
|---|---|---|
| `SCALE` | 2.0 | Sprite scale multiplier |
| `Y_MIN` | 280 | Upper movement boundary |
| `FRAME_DELAY` | 6 | Frames per animation frame |
| `FOOT_OFFSET` | 14 | Transparent padding at sprite bottom (px) |

---

5.2 Guard NPC (entities/guard.py)

The guard follows a fixed rectangular patrol path defined by waypoints.

**Sprite Sheet:** `guard walking.png` — 6 frames, scaled 2×

**Key Methods:**

- `__init__(x, y, waypoints, speed)` — Accepts a custom waypoint list and speed, allowing different patrol paths and difficulties per level.
- `update(player)` — Moves the guard toward the next waypoint using normalized direction vectors. Advances to the next waypoint when within `SPEED` distance. Updates the collision mask each frame.
- `draw(surface)` — Blits the current animation frame, flipping the sprite horizontally based on movement direction. Calls `_draw_path` before drawing the guard.
- `_draw_path(surface)` — Draws the dotted white patrol path on screen for visibility.

**Level Differences:**

| Level | Guards | Speed | Path |
|---|---|---|---|
| 1 | 1 | 1.8 | Outer rectangle around the can |
| 2 | 2 | 2.2 / 2.5 | Outer + inner rectangle (tighter) |

---

 5.3 Tin Can (entities/can.py)

The can has two animation states:

| State | Sprite File | Frames |
|---|---|---|
| Idle (upright) | `lata knocked v2 (1).png` | 3 |
| Knocked (falling) | `lata knocked.png` | 5 |

Note: the idle sprite filename is a legacy asset name — in code it is loaded as `frames_idle` and displays the can standing upright.

**Key Methods:**

- `hit()` — Triggers the knocked animation (plays once, holds on last frame).
- `update()` — Advances the knock animation frame by frame.
- `reset()` — Returns the can to idle state after a hold timer expires.

Collision detection uses `pygame.mask` (pixel-perfect) rather than bounding rectangles, meaning only actual visible pixels from the slipper and can sprites register a hit — not the transparent padding around them.

---

 5.4 Slipper Projectile (entities/slipper.py)

**Sprite Sheet:** `slipper.png` — 4 frames, scaled 0.8×

The slipper is a physics-based projectile:

- Launched with a velocity vector derived from the locked angle and power
- Subject to gravity (`GRAVITY = 0.08` per frame)
- Speed is capped at 12 px/frame to prevent it flying off screen
- Lands at `ground_y` — calculated as the maximum of the player's foot level and the can's base level at throw time. This ensures the slipper travels far enough to reach the can regardless of the player's vertical position on the court.
- Uses pixel-perfect mask collision

**Key Methods:**

- `__init__(x, y, angle, speed, power, ground_y)` — Spawns the slipper at the given position, computes initial velocity from angle and speed, loads and slices the sprite sheet, and builds the initial collision mask.
- `update()` — Applies gravity to `vel_y` each frame, advances position, cycles the spin animation, and sets `landed = True` when `y >= ground_y`.
- `draw(surface)` — Blits the current animation frame at the slipper's position.

**Physics:**
```
vel_x = cos(angle) × speed
vel_y = sin(angle) × speed
vel_y += GRAVITY  (each frame)
```

---

5.5 Parallax Background (entities/background.py)

The background is composed of multiple image layers that scroll at different speeds to create a depth illusion.

Each layer is a tuple of `(surface, y_position, scroll_speed)`. Layers with `speed = 0` are static (sky, ground overlay). Layers with higher speed values scroll faster, appearing closer to the camera.

**Key Methods:**

- `__init__(layers)` — Accepts the pre-built layer list from `AssetManager` and initializes scroll offsets.
- `update()` — Advances the x offset of each scrolling layer. When a layer scrolls fully off the left edge, it wraps back to the right.
- `draw(surface)` — Tiles each layer horizontally across the canvas to fill the screen width seamlessly.

---

5.6 Clouds (entities/clouds.py)

Animated cloud entities that drift across the top portion of the screen on all screens.

**Key Methods:**

- `__init__(width, height, cloud_images)` — Randomly selects 3 cloud images from the pool, scales each one randomly between 35%–55%, and assigns each a random starting position and drift speed.
- `update(time)` — Moves each cloud left at its drift speed and applies a gentle sine-wave vertical bob using the global time value. Clouds that drift off the left edge respawn at the right.
- `draw(surface)` — Blits each cloud at its current position.

---

 6. Aiming Mechanic (ui/power_meter.py)

The throw uses a two-phase system inspired by classic sports games:

**Phase 1 — Direction:**
- An arrow oscillates between −60° and +60° beside the player
- Press SPACE to lock the angle
- Oscillation: `angle = -60° × sin(timer × 1.5)`

**Phase 2 — Power:**
- A bar oscillates from 0% to 100%
- Press SPACE again to lock power and fire
- Oscillation: `power = (sin(timer × 2.0) + 1) / 2 × 100`

**Key Methods:**

- `start_direction()` — Begins phase 1, sets `phase = "direction"` and resets the timer.
- `lock_direction()` — Captures the current oscillating angle and advances to phase 2 (`phase = "power"`).
- `lock_power()` — Captures the current power value, resets state, and returns `(angle, power)` to the caller to spawn the slipper.
- `reset()` — Cancels the aiming sequence and clears phase state.
- `_current_angle()` — Returns the live oscillating angle in radians for phase 1.
- `_current_power()` — Returns the live oscillating power (0–100) for phase 2.
- `update()` — Advances the internal timer each frame while a phase is active.
- `draw(surface, player_x, player_y)` — Renders the direction arrow and/or power bar depending on the current phase, plus the hint text prompt.

**Scoring based on power:**

| Power Range | Label | Points Awarded |
|---|---|---|
| 1–33 | Weak | 5 pts |
| 34–66 | Medium | 10 pts |
| 67–100 | Strong | 20 pts |

---

7. Level Design

### Level 1
- Score target: **100 points**
- Timer: **5 minutes**
- Miss/guard penalty: **−10 points**
- 1 guard, outer patrol path

### Level 2 (unlocked after completing Level 1)
- Score target: **150 points**
- Timer: **4 minutes**
- Miss/guard penalty: **−15 points**
- 2 guards, outer + inner patrol paths, faster speeds

### Levels 3 and 4
- Locked placeholder slots visible in the level select screen
- Not yet implemented — reserved for the 100% milestone

Score cannot go below 0.

---

8. Audio

| Label | File | Trigger |
|---|---|---|
| Background Music | `retro-game-arcade.mp3` | Loops on game launch |
| Button Click SFX | `ui-button-click.mp3` | Menu button press |
| Button Hover SFX | `button-hover.mp3` | Mouse enters button |

All audio volumes are controllable via the Settings screen sliders (Music, Sound, SFX, Sensitivity).

---

 9. Screens Implemented

| Screen | Description |
|---|---|
| Main Menu | Title, animated parallax background, 6 navigation buttons with hover effects |
| Character Select | 4 character cards with colored backgrounds, arrow key and mouse navigation, confirm with SPACE or ENTER |
| Level Select | Shows unlocked/locked levels with padlock icons |
| Gameplay | Core game with player, guard, can, aiming mechanic, HUD, timer |
| Pause Menu | Resume, How To Play, Settings, Exit — rendered as overlay on gameplay |
| Settings | 4 draggable sliders for audio control |
| How To Play | Game instructions in two-column label/description layout |
| Credits | Developer names and roles in two-column layout |

---

9.1 Character Select Screen (screens/character_select_screen.py)

The character select screen sits between the main menu and level select. The player browses 4 character cards and confirms their choice before entering the game.

**Navigation flow:** Main Menu → Character Select → Level Select → Gameplay

**Key Methods:**

- `__init__(game)` — Initializes fonts and input state flags. Reads the current `selected_character` from `GameManager` so the last selection is remembered if the player returns to this screen.
- `update(mouse_pos, clicked)` — Handles left/right arrow key navigation (single-step per press using held-key guards), mouse click to select a card, SPACE or ENTER to confirm, and ESC to return to the menu.
- `_confirm()` — Writes the selected index to `game.manager.selected_character` and transitions to `level_select`.
- `_card_rect(index)` — Returns the `pygame.Rect` for a given character card, calculated from the card layout constants.
- `draw(surface)` — Renders the title, all four character cards with colored backgrounds and placeholder silhouettes, a gold highlight border on the selected card, character names below each card, and navigation hint text at the bottom.

**Card Layout Constants:**

| Constant | Value | Purpose |
|---|---|---|
| `CARD_W` | 120 | Card width in pixels |
| `CARD_H` | 150 | Card height in pixels |
| `GAP` | 20 | Space between cards |
| `CARD_Y` | 220 | Vertical position of cards |

---

 10. Current Progress (50%)

**Completed:**
- Full menu and navigation system
- 2 playable levels with difficulty scaling
- All core game mechanics (movement, aiming, throwing, scoring)
- Guard AI with waypoint pathfinding
- Sprite animations for all entities
- Audio system with settings
- Level progression and unlock system
- Fade transitions between screens
- Pause menu with sub-panels
- Character select screen with 4 character slots
- Asset path resolution system (`resource_path.py`) for portable distribution

**Remaining (for 100%):**
- Levels 3 and 4
- Sprite sheets for Maria, Bong, and Guard characters
- Additional SFX: slipper throw sound, can hit sound
- Missing aesthetic assets: game mode screen, additional background variants

---

 11. Portable Asset Resolution (resource_path.py)

All asset file paths in the game are resolved through `resource_path()` rather than using raw relative strings. This ensures the game finds its assets correctly regardless of where the folder is extracted or run from.

```python
def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)
```

`sys.argv[0]` always points to `main.py`'s location on disk, so `base_path` is always the project root — not the terminal's current working directory. Every `pygame.image.load()`, `pygame.font.Font()`, and `pygame.mixer.Sound()` call passes its path through this function.

---

 12. Team

| Role | Name |
|---|---|
| Team Leader | Thrisha Mae Lagbo |
| Programmer | Elgyin Roei Ruiz |
| Artist | Janryl Bautista |
| Asset Designer | Braeden Alfonso |
| Project Manager | Charles Andrei Cruz |
| QA | Johannes Afable |


