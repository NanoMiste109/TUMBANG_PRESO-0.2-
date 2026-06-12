# TUMBANG PRESO — Game Content Overview

A reference document listing everything currently implemented in the game. Use this to verify nothing is missing before the presentation.

---

## Screens

| Screen | Access | Status |
|---|---|---|
| Intro | Auto on launch | ✅ |
| Name Entry | First time playing | ✅ |
| Main Menu | After intro / after game | ✅ |
| Character Select | PLAY from menu | ✅ |
| Level Select | After character confirmed | ✅ |
| Gameplay | Level selected | ✅ |
| Pause (overlay) | ESC during gameplay | ✅ |
| Level Cleared (overlay) | Score target reached | ✅ |
| Level Failed (overlay) | Throws exhausted | ✅ |
| Settings | Menu or Pause | ✅ |
| How to Play | Menu or Pause | ✅ |
| Credits | Menu | ✅ |
| Leaderboard | Trophy icon on menu | ✅ |
| Achievements | Green trophy icon on menu | ✅ |
| Game Modes | Menu (shows "Coming Soon" popup) | ✅ |

---

## Characters

| # | Name | Unlock | Special Skill | Status |
|---|---|---|---|---|
| 0 | Jose | Default | Steady Aim — boosts throw power (3 uses/level) | ✅ |
| 1 | Bong | Clear Level 1 | Doble Hampas — doubles hit points (3 uses/level) | ✅ |
| 2 | Maria | Clear Level 2 | Tiyaga — +1 bonus throw, double miss penalty (3 uses/level) | ✅ |
| 3 | Guard | Clear Level 4 | Bantay Mode — placeholder (3 uses/level) | ✅ |

---

## Slippers

| # | Name | Unlock | Behaviour |
|---|---|---|---|
| 0 | Default | Always unlocked | Standard slipper sprite |
| 1 | Street Slipper | Clear Level 2 | Cosmetic only |
| 2 | Pro Slipper | Hit can with special 3× (persistent) | Cosmetic only |
| 3 | Champion Slipper | Clear Level 4 | Cosmetic only |

---

## Achievements

| ID | Name | Condition | Reward |
|---|---|---|---|
| clear_level_1 | Barangay Rookie | Clear Level 1 | Unlocks Bong |
| clear_level_2 | Street Legend | Clear Level 2 | Unlocks Maria + Street Slipper |
| clear_level_4 | Tumbang Preso Master | Clear Level 4 | Unlocks Guard + Champion Slipper |
| slipper_v3 | Special Master | Hit can with special 3× (any sessions) | Unlocks Pro Slipper |

Progress for Special Master is shown in the Achievements screen.

---

## Levels

| Level | Background | Guards | Throws | Score Target | Moving Can |
|---|---|---|---|---|---|
| 1 | Kalsada (Street) | 1 (rect patrol) | 10 | 100 | No |
| 2 | Park | 2 (rect patrols) | 8 | 100 | No |
| 3 | Market | 2 (horizontal sweeps) | 8 | 120 | No |
| 4 | Field | 3 (top/bottom sweep + vertical) | 6 | 100 | Yes (vertical) |

---

## Audio

| Sound | File | Controlled By |
|---|---|---|
| Menu BGM | moodmode-retro-game-arcade-236133.mp3 | MUSIC slider |
| Level 1 BGM | sandbox-serenade-sky-toes-... .mp3 | MUSIC slider |
| Level 2 BGM | 2019-12-09_-_Retro_Forest_... .mp3 | MUSIC slider |
| Level 3 BGM | 2020-06-18_-_8_Bit_Retro_Funk_... .mp3 | MUSIC slider |
| Level 4 BGM | 2020-03-22_-_8_Bit_Surf_... .mp3 | MUSIC slider |
| Throw SFX | floraphonic-fireball-whoosh-... .mp3 | SFX slider |
| Can hit SFX | audiomass-output.mp3 | SFX slider |
| Miss SFX | sfx_miss.mp3 (placeholder: whoosh) | SFX slider |
| Level Cleared SFX | sfx_level_cleared.mp3 (placeholder: can hit) | SFX slider |
| Level Failed SFX | sfx_level_failed.mp3 (placeholder: can hit) | SFX slider |
| Button Click | audley_fergine-ui-button-click-... .mp3 | SOUND slider |
| Button Hover | lesiakower-minimalist-button-hover-... .mp3 | SOUND slider |

**Missing real audio** (currently using placeholders): `sfx_miss.mp3`, `sfx_level_cleared.mp3`, `sfx_level_failed.mp3`

---

## Settings

| Option | Function |
|---|---|
| MUSIC slider | Controls BGM volume |
| SOUND slider | Controls UI click/hover volume |
| SFX slider | Controls all in-game sound effects |
| Language toggle | Switches UI text between EN and TL (Tagalog) |

---

## Language Support

- English (EN) — default
- Tagalog (TL) — covers: menu buttons, pause buttons, settings labels, level cleared/failed, character select hints
- PNG-based labels (English): rendered as-is in EN mode, replaced with ThaleahFat font in TL mode

---

## Save Data (`profile.json`)

```json
{
  "achievements": { "clear_level_1": bool, "clear_level_2": bool, "clear_level_4": bool, "slipper_v2": bool, "slipper_v3": bool, "slipper_v4": bool },
  "unlocked_levels": [1, ...],
  "unlocked_characters": [0, ...],
  "unlocked_slippers": [0, ...],
  "special_hits": int
}
```

Leaderboard is stored separately in `scores.json` — cumulative score per named player, top 10 kept.

---

## Known Placeholders / Post-Presentation TODO

- [ ] Guard (character 3) special skill `Bantay Mode` has no effect yet
- [ ] `sfx_miss.mp3`, `sfx_level_cleared.mp3`, `sfx_level_failed.mp3` — need real audio files
- [ ] Slipper cosmetics only — no passive perks implemented yet
- [ ] Game Modes screen — not implemented, shows "Coming Soon"
