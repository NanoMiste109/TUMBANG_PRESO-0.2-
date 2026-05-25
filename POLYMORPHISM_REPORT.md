# Activity 3: Building a Polymorphic Game System Using Python OOP

---

## Title of the Game

**Tumbang Preso — Digital Larong Pinoy**

---

## Group Members

| Role | Name |
|---|---|
| Team Leader | Thrisha Mae Lagbo |
| Programmer | Elgyin Roei Ruiz |
| Artist | Janryl Bautista |
| Asset Designer | Braeden Alfonso |
| Project Manager | Charles Andrei Cruz |
| QA | Johannes Afable |

---

## Game Description

Tumbang Preso is a desktop game built with Python and Pygame, inspired by the traditional Filipino street game of the same name. The player controls a character who throws a slipper (tsinelas) to knock down a tin can (lata) that is guarded by one or more NPC guards. The game features a two-phase aiming mechanic, animated sprites, a parallax scrolling background, multiple levels with increasing difficulty, and a full menu and navigation system.

The game is a digital modernization of a classic Filipino cultural game, designed to be accessible to both Filipino and international players through an interactive desktop experience.

---

## Objectives of the Game

- Knock the tin can by throwing the slipper before running out of throws
- Reach the score target for each level to progress to the next
- Avoid hitting the guards — doing so deducts points
- Complete all levels to win

**Scoring:**

| Throw Power | Points Awarded |
|---|---|
| Weak (1–33%) | +5 pts |
| Medium (34–66%) | +10 pts |
| Strong (67–100%) | +20 pts |

**Penalties:**
- Hitting a guard: −10 to −25 pts (scales per level)
- Missing the can: −10 to −25 pts (scales per level)
- Score cannot go below 0

---

## Classes and Objects Used

### Entity Classes

| Class | File | Description |
|---|---|---|
| `GameObject` | `entities/game_object.py` | Abstract base class for all game entities |
| `Player` | `entities/player.py` | Player character with 4-directional movement and throw animation |
| `Guard` | `entities/guard.py` | NPC guard that patrols a waypoint path |
| `Can` | `entities/can.py` | Tin can with idle and knocked animation states |
| `Slipper` | `entities/slipper.py` | Physics-based projectile with gravity |
| `Score` | `entities/score.py` | Score tracker with operator overloading |

### Manager Classes

| Class | File | Description |
|---|---|---|
| `GameManager` | `managers/game_manager.py` | Tracks game state, level, score, unlocked levels |
| `AssetManager` | `managers/asset_manager.py` | Loads and stores all sprites, fonts, sounds |
| `AchievementManager` | `managers/achievement_manager.py` | Tracks and triggers achievement events |

### Screen Classes

| Class | File | Description |
|---|---|---|
| `GameplayScreen` | `screens/gameplay_screen.py` | Core gameplay logic, HUD, level/gameover overlays |
| `MenuScreen` | `screens/menu_screen.py` | Main menu with animated background |
| `LevelSelectScreen` | `screens/level_select_screen.py` | Level selection with lock/unlock display |
| `CharacterSelectScreen` | `screens/character_select_screen.py` | Character selection before level select |
| `PauseScreen` | `screens/pause_screen.py` | In-game pause overlay |
| `SettingsScreen` | `screens/settings_screen.py` | Audio settings with draggable sliders |
| `CreditsScreen` | `screens/credits_screen.py` | Developer credits |
| `HowToPlayScreen` | `screens/how_to_play_screen.py` | Game instructions |

### UI Classes

| Class | File | Description |
|---|---|---|
| `PowerMeter` | `ui/power_meter.py` | Two-phase aiming mechanic (direction + power) |

### Utility Modules

| Module | File | Description |
|---|---|---|
| `render_all` / `update_all` | `entities/duck_typing.py` | Duck typing utility functions |
| `resource_path` | `resource_path.py` | Portable asset path resolver |

---

## Explanation of Polymorphism Concepts Applied

### 1. Method Overriding

