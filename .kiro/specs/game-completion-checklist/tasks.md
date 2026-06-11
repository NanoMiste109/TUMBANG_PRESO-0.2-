# Implementation Plan: game-completion-checklist

## Overview

Seven areas of work to bring the Tumbang Preso pygame game to 100% completion. Tasks are ordered so each step builds on the previous, with integration wiring at the end of each area. All code is Python / pygame targeting the existing project structure.

## Tasks

- [x] 1. Code audit and error resolution
  - [x] 1.1 Audit all screen files for runtime errors and fix them
    - Review `screens/` for missing attribute accesses, incorrect method calls, and unhandled edge cases
    - Fix any `AttributeError`, `KeyError`, or `TypeError` that would surface during normal navigation
    - Ensure `GameplayScreen.__init__` does not call `setup_level()` before `self.game.manager` is fully initialised
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 1.2 Audit entity and manager files for logic and syntax errors
    - Review `entities/`, `managers/` for incorrect operator usage, missing imports, and stale references
    - Verify `Score` operator overloading (`__add__`, `__sub__`, `__ge__`, `__str__`, `is_complete`) works correctly
    - _Requirements: 1.1, 1.5_
  - [x] 1.3 Verify full navigation flow runs without exceptions
    - Trace the path: intro → menu → character select → level select → gameplay → level cleared → menu
    - Fix any crash that occurs along this path
    - _Requirements: 1.6_

- [x] 2. Character spritesheets
  - [x] 2.1 Update `CHARACTER_SHEETS` in `entities/player.py` with agreed placeholder filenames
    - Replace current ad-hoc placeholder paths with the canonical filenames defined in the design:
      - Jose (0): `jose_right.png`, `jose_up.png`, `jose_down.png`, `jose_throw.png`
      - Bong (1): `bong_right.png`, `bong_up.png`, `bong_down.png`, `bong_throw.png`
      - Maria (2): `maria_right.png`, `maria_up.png`, `maria_down.png`, `maria_throw.png`
      - Guard (3): `guard_right.png`, `guard_up.png`, `guard_down.png`, `guard_throw.png`
    - All paths under `ASSETS/PLAYER/`; fall back to Jose's existing files when the named file is absent (wrap `load_sheet` with a try/except that falls back to `CHARACTER_SHEETS[0]`)
    - _Requirements: 2.1, 2.3, 2.4, 2.5_
  - [ ]* 2.2 Write property test for Player character sheet loading (Property 2)
    - **Property 2: Player loads all character sheets without error**
    - For each index in `{0, 1, 2, 3}`, constructing `Player(100, 268, index)` must not raise
    - Use `SDL_VIDEODRIVER=dummy` environment variable and `pygame.display.set_mode((1,1))`
    - **Validates: Requirements 2.2, 2.3**

- [x] 3. Profile reset and GameManager defaults
  - [x] 3.1 Add `DEFAULT_PROFILE` constant and `reset_profile()` to `managers/save_manager.py`
    - Define `DEFAULT_PROFILE` dict with `achievements` (all `False`), `unlocked_levels: [1]`, `unlocked_characters: [0]`
    - Implement `reset_profile()` that calls `save_profile(DEFAULT_PROFILE)` and overwrites `profile.json`
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 3.2 Update `GameManager.__init__` to import and merge `DEFAULT_PROFILE`
    - Import `DEFAULT_PROFILE` from `save_manager`
    - Merge loaded profile with defaults so missing keys are always present (shallow merge + nested achievements merge as shown in design)
    - Add `"LANGUAGE": "EN"` to the default `settings` dict
    - _Requirements: 3.4, 5.9_
  - [x] 3.3 Reset `profile.json` on disk to the default state
    - Call `reset_profile()` once (can be done via a small one-off script or directly in the REPL) to write the canonical default profile to disk
    - Verify the file matches the schema in Requirement 3.3
    - _Requirements: 3.3_
  - [ ]* 3.4 Write property test for `reset_profile` idempotence (Property 3)
    - **Property 3: reset_profile is idempotent**
    - Use Hypothesis `st.fixed_dictionaries` to generate arbitrary profile dicts, write them to a temp file, call `reset_profile()`, assert result equals `DEFAULT_PROFILE`
    - **Validates: Requirements 3.2, 3.3**
  - [ ]* 3.5 Write property test for profile round-trip (Property 4)
    - **Property 4: Profile round-trip preserves unlocked characters**
    - Use `st.frozensets(st.integers(0, 3), min_size=1)` to generate character sets, save via `GameManager.save_profile()`, reload a fresh `GameManager`, assert sets match
    - **Validates: Requirements 4.8, 3.4**

