# Requirements Document

## Introduction

This document covers the remaining work to bring the Tumbang Preso pygame game to 100% completion. The game is a Filipino street game where players throw slippers/cans at a target while avoiding guards. It features 4 levels, multiple playable characters, a save/achievement system, and various screens (menu, gameplay, level select, character select, settings, pause, credits, how to play). The remaining work spans code quality, missing assets, save data reset, an achievement-driven character unlock system, a bilingual language option, level reworks for levels 3 and 4, and completing the audio suite.

---

## Glossary

- **Game**: The top-level pygame application class (`game.py`) that owns all screens and managers.
- **GameManager**: The `managers/game_manager.py` class that holds global state (current level, selected character, unlocked levels/characters, settings, player name).
- **AchievementManager**: The `managers/achievement_manager.py` class that tracks and unlocks achievements, which in turn unlock characters.
- **SaveManager**: The `managers/save_manager.py` module that reads/writes `profile.json` and `scores.json`.
- **AssetManager**: The `managers/asset_manager.py` class that loads and caches all images, fonts, and sounds.
- **Player**: The `entities/player.py` entity controlled by the user.
- **Guard**: The `entities/guard.py` entity that patrols and blocks throws.
- **Character**: The abstract base class in `entities/character.py`; concrete subclasses are `JoseCharacter`, `BongCharacter`, `MariaCharacter`, `GuardCharacter`.
- **CharacterSelectScreen**: The `screens/character_select_screen.py` screen where the player picks a character.
- **SettingsScreen**: The `screens/settings_screen.py` screen with audio sliders.
- **GameplayScreen**: The `screens/gameplay_screen.py` screen that runs the active level.
- **Profile**: The `profile.json` file storing unlocked levels, unlocked characters, and achievement flags.
- **Spritesheet**: A single image file containing multiple animation frames laid out in a horizontal strip.
- **Language**: Either `"EN"` (English) or `"TL"` (Tagalog/Filipino), stored in `GameManager.settings`.
- **TextProvider**: A utility module/class that returns UI strings in the active language.
- **SFX**: Short sound effects triggered by in-game events (throw, hit, miss).
- **BGM**: Background music that loops during gameplay or menu screens.

---

## Requirements

### Requirement 1: Code Audit and Error Resolution

**User Story:** As a developer, I want all logic, syntax, and runtime errors identified and fixed, so that the game runs without crashes or unexpected behaviour.

#### Acceptance Criteria

1. THE Game SHALL load and reach the main menu without raising any Python exceptions.
2. WHEN any screen transition is triggered, THE Game SHALL complete the transition without raising a runtime error.
3. WHEN the player completes or fails a level, THE GameplayScreen SHALL display the correct overlay and allow navigation without crashing.
4. IF a required asset file is missing at startup, THEN THE AssetManager SHALL raise a descriptive `FileNotFoundError` that names the missing file path.
5. THE Game SHALL produce no `DeprecationWarning` or `SyntaxWarning` messages when launched with Python 3.12.
6. WHEN the player navigates through every screen in sequence (menu → character select → level select → gameplay → level cleared → menu), THE Game SHALL complete the full flow without error.

---

### Requirement 2: Character Spritesheets

**User Story:** As a player, I want each character to display their own unique sprite animations, so that the characters feel visually distinct.

#### Acceptance Criteria

1. THE AssetManager SHALL define a spritesheet path entry for each of the four characters (Jose, Bong, Maria, Guard) for each animation state: `right`, `up`, `down`, and `throw`.
2. WHEN a character index is selected, THE Player SHALL load the spritesheet paths corresponding to that character index from `CHARACTER_SHEETS`.
3. WHERE a character's real spritesheet asset is not yet supplied, THE Player SHALL fall back to the Jose placeholder spritesheet without raising an error.
4. WHEN the real spritesheet assets are placed in `ASSETS/PLAYER/` with the agreed filenames, THE Player SHALL load and display them automatically without code changes.
5. THE `CHARACTER_SHEETS` dictionary in `player.py` SHALL contain placeholder path entries for all four character indices (0–3) so that asset substitution requires only dropping in the file.

---

### Requirement 3: Profile Reset

**User Story:** As a developer, I want the saved profile data reset to a clean initial state, so that testers and players start from a fresh progression.

#### Acceptance Criteria

1. THE SaveManager SHALL provide a `reset_profile()` function that writes a default `profile.json` containing: `unlocked_levels: [1]`, `unlocked_characters: [0]`, and `achievements` with all flags set to `false`.
2. WHEN `reset_profile()` is called, THE SaveManager SHALL overwrite the existing `profile.json` with the default values.
3. THE default `profile.json` on disk SHALL match the schema: `{ "achievements": { "clear_level_1": false, "clear_level_2": false, "clear_level_4": false }, "unlocked_levels": [1], "unlocked_characters": [0] }`.
4. WHEN the Game starts and `profile.json` is absent or malformed, THE GameManager SHALL initialise with the same default values as `reset_profile()` produces.

---

### Requirement 4: Achievement System

**User Story:** As a player, I want to unlock new characters by completing specific in-game achievements, so that progression feels rewarding.

#### Acceptance Criteria

1. THE AchievementManager SHALL define at least the following achievements and their character unlock mappings:
   - `clear_level_1` → unlocks character index 1 (Bong)
   - `clear_level_2` → unlocks character index 2 (Maria)
   - `clear_level_4` → unlocks character index 3 (Guard)