**What it is:** A child class provides its own implementation of a method defined in the parent class.

**How it is applied:**

A base class `GameObject` was created in `entities/game_object.py`. It defines three methods — `update()`, `draw()`, and `interact()` — that every game entity is expected to override with its own behavior.

All four entity classes (`Player`, `Guard`, `Can`, `Slipper`) inherit from `GameObject` and override these methods. Each class performs a completely different action under the same method name.

| Class | `update()` behavior | `draw()` behavior | `interact()` behavior |
|---|---|---|---|
| `Player` | Advances animation frame | Renders directional sprite | Triggers throw animation |
| `Guard` | Moves along waypoints, updates mask | Renders directional guard sprite + patrol path | Placeholder for stun reaction |
| `Can` | Advances knock animation | Renders idle or knocked frame | Triggers `hit()` — starts knock animation |
| `Slipper` | Applies gravity, moves projectile | Renders spinning slipper frame | Marks slipper as landed, stops velocity |

---

### 2. Method Overloading

**What it is:** A method behaves differently depending on the arguments passed to it. Python achieves this through default and optional parameters.

**How it is applied:**

`Player.move()` was redesigned to accept two different call signatures:

- `move(keys)` — reads keyboard input from Pygame and moves the player based on arrow key presses. This is the normal gameplay path.
- `move(dx=n, dy=n)` — moves the player by an explicit pixel delta, with no key input required. This is used for scripted movement, cutscenes, or testing.

The method checks which arguments were provided and executes the appropriate branch. Both signatures share the same method name and the same boundary clamping logic.

---

### 3. Operator Overloading

**What it is:** Custom behavior is defined for built-in Python operators (`+`, `-`, `>`, etc.) when applied to objects of a custom class.

**How it is applied:**

A `Score` class was created in `entities/score.py`. It wraps the integer score value and overloads the following operators:

| Operator | Method | Behavior |
|---|---|---|
| `score += pts` | `__iadd__` | Adds points, clamps to target |
| `score -= penalty` | `__isub__` | Subtracts penalty, floors at 0 |
| `score + pts` | `__add__` | Returns a new Score object |
| `score - pts` | `__sub__` | Returns a new Score object |
| `score > other` | `__gt__` | Compares two Score objects or an int |
| `score >= other` | `__ge__` | Compares two Score objects or an int |
| `int(score)` | `__int__` | Returns the raw integer value |
| `str(score)` | `__str__` | Returns `"75 / 100"` format for HUD display |

The `Score` object is used directly in `GameplayScreen` for all scoring operations, and `str(score)` is used to render the HUD score text.

---

### 4. Duck Typing

**What it is:** Objects are used based on what methods they have, not what class they belong to. If an object has the right method, it works — no `isinstance()` check needed.

**How it is applied:**

Two utility functions were created in `entities/duck_typing.py`:

- `render_all(entities, surface)` — calls `.draw(surface)` on every object in the list
- `update_all(entities, **kwargs)` — calls `.update(**kwargs)` on every object in the list

These functions accept any list of objects. They do not check the type of each object — they only check whether the object has the method (`hasattr`). This means `Player`, `Guard`, `Can`, and `Slipper` can all be passed into the same function call, and each one draws itself correctly using its own overridden `draw()` implementation.

In `GameplayScreen.draw()`, the rendering loop was replaced with:

```python
render_all(self.guards, surface)
render_all([self.can, self.slipper, self.player], surface)
```

This is duck typing in action — the function does not care whether it is drawing a guard, a can, or a slipper. It only cares that the object can be drawn.

---

## Code Explanations

### `entities/game_object.py` — Base Class

```python
class GameObject:
    def update(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__} must implement update()")

    def draw(self, surface):
        raise NotImplementedError(f"{self.__class__.__name__} must implement draw()")

    def interact(self, other=None):
        pass
```

`GameObject` is the abstract base for all entities. `update()` and `draw()` raise `NotImplementedError` if a subclass forgets to override them — this enforces the contract. `interact()` has a default empty implementation since not all entities need to react to others.