- [x] 4. Achievement system wiring
  - [x] 4.1 Wire `AchievementManager.on_level_cleared()` into `GameplayScreen` level-clear logic
    - In `GameplayScreen.update()`, the call `self.game.achievements.on_level_cleared(...)` already exists — verify it passes `self.game.manager.current_level` (not `current_level + 1`)
    - Confirm `GameManager.unlock_character` and `save_profile` are called transitively
    - _Requirements: 4.2, 4.3_
  - [x] 4.2 Add padlock icon and locked-click guard to `CharacterSelectScreen`
    - The padlock blit already exists; verify it renders for every locked character index
    - In `update()`, when `clicked and self.hovered >= 0` and the character is locked, do NOT call `self._confirm()` and do NOT change `self.selected`
    - _Requirements: 4.5, 4.6_
  - [x] 4.3 Add unlock hint on hover for locked characters in `CharacterSelectScreen`
    - Add `_find_achievement_for_character(char_idx)` helper that searches `self.game.achievements.defs` for the achievement whose `unlocks_character == char_idx`
    - In `draw()`, when a card is hovered and locked, render the achievement's `description` (or `TextProvider.get("charselect.locked_hint", lang)` as fallback) below the card using `self.hint_font`
    - _Requirements: 4.7_
  - [ ]* 4.4 Write property test for achievement unlock idempotence (Property 5)
    - **Property 5: Achievement unlock is idempotent**
    - Use `st.sampled_from(list(defs.keys()))` — calling `unlock(id)` twice must produce the same profile state as calling it once
    - **Validates: Requirements 4.4**
  - [ ]* 4.5 Write property test for level clear → achievement + character unlock (Property 6)
    - **Property 6: Level clear triggers correct achievement and character unlock**
    - Use `st.sampled_from([1, 2, 4])` — after `on_level_cleared(level)` on a fresh profile, assert achievement flag is `True` and mapped character index is in `unlocked_characters`
    - **Validates: Requirements 4.2, 4.3**
  - [ ]* 4.6 Write property test for locked character selection blocked (Property 7)
    - **Property 7: Locked character selection is blocked**
    - Use `st.integers(1, 3)` — simulate a click/confirm on a locked card and assert `selected_character` is unchanged
    - **Validates: Requirements 4.6**

- [x] 5. Checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Language option — TextProvider and render_label
  - [x] 6.1 Replace `utils/text.py` with `TextProvider` class and `render_label` helper
    - Keep the existing `draw_text_outline` function for backward compatibility
    - Add `TextProvider` class with `_STRINGS` dict covering all keys listed in the design (menu, pause, settings, level, charselect)
    - Add `render_label(surface, key, game, rect, font, png_surf=None, color=(255,255,255))` helper that blits PNG for EN and renders font text for TL
    - _Requirements: 5.3, 5.4, 5.5, 5.6, 5.7, 5.10, 5.11, 5.12_
  - [ ]* 6.2 Write property test for TextProvider non-empty strings (Property 8)
    - **Property 8: TextProvider returns a non-empty string for every defined key and language**
    - Use `st.sampled_from(list(TextProvider._STRINGS.keys()))` × `st.sampled_from(["EN", "TL"])` — assert result is a non-empty string
    - **Validates: Requirements 5.3, 5.4, 5.5**
  - [ ]* 6.3 Write property test for TL uses font rendering (Property 9)
    - **Property 9: TextProvider uses font rendering for TL on PNG-backed labels**
    - For each PNG-backed key, call `render_label` with `language="TL"` and assert the returned surface was produced by font rendering (not the png_surf)
    - **Validates: Requirements 5.10, 5.11**
  - [x] 6.4 Add language toggle to `SettingsScreen`
    - In `__init__`, create `self.lang_btn_rect` centered below the last slider bar
    - In `update()`, detect click on `lang_btn_rect` and toggle `settings["LANGUAGE"]` between `"EN"` and `"TL"`
    - In `draw()`, render `"LANGUAGE: EN"` / `"LANGUAGE: TL"` label with a border rect using `settings_font`
    - _Requirements: 5.1, 5.2, 5.8_
  - [x] 6.5 Update `SettingsScreen` and `PauseScreen` slider labels to use `render_label`
    - Replace hard-coded `f"{name}: {val}"` label strings with `TextProvider`-backed keys (`settings.music`, `settings.sound`, `settings.sfx`, `settings.sensitivity`)
    - Use `render_label` so TL renders in ThaleahFat font
    - Also update the language toggle label via `TextProvider.get("settings.language", lang)`
    - _Requirements: 5.6, 5.8_
  - [x] 6.6 Update `CharacterSelectScreen` hint text to use `TextProvider`
    - Replace the hard-coded hint string at the bottom of `draw()` with `TextProvider.get("charselect.hint", lang)`
    - Replace the locked-hover hint with `TextProvider.get("charselect.locked_hint", lang)`
    - _Requirements: 5.6_

