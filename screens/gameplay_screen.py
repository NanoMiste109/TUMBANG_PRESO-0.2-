import pygame
import math
from entities.player import Player
from entities.guard import Guard
from entities.can import Can
from entities.slipper import Slipper, V4_STUN_FRAMES
from entities.score import Score
from entities.character import character_from_index
from entities.duck_typing import render_all
from ui.power_meter import PowerMeter
from resource_path import resource_path
from managers.save_manager import save_score


class GameplayScreen:

    LEVEL_THROWS = {1: 10, 2: 8, 3: 8, 4: 6}

    def __init__(self, game):
        self.game = game
        self.player      = Player(100, 268, self.game.manager.selected_character)
        self.guards      = []
        self.can         = Can(540, 400)
        self.slipper     = None
        self.power_meter = PowerMeter()
        self._esc_held   = False
        self._space_held = False
        self.score       = Score(0, 100)   # Score object — operator overloading
        self.miss_penalty = 10
        self.throws_remaining = 0
        self.state = "playing"
        self.character = character_from_index(self.game.manager.selected_character)
        self.special_armed = False
        self.special_active = False
        self.committed_points = 0
        self._e_held = False
        self._g_held = False          # G key for slipper ability
        self._slipper_ability_used = False  # one use per level
        self._extra_slippers = []     # v3 split extra projectiles
        self.setup_level()

    def setup_level(self):
        lvl = self.game.manager.current_level
        self.slipper = None
        self.power_meter.reset()
        self.can.reset()
        self.state = "playing"
        self.player = Player(100, 268, self.game.manager.selected_character)
        self.character = character_from_index(self.game.manager.selected_character)
        self.special_armed = False
        self.special_active = False
        self.committed_points = 0
        self.throws_remaining = self.LEVEL_THROWS.get(lvl, 10)
        self._g_held = False
        self._slipper_ability_used = False
        self._extra_slippers = []

        if lvl == 1:
            self.score       = Score(0, 100)
            self.miss_penalty = 10
            self.can.clear_patrol()
            self.guards = [Guard(500, 400, [
                (680, 370), (680, 540), (380, 540), (380, 370)
            ], speed=1.8)]

        elif lvl == 2:
            self.score       = Score(0, 100)
            self.miss_penalty = 15
            self.can.clear_patrol()
            self.guards = [
                Guard(500, 400, [
                    (760, 370), (760, 540), (380, 540), (380, 370)
                ], speed=2.2),
                Guard(450, 420, [
                    (730, 400), (730, 510), (410, 510), (410, 400)
                ], speed=2.5),
            ]

        elif lvl == 3:
            self.score       = Score(0, 120)
            self.miss_penalty = 20
            self.can.clear_patrol()
            # 2 guards in front of the can, patrolling vertically one behind the other
            self.guards = [
                Guard(530, 360, [
                    (530, 360), (530, 520)
                ], speed=2.2),
                Guard(560, 440, [
                    (560, 440), (560, 360), (560, 520)
                ], speed=2.4),
            ]

        elif lvl == 4:
            self.score       = Score(0, 100)
            self.miss_penalty = 25
            # Can moves vertically between two points
            self.can.set_patrol(
                waypoints=[(540, 360), (540, 480)],
                speed=1.2,
            )
            # 1 fast guard patrolling vertically in front of the can
            self.guards = [
                Guard(530, 360, [
                    (530, 360), (530, 520)
                ], speed=3.8),
            ]

        # keep manager in sync; health = score
        self.game.manager.score = int(self.score)
        self.character.sync_health(int(self.score))

    def _apply_miss_penalty(self):
        loss = self.character.miss_penalty_amount(
            self.committed_points, self.special_active, self.miss_penalty
        )
        self.score -= loss
        self.game.manager.score = int(self.score)
        self.character.sync_health(int(self.score))
        self.special_active = False
        self.game.assets.sfx_miss.play()

    def _outlined_text(self, font, text, color, surface, pos):
        outline = font.render(text, True, (0, 0, 0))
        for dx in (-1, 1):
            for dy in (-1, 1):
                surface.blit(outline, (pos[0]+dx, pos[1]+dy))
        surface.blit(font.render(text, True, color), pos)

    # Level cleared / failed overlay layout (matches level-cont mockup)
    _LC_BOARD_CENTER = (400, 300)
    _LC_STATUS_Y_RATIO = 0.36   # status text sits in upper-middle of bamboo board
    _LC_BTN_ROW_Y_RATIO = 0.74    # buttons in bottom rail of board
    _LC_BTN_GAP = 14

    def _lc_scaled_mouse(self):
        mx, my = pygame.mouse.get_pos()
        return (
            mx * self.game.WIDTH / self.game.SCREEN_WIDTH,
            my * self.game.HEIGHT / self.game.SCREEN_HEIGHT,
        )

    def _lc_board_rect(self):
        return self.game.assets.lc_board.get_rect(center=self._LC_BOARD_CENTER)

    def _lc_status_rect(self, status_img, board_rect):
        """Place LEVEL CLEARED / FAILED text in the upper half of the board."""
        y = board_rect.top + int(board_rect.height * self._LC_STATUS_Y_RATIO)
        return status_img.get_rect(center=(board_rect.centerx, y))

    def _lc_button_row(self, board_rect, left_btn, right_btn):
        """Home on the left, next/retry on the right — in the board footer."""
        gap = self._LC_BTN_GAP
        row_y = board_rect.top + int(board_rect.height * self._LC_BTN_ROW_Y_RATIO)
        total_w = left_btn.get_width() + gap + right_btn.get_width()
        left_x = board_rect.centerx - total_w // 2
        left_rect = left_btn.get_rect(topleft=(left_x, row_y))
        right_rect = right_btn.get_rect(topleft=(left_x + left_btn.get_width() + gap, row_y))
        return left_rect, right_rect

    def _lc_single_button_rect(self, board_rect, btn):
        row_y = board_rect.top + int(board_rect.height * self._LC_BTN_ROW_Y_RATIO)
        return btn.get_rect(topleft=(board_rect.centerx - btn.get_width() // 2, row_y))

    def _lc_draw_overlay(self, surface, status_img, left_btn, right_btn,
                         left_hov, right_hov, single_btn=False):
        a = self.game.assets
        self._lc_dim_overlay(surface)
        mx, my = self._lc_scaled_mouse()

        board_rect = self._lc_board_rect()
        surface.blit(a.lc_board, board_rect)

        status_rect = self._lc_status_rect(status_img, board_rect)
        surface.blit(status_img, status_rect)

        if single_btn:
            btn_rect = self._lc_single_button_rect(board_rect, left_btn)
            surface.blit(self._lc_btn_img(btn_rect, left_btn, left_hov, mx, my), btn_rect)
            return board_rect, btn_rect, None

        menu_rect, action_rect = self._lc_button_row(board_rect, left_btn, right_btn)
        surface.blit(self._lc_btn_img(menu_rect, left_btn, left_hov, mx, my), menu_rect)
        surface.blit(self._lc_btn_img(action_rect, right_btn, right_hov, mx, my), action_rect)
        return board_rect, menu_rect, action_rect

    def _lc_btn_img(self, rect, normal, hovered, mx, my):
        return hovered if rect.collidepoint(mx, my) else normal

    def _lc_dim_overlay(self, surface):
        ov = pygame.Surface((800, 600), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        surface.blit(ov, (0, 0))

    def update(self, mouse_pos, clicked):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            if not self._esc_held and self.state == "playing":
                self.game.pause.toggle()
            self._esc_held = True
        else:
            self._esc_held = False
        if self.state != "playing":
            self.game.pause.update(mouse_pos, clicked)
            if self.state == "complete" and clicked and not self.game.pause.active:
                self._handle_complete_click(mouse_pos)

            if self.state == "gameover" and clicked and not self.game.pause.active:
                self._handle_gameover_click(mouse_pos)
            return

        self.player.move(keys)
        self.power_meter.update()

        # ── E key: arm/disarm character special ──────────────────────────────
        if keys[pygame.K_e] and not self._e_held:
            if self.power_meter.phase is None and self.slipper is None:
                if not self.special_armed and self.character.uses_remaining > 0:
                    self.special_armed = True
                elif self.special_armed:
                    self.special_armed = False
        self._e_held = keys[pygame.K_e]

        # ── G key: activate slipper ability ──────────────────────────────────
        slipper_idx = self.game.manager.selected_slipper
        slip_idx = slipper_idx  # alias used below in SPACE block
        if keys[pygame.K_g] and not self._g_held:
            if not self._slipper_ability_used and slipper_idx > 0:
                if self.slipper and not self.slipper.landed:
                    # Activate ability on the in-flight slipper (v2/v3/v4)
                    activated = self.slipper.activate_ability(guards=self.guards)
                    if activated:
                        self._slipper_ability_used = True
                        if slipper_idx == 2:
                            # v3 split: spawn 2 extra slippers at spread angles
                            spread = 0.25
                            angle_main = math.atan2(self.slipper.vel_y, self.slipper.vel_x)
                            base_speed = math.hypot(self.slipper.vel_x, self.slipper.vel_y)
                            for delta in (-spread, spread):
                                extra = Slipper(
                                    self.slipper.x, self.slipper.y,
                                    angle_main + delta, base_speed, self.slipper.power,
                                    ground_y=self.slipper.ground_y,
                                    slipper_index=2,
                                )
                                extra.ability_used  = True
                                extra._split_active = True
                                extra._num_frames   = len(extra.frames_split)
                                extra.anim_frame    = 0
                                self._extra_slippers.append(extra)
                elif self.power_meter.phase is None and self.slipper is None:
                    # Arm for next throw (v2 arms before throw)
                    self._slipper_ability_armed = not getattr(self, '_slipper_ability_armed', False)
        self._g_held = keys[pygame.K_g]

        space_down = keys[pygame.K_SPACE]
        if space_down and not self._space_held:
            pm = self.power_meter
            if pm.phase is None and self.slipper is None and self.throws_remaining > 0:
                if self.special_armed:
                    self.special_active = True
                    self.special_armed = False
                    self.character.consume_special_use()
                    # Maria's Tiyaga: grant +1 bonus throw when activated
                    from entities.character import MariaCharacter
                    if isinstance(self.character, MariaCharacter):
                        self.throws_remaining += 1
                pm.start_direction()
            elif pm.phase == "direction":
                pm.angle = pm._current_angle()
                pm.lock_direction()
            elif pm.phase == "power":
                result = pm.lock_power()
                if result:
                    angle, power = result
                    self.committed_points = self.character.compute_hit_points(
                        power, self.special_active
                    )
                    speed = 3 + (power / 100) * 9
                    self.player.throw()
                    self.throws_remaining -= 1
                    self.game.assets.sfx_whoosh.play()
                    self.slipper = Slipper(
                        self.player.x + self.player.frame_w,
                        self.player.y + self.player.frame_h // 2,
                        angle, speed, power,
                        ground_y=max(self.player.y + self.player.frame_h - self.player.FOOT_OFFSET, self.can.y + self.can.rect.height),
                        slipper_index=self.game.manager.selected_slipper,
                    )
                    # Apply v2 rocket ability if armed before throw
                    if slip_idx == 1 and getattr(self, '_slipper_ability_armed', False) and not self._slipper_ability_used:
                        self.slipper.activate_ability()
                        self._slipper_ability_used = True
                        self._slipper_ability_armed = False
        self._space_held = space_down

        if self.slipper:
            self.slipper.update()

            def mask_hit(a, b):
                offset = (b.rect.x - a.rect.x, b.rect.y - a.rect.y)
                return a.mask.overlap(b.mask, offset) is not None

            if mask_hit(self.slipper, self.can) and not self.can.knocked:
                pts = self.committed_points
                was_special = self.special_active
                self.score += pts
                self.game.manager.score = int(self.score)
                self.character.sync_health(int(self.score))
                self.game.assets.sfx_can_hit.play()
                self.can.hit()
                self.slipper = None
                # Track special hits for slipper_v3 achievement
                if was_special:
                    self.game.achievements.on_special_hit()
                self.special_active = False
                # Operator overloading: Score.is_complete() / Score.__ge__
                if self.score.is_complete():
                    self.state = "complete"
                    self.game.assets.sfx_level_cleared.play()
                    self.game.manager.unlock_level(self.game.manager.current_level + 1)
                    self.game.achievements.on_level_cleared(self.game.manager.current_level)
                    if self.game.manager.player_name:
                        save_score(self.game.manager.player_name, int(self.score))
            else:
                hit_guard = False
                stunned_by_pikachu = False
                for g in self.guards:
                    if mask_hit(self.slipper, g):
                        hit_guard = True
                        # v4 Pikachu: stun guard, no miss penalty
                        if self.slipper.is_pikachu and not self._slipper_ability_used:
                            g.stun(V4_STUN_FRAMES)
                            self._slipper_ability_used = True
                            stunned_by_pikachu = True
                        break
                if hit_guard:
                    if not stunned_by_pikachu:
                        self._apply_miss_penalty()
                    self.slipper = None
                elif self.slipper.landed:
                    self._apply_miss_penalty()
                    self.slipper = None
                elif self.slipper.x > 850 or self.slipper.x < -20:
                    self.slipper = None
                    self.special_active = False

        # Update and check extra slippers (v3 split)
        for es in self._extra_slippers[:]:
            es.update()
            if not es.landed:
                def mask_hit(a, b):
                    offset = (b.rect.x - a.rect.x, b.rect.y - a.rect.y)
                    return a.mask.overlap(b.mask, offset) is not None
                if mask_hit(es, self.can) and not self.can.knocked:
                    self.score += self.committed_points
                    self.game.manager.score = int(self.score)
                    self.character.sync_health(int(self.score))
                    self.game.assets.sfx_can_hit.play()
                    self.can.hit()
                    self._extra_slippers.clear()
                    if self.score.is_complete():
                        self.state = "complete"
                        self.game.assets.sfx_level_cleared.play()
                        self.game.manager.unlock_level(self.game.manager.current_level + 1)
                        self.game.achievements.on_level_cleared(self.game.manager.current_level)
                        if self.game.manager.player_name:
                            save_score(self.game.manager.player_name, int(self.score))
                    break
                elif es.landed or es.x > 850 or es.x < -20:
                    self._extra_slippers.remove(es)

        # check if out of throws after all slippers resolve
        if self.slipper is None and not self._extra_slippers and self.throws_remaining <= 0 and self.state == "playing":
            self.state = "gameover"
            self.game.assets.sfx_level_failed.play()
        self.can.update()

        if self.can.knocked and self.can.anim_frame == self.can.KNOCK_FRAMES - 1:
            self.can._hold_timer = getattr(self.can, '_hold_timer', 0) + 1
            if self.can._hold_timer > 40:
                self.can.reset()
                self.can._hold_timer = 0
        else:
            self.can._hold_timer = 0
        for guard in self.guards:
            guard.update(self.player)

    def draw(self, surface):
        lvl = self.game.manager.current_level
        bg = self.game.assets.level_bgs.get(lvl, self.game.assets.game_bg)
        surface.blit(bg, (0, 0))

        # Duck typing: render_all() calls .draw() on each entity regardless of type
        render_all(self.guards, surface)
        render_all([self.can, self.slipper, self.player], surface)
        # Render extra slippers (v3 split)
        for es in self._extra_slippers:
            es.draw(surface)

        px = self.player.x + self.player.frame_w // 2
        py = self.player.y + self.player.frame_h // 2
        self.power_meter.draw(surface, px, py)
        font  = self.game.assets.font
        bfont = self.game.assets.big_font
        # str(Score) uses __str__ → "75 / 100"
        score_str = f"SCORE: {self.score}"
        self._outlined_text(font, score_str, (255, 255, 255), surface, (10, 10))
        if self.special_active:
            self._outlined_text(font, "SPECIAL ACTIVE!", (255, 220, 80), surface, (10, 46))
        elif self.special_armed:
            self._outlined_text(font, "SPECIAL ARMED (E)", (180, 255, 180), surface, (10, 46))
        elif self.character.uses_remaining > 0:
            uses_str = f"SPECIAL (E)  x{self.character.uses_remaining}"
            self._outlined_text(font, uses_str, (140, 200, 140), surface, (10, 46))
        else:
            self._outlined_text(font, "NO SPECIAL LEFT", (120, 120, 120), surface, (10, 46))

        # Slipper ability HUD (G key, v2/v3/v4 only)
        slip_idx = self.game.manager.selected_slipper
        if slip_idx > 0:
            if self._slipper_ability_used:
                self._outlined_text(font, "SLIPPER ABILITY USED", (100, 100, 100), surface, (10, 68))
            elif getattr(self, '_slipper_ability_armed', False):
                self._outlined_text(font, "SLIPPER ARMED (G)", (80, 220, 255), surface, (10, 68))
            else:
                self._outlined_text(font, "SLIPPER ABILITY (G)", (100, 180, 255), surface, (10, 68))
        throws_color = (255, 80, 80) if self.throws_remaining <= 3 else (255, 255, 255)
        throws_str = f"THROWS: {self.throws_remaining}"
        throws_surf = font.render(throws_str, True, throws_color)
        surface.blit(throws_surf, (800 - throws_surf.get_width() - 10, 580))
        a = self.game.assets
        esc_img = a.esc_key
        text_surf = a.pause_hint_font.render("TO PAUSE", True, (255, 255, 255))
        outlined = pygame.Surface((text_surf.get_width()+2, text_surf.get_height()+2), pygame.SRCALPHA)
        outline_s = a.pause_hint_font.render("TO PAUSE", True, (0, 0, 0))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    outlined.blit(outline_s, (dx+1, dy+1))
        outlined.blit(text_surf, (1, 1))
        margin = 8
        total_w = esc_img.get_width() + 6 + outlined.get_width()
        x = 800 - total_w - margin
        y = margin
        surface.blit(esc_img, (x, y))
        surface.blit(outlined, (x + esc_img.get_width() + 6,
                                y + esc_img.get_height()//2 - outlined.get_height()//2))
        if not self.game.pause.active:
            if self.state == "complete":
                self._draw_complete_overlay(surface)
            elif self.state == "gameover":
                self._draw_gameover_overlay(surface)

    def _handle_complete_click(self, mouse_pos):
        a = self.game.assets
        board_rect = self._lc_board_rect()
        next_lvl = self.game.manager.current_level + 1

        if next_lvl <= 4:
            menu_rect, next_rect = self._lc_button_row(
                board_rect, a.lc_btn_menu_normal, a.lc_btn_next_normal
            )
            if menu_rect.collidepoint(mouse_pos):
                self.game.start_fade("menu")
            elif next_rect.collidepoint(mouse_pos):
                self.game.manager.current_level = next_lvl
                self.game.start_fade("gameplay")
        else:
            menu_rect = self._lc_single_button_rect(board_rect, a.lc_btn_menu_normal)
            if menu_rect.collidepoint(mouse_pos):
                self.game.start_fade("menu")

    def _handle_gameover_click(self, mouse_pos):
        a = self.game.assets
        board_rect = self._lc_board_rect()
        menu_rect, retry_rect = self._lc_button_row(
            board_rect, a.lc_btn_menu_normal, a.lc_btn_retry_normal
        )
        if menu_rect.collidepoint(mouse_pos):
            self.game.start_fade("menu")
        elif retry_rect.collidepoint(mouse_pos):
            self.game.start_fade("gameplay")

    def _draw_complete_overlay(self, surface):
        a = self.game.assets
        next_lvl = self.game.manager.current_level + 1
        if next_lvl <= 4:
            self._lc_draw_overlay(
                surface, a.lc_cleared,
                a.lc_btn_menu_normal, a.lc_btn_next_normal,
                a.lc_btn_menu_hovered, a.lc_btn_next_hovered,
            )
        else:
            self._lc_draw_overlay(
                surface, a.lc_cleared,
                a.lc_btn_menu_normal, a.lc_btn_menu_normal,
                a.lc_btn_menu_hovered, a.lc_btn_menu_hovered,
                single_btn=True,
            )

    def _draw_gameover_overlay(self, surface):
        a = self.game.assets
        self._lc_draw_overlay(
            surface, a.lc_failed,
            a.lc_btn_menu_normal, a.lc_btn_retry_normal,
            a.lc_btn_menu_hovered, a.lc_btn_retry_hovered,
        )