---

### `entities/player.py` — Method Overloading + Overriding

```python
class Player(GameObject):

    def move(self, keys=None, *, dx=None, dy=None):
        if dx is not None or dy is not None:
            # Scripted movement — direct delta
            if dx is not None:
                self.x = max(0, min(self.x + dx, self.X_MAX - self.frame_w))
                self.facing_right = dx >= 0
            if dy is not None:
                self.y = max(self.Y_MIN, min(self.y + dy, 600 - self.frame_h + self.FOOT_OFFSET))
            self.moving = True
            self.rect.topleft = (self.x, self.y)
            return

        # Keyboard-driven movement
        self.moving = False
        if keys[pygame.K_UP] and self.y > self.Y_MIN:
            self.y -= self.speed
            ...

    def update(self, keys=None, **kwargs):
        """Override: advance animation state."""
        self._update_anim()

    def interact(self, other=None):
        """Override: trigger throw animation when interacting with an object."""
        if other is not None:
            self.throw()
```

`move()` demonstrates method overloading — the same method name handles both keyboard input and scripted delta movement depending on which arguments are passed. `update()` and `interact()` demonstrate method overriding — they replace the base class implementations with Player-specific behavior.

---

### `entities/score.py` — Operator Overloading

```python
class Score:
    def __init__(self, value: int = 0, target: int = 100):
        self.target = target
        self._value = max(0, min(value, target))

    def __iadd__(self, points):
        self.value = self._value + int(points)
        return self

    def __isub__(self, penalty):
        self.value = self._value - int(penalty)
        return self

    def __gt__(self, other):
        other_val = other.value if isinstance(other, Score) else int(other)
        return self._value > other_val

    def __str__(self):
        return f"{self._value} / {self.target}"
```

The `Score` class wraps the integer score and overloads arithmetic and comparison operators. The `value` setter automatically clamps the score between 0 and `target`, so the clamping logic does not need to be repeated at every scoring call site. `__str__` returns the formatted HUD string directly.

**Usage in GameplayScreen:**

```python
# Hit — operator overloading: Score.__iadd__
self.score += pts

# Miss — operator overloading: Score.__isub__
self.score -= self.miss_penalty

# Check win condition
if self.score.is_complete():
    self.state = "complete"

# HUD display — Score.__str__
score_str = f"SCORE: {self.score}"   # → "SCORE: 75 / 100"
```

---

### `entities/duck_typing.py` — Duck Typing

```python
def render_all(entities, surface):
    for entity in entities:
        if entity is not None and hasattr(entity, "draw"):
            entity.draw(surface)

def update_all(entities, **kwargs):
    for entity in entities:
        if entity is not None and hasattr(entity, "update"):
            entity.update(**kwargs)
```

`render_all()` and `update_all()` accept any list of objects. There are no `isinstance()` checks — the functions only verify that the object has the expected method using `hasattr`. This means any future entity added to the game will work automatically as long as it implements `draw()` and `update()`, regardless of its class hierarchy.

**Usage in GameplayScreen:**

```python
# Duck typing: draws Guard, Can, Slipper, and Player
# through the same function — no type checks needed
render_all(self.guards, surface)
render_all([self.can, self.slipper, self.player], surface)
```

---

### `entities/guard.py` — Method Overriding

```python
class Guard(GameObject):

    def update(self, player=None, **kwargs):
        """Override: patrol waypoints and advance animation."""
        tx, ty = self.WAYPOINTS[self.wp_index]
        cx = self.x + self.frame_w // 2
        dx = tx - cx
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < self.SPEED:
            self.wp_index = (self.wp_index + 1) % len(self.WAYPOINTS)
        else:
            self.x += (dx / dist) * self.SPEED
            self.y += (dy / dist) * self.SPEED
        ...

    def draw(self, surface):
        """Override: render guard sprite based on movement direction."""
        ...

    def interact(self, other=None):
        """Override: placeholder for stun/reaction when hit by slipper."""
        pass
```