2. WHEN a level is cleared, THE AchievementManager SHALL call `on_level_cleared(level)` which checks and unlocks the corresponding achievement.
3. WHEN an achievement is unlocked for the first time, THE AchievementManager SHALL call `GameManager.unlock_character(index)` and persist the profile via `SaveManager`.
4. WHEN an achievement has already been unlocked, THE AchievementManager SHALL not unlock it again or overwrite the profile unnecessarily.
5. THE CharacterSelectScreen SHALL display a padlock icon over any character whose index is not present in `GameManager.unlocked_characters`.
6. WHEN a locked character card is clicked or confirmed, THE CharacterSelectScreen SHALL not allow selection and SHALL provide visual feedback (padlock remains visible).
7. THE CharacterSelectScreen SHALL display an unlock hint (e.g. the achievement description) when a locked character card is hovered.
8. WHEN the profile is loaded at startup, THE GameManager SHALL restore previously unlocked characters from `profile.json` so that unlocks persist across sessions.

---

### Requirement 5: Language Option

**User Story:** As a player, I want to switch the game's UI language between English and Tagalog, so that Filipino players can enjoy the game in their native language.

#### Acceptance Criteria

1. THE SettingsScreen SHALL display a language toggle control that switches between `"EN"` (English) and `"TL"` (Tagalog).
2. WHEN the language toggle is activated, THE GameManager SHALL update `settings["LANGUAGE"]` to the new value.
3. THE Game SHALL provide a `TextProvider` that returns the correct string for a given key based on `GameManager.settings["LANGUAGE"]`.
4. WHEN `settings["LANGUAGE"]` is `"TL"`, THE TextProvider SHALL return Tagalog strings for all defined UI keys.
5. WHEN `settings["LANGUAGE"]` is `"EN"`, THE TextProvider SHALL return English strings for all defined UI keys.
6. THE TextProvider SHALL cover at minimum the following UI contexts: menu button labels, settings screen labels, pause screen labels, level cleared/failed messages, and character select hints.
7. IF a translation key is missing for the active language, THEN THE TextProvider SHALL fall back to the English string for that key.
8. WHEN the language is changed in settings, THE SettingsScreen SHALL re-render labels in the new language immediately without requiring a restart.
9. THE `settings["LANGUAGE"]` value SHALL default to `"EN"` when no saved preference exists.
10. WHERE a UI label is currently rendered as a PNG image asset, THE TextProvider SHALL render that label using the `ThaleahFat.ttf` font when the active language is `"TL"`, so that Tagalog text displays correctly without requiring separate PNG assets per language.
11. WHEN the active language is `"EN"`, THE Game SHALL continue to display the original PNG image assets for labels that have them, preserving the existing visual style.
12. THE transition between PNG-rendered and font-rendered labels SHALL not cause layout shifts or overlap with other UI elements.

---

### Requirement 6: Level 3 and Level 4 Rework

**User Story:** As a player, I want levels 3 and 4 to be well-designed and fun, so that the difficulty curve feels fair and engaging.

#### Acceptance Criteria

1. WHEN level 3 is loaded, THE GameplayScreen SHALL configure guard patrol paths that cover the horizontal and vertical axes around the can without overlapping each other.
2. WHEN level 4 is loaded, THE GameplayScreen SHALL configure guard patrol paths that are distinct from level 3 and provide a harder challenge.
3. THE `setup_level()` method SHALL set `throws_remaining` for level 3 to a value that makes the level completable but challenging (designer-specified, default 8).
4. THE `setup_level()` method SHALL set `throws_remaining` for level 4 to a value that makes the level completable but challenging (designer-specified, default 6).
5. WHEN level 3 is loaded, THE GameplayScreen SHALL set `score.target` to a value that reflects increased difficulty over level 2 (designer-specified, default 120).
6. WHEN level 4 is loaded, THE GameplayScreen SHALL set `score.target` to a value that reflects the highest difficulty (designer-specified, default 150).
7. WHEN level 3 or 4 is active, THE GameplayScreen SHALL use the correct level background image (`LEVEL DESIGN 3 - MARKET.png` and `LEVEL DESIGN 4 - FIELD.png` respectively).
8. WHEN a guard in level 3 or 4 is hit by a slipper, THE GameplayScreen SHALL apply the miss penalty defined for that level.

---

### Requirement 7: Audio Completion

**User Story:** As a player, I want the game to have complete background music, sound effects, and SFX for all screens and events, so that the audio experience feels polished.

#### Acceptance Criteria

1. THE AssetManager SHALL define named slots for all required audio assets: menu BGM, gameplay BGM, level-cleared SFX, level-failed SFX, throw SFX, hit SFX, miss SFX, button click SFX, and button hover SFX.
2. WHERE a real audio asset is not yet supplied, THE AssetManager SHALL load a placeholder silent audio file or reuse an existing sound without raising an error.
3. WHEN the game transitions to the gameplay screen, THE Game SHALL play the gameplay BGM on loop.
4. WHEN the game transitions away from the gameplay screen, THE Game SHALL stop the gameplay BGM and resume the menu BGM.
5. WHEN a level is cleared, THE GameplayScreen SHALL play the level-cleared SFX.
6. WHEN a level is failed (throws exhausted), THE GameplayScreen SHALL play the level-failed SFX.
7. WHEN the player throws a projectile, THE GameplayScreen SHALL play the throw SFX.
8. WHEN a projectile hits the can, THE GameplayScreen SHALL play the hit SFX.
9. WHEN a projectile misses (hits a guard or lands), THE GameplayScreen SHALL play the miss SFX.
10. THE SettingsScreen MUSIC slider SHALL control the volume of all BGM channels.
11. THE SettingsScreen SOUND slider SHALL control the volume of UI sounds (click, hover).
12. THE SettingsScreen SFX slider SHALL control the volume of all in-game SFX (throw, hit, miss, level cleared, level failed).
13. WHERE placeholder audio files are used, THE AssetManager SHALL log a warning to stdout naming the placeholder so the developer knows which files still need real assets.