- [x] 7. Level 3 and Level 4 rework
  - [x] 7.1 Update `GameplayScreen.setup_level()` for level 3
    - Set `self.score = Score(0, 120)`, `self.throws_remaining = 8`, `self.miss_penalty = 20`
    - Replace guard waypoints with the three non-overlapping paths from the design:
      - Guard 1: wide horizontal top sweep `(760,375)→(760,410)→(390,410)→(390,375)`, speed 2.8
      - Guard 2: vertical right-side patrol `(620,355)→(620,545)→(660,545)→(660,355)`, speed 2.6
      - Guard 3: horizontal bottom sweep `(760,495)→(760,545)→(390,545)→(390,495)`, speed 2.5
    - _Requirements: 6.1, 6.3, 6.5, 6.7, 6.8_
  - [x] 7.2 Update `GameplayScreen.setup_level()` for level 4
    - Set `self.score = Score(0, 150)`, `self.throws_remaining = 6`, `self.miss_penalty = 25`
    - Replace guard waypoints with the three tighter/faster paths from the design:
      - Guard 1: tight horizontal mid `(750,375)→(750,415)→(390,415)→(390,375)`, speed 3.2
      - Guard 2: vertical offset-right patrol `(580,355)→(580,545)→(620,545)→(620,355)`, speed 3.0
      - Guard 3: bottom sweep `(390,490)→(390,545)→(750,545)→(750,490)`, speed 3.1
    - _Requirements: 6.2, 6.4, 6.6, 6.7, 6.8_
  - [x] 7.3 Update `LEVEL_THROWS` class constant to match new per-level values
    - Change `LEVEL_THROWS = {1: 10, 2: 8, 3: 8, 4: 6}` (level 4 drops from 8 to 6)
    - _Requirements: 6.3, 6.4_
  - [ ]* 7.4 Write property test for miss penalty correctness (Property 11)
    - **Property 11: Miss penalty applied correctly for all levels**
    - Use `st.integers(1, 4)` for level — after a miss, assert score decreased by exactly `miss_penalty` for that level (floor at 0)
    - **Validates: Requirements 6.8**

- [x] 8. Audio completion
  - [x] 8.1 Add `_load_sfx_placeholder` helper and named audio slots to `AssetManager`
    - Add `_load_sfx_placeholder(self, path, fallback, name)` method that checks `os.path.exists`, prints a warning if absent, and returns the fallback `Sound`
    - Add `self.bgm_menu_path` and `self.bgm_gameplay_path` string attributes (gameplay path falls back to menu path if file absent, with warning)
    - Add `self.sfx_level_cleared`, `self.sfx_level_failed`, `self.sfx_miss` using `_load_sfx_placeholder` with appropriate fallbacks (`sfx_can_hit` for cleared/failed, `sfx_whoosh` for miss)
    - _Requirements: 7.1, 7.2, 7.13_
  - [x] 8.2 Update SFX slider in `SettingsScreen` and `PauseScreen` to include new SFX sounds
    - In the `SFX` slider handler, also call `.set_volume()` on `sfx_level_cleared`, `sfx_level_failed`, and `sfx_miss`
    - _Requirements: 7.12_
  - [x] 8.3 Wire BGM transitions in `Game.start_fade()`
    - Before the existing fade logic, add BGM transition:
      - If `target_state == "gameplay"`: load `assets.bgm_gameplay_path` and play on loop
      - Elif current state is `"gameplay"` (leaving gameplay): load `assets.bgm_menu_path` and play on loop
    - _Requirements: 7.3, 7.4_
  - [x] 8.4 Wire SFX calls in `GameplayScreen` for all in-game events
    - Throw: `self.game.assets.sfx_whoosh.play()` — already present; verify it fires on every throw
    - Hit (can knocked): add `self.game.assets.sfx_can_hit.play()` — already present; verify
    - Miss (guard hit or landed): add `self.game.assets.sfx_miss.play()` in `_apply_miss_penalty()`
    - Level cleared: add `self.game.assets.sfx_level_cleared.play()` when `self.state = "complete"` is set
    - Level failed: add `self.game.assets.sfx_level_failed.play()` when `self.state = "gameover"` is set
    - _Requirements: 7.5, 7.6, 7.7, 7.8, 7.9_
  - [ ]* 8.5 Write property test for volume slider accuracy (Property 10)
    - **Property 10: Volume slider sets correct mixer volume**
    - Use `st.integers(0, 100)` — set MUSIC slider to `v`, assert `pygame.mixer.music.get_volume()` is within 0.01 of `v / 100.0`; set SFX slider to `v`, assert all SFX sounds report volume within 0.01
    - **Validates: Requirements 7.10, 7.12**

- [x] 9. Final checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests require `hypothesis` and `pytest`; run with `SDL_VIDEODRIVER=dummy` for headless pygame
- Placeholder audio files (`BGM_gameplay.mp3`, `sfx_level_cleared.mp3`, `sfx_level_failed.mp3`, `sfx_miss.mp3`) should be placed in `ASSETS/SOUND/` when real assets are ready — no code changes needed
- Placeholder character spritesheets (`jose_right.png` etc.) should be placed in `ASSETS/PLAYER/` — no code changes needed