`Guard` overrides all three `GameObject` methods. Its `update()` implements waypoint pathfinding using normalized direction vectors — completely different from `Player.update()` which advances animation frames, or `Can.update()` which advances a knock animation. Same method name, entirely different behavior.

---

### `entities/can.py` — Method Overriding

```python
class Can(GameObject):

    def update(self, **kwargs):
        """Override: advance knock animation frame."""
        if not self.knocked:
            return
        self.anim_timer += 1
        if self.anim_timer >= self.FRAME_DELAY:
            self.anim_timer = 0
            if self.anim_frame < self.KNOCK_FRAMES - 1:
                self.anim_frame += 1

    def draw(self, surface):
        """Override: render idle or knocked animation frame."""
        frame = self.frames_knock[self.anim_frame] if self.knocked else self.frames_idle[0]
        surface.blit(frame, (self.x, self.y))

    def interact(self, other=None):
        """Override: can reacts to being hit — triggers knock animation."""
        self.hit()
```

`Can.interact()` is the most direct use of the `interact()` override — when the slipper collides with the can, calling `can.interact()` triggers the knock animation. This keeps the collision response encapsulated inside the can itself.

---

## Screenshots of the Game

> *(Insert screenshots here — suggested captures below)*

| Screenshot | Description |
|---|---|
| `screenshot_menu.png` | Main menu with parallax background and animated clouds |
| `screenshot_character_select.png` | Character selection screen with 4 cards |
| `screenshot_level_select.png` | Level select showing locked and unlocked levels |
| `screenshot_gameplay.png` | Active gameplay with player, guard, can, HUD, and power meter |
| `screenshot_level_cleared.png` | Level cleared overlay with home and next buttons |
| `screenshot_game_over.png` | Game over overlay with home and retry buttons |
| `screenshot_pause.png` | Pause menu overlay during gameplay |
| `screenshot_settings.png` | Settings screen with audio sliders |

---

## Challenges Encountered

**Integrating OOP into an existing codebase**
The game already had a working structure before the OOP requirements were introduced. Adding inheritance without breaking existing behavior required careful planning — the base class had to be designed around what the entities already did, not the other way around.

**Python's lack of true method overloading**
Python does not support multiple method signatures natively. The overloading pattern had to be implemented using default and keyword-only arguments (`*` separator), and the method body uses conditional branching to handle each case. This is less explicit than overloading in Java or C++, so clear comments were added to document the two call signatures.

**Keeping Score consistent across systems**
The `GameManager` already tracked score as a plain integer, and several screens read from it. Introducing the `Score` class required keeping `game.manager.score` (int) in sync with `self.score` (Score object) in `GameplayScreen`. This was handled by calling `self.game.manager.score = int(self.score)` after every scoring operation.

**Collision detection precision**
Using pixel-perfect mask collision (`pygame.mask`) instead of bounding rectangles required the collision mask to be rebuilt every frame for animated sprites, since the visible pixels change with each animation frame. This was already handled in `Guard.update()` and `Slipper.update()` but had to be maintained carefully when refactoring.

**Asset path portability**
All asset paths are resolved through `resource_path()` to ensure the game works regardless of where the project folder is located. This became important when the project was run from different machines and directories during development and testing.

---

## Conclusion

This activity demonstrated how Python's OOP features — method overriding, method overloading, operator overloading, and duck typing — can be applied to a real, working game project rather than isolated examples.

The `GameObject` base class gave the entity system a formal structure, making it clear what every game entity is expected to do. Method overriding allowed `Player`, `Guard`, `Can`, and `Slipper` to each define their own behavior under the same interface. The overloaded `Player.move()` method showed how a single method can serve two different use cases cleanly. The `Score` class made scoring logic more expressive and self-contained through operator overloading. And the `render_all()` duck typing utility showed how objects can be treated uniformly based on capability rather than type.

The result is a codebase that is more organized, easier to extend, and demonstrates each polymorphism concept in a context that is directly tied to the game's actual mechanics.
