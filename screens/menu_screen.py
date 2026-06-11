import pygame
from resource_path import resource_path


class MenuScreen:

    def __init__(self, game):
        self.game = game
        self.assets = game.assets
        self.menu_items = [
            "play",
            "gamemodes",
            "howtoplay",
            "settings",
            "credits",
            "exit"
        ]

        self.board_rect = self.assets.board.get_rect(center=(400, 370))
        self.spacing = 45
        self._last_hovered = None
        self._coming_soon_timer = 0  # frames remaining to show popup

        # leaderboard icon
        icon_src = pygame.image.load(resource_path("ASSETS/MENU/retrostyle-pixel-art-golden-trophy-260nw-2637425725-Photoroom.png")).convert_alpha()
        icon_size = 52
        self.lb_icon = pygame.transform.scale(icon_src, (icon_size, icon_size))
        self.lb_rect = self.lb_icon.get_rect(bottomright=(790, 590))

        # achievements icon — reuse trophy but tinted, placed beside the leaderboard icon
        self.ach_icon = pygame.transform.scale(icon_src, (icon_size, icon_size))
        # tint green to distinguish from leaderboard
        tint = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        tint.fill((80, 220, 80, 100))
        self.ach_icon.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.ach_rect = self.ach_icon.get_rect(bottomright=(790 - icon_size - 8, 590))
        self._popup_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 22)
        self._label_font = pygame.font.Font(resource_path("ASSETS/ThaleahFat/ThaleahFat.ttf"), 13)

    def update(self, mouse_pos, clicked):
        mx, my = mouse_pos
        hovered_item = None
        for i, item in enumerate(self.menu_items):
            img = self.assets.text_normal[item]
            rect = img.get_rect(center=(
                self.board_rect.centerx,
                self.board_rect.top + 60 + i * self.spacing
            ))

            if rect.collidepoint(mx, my):
                hovered_item = item
                if clicked:
                    self.assets.sfx_click.play()
                    if item == "play":
                        if not self.game.manager.player_name:
                            self.game.screens["name_entry"].reset()
                            self.game.manager.change_state("name_entry")
                        else:
                            self.game.manager.change_state("character_select")
                    elif item == "gamemodes":
                        self._coming_soon_timer = 180  # show for 3 seconds
                    elif item == "howtoplay":
                        self.game.manager.previous_state = "menu"
                        self.game.manager.change_state("how_to_play")
                    elif item == "settings":
                        self.game.manager.previous_state = "menu"
                        self.game.manager.change_state("settings")
                    elif item == "credits":
                        self.game.manager.change_state("credits")
                    elif item == "exit":
                        pygame.quit()
                        exit()

        # leaderboard icon click
        if clicked and self.lb_rect.collidepoint(mx, my):
            self.assets.sfx_click.play()
            self.game.manager.change_state("leaderboard")

        # achievements icon click
        if clicked and self.ach_rect.collidepoint(mx, my):
            self.assets.sfx_click.play()
            self.game.manager.change_state("achievements")

        if hovered_item != self._last_hovered and hovered_item is not None:
            self.assets.sfx_hover.play()
        self._last_hovered = hovered_item
        if self._coming_soon_timer > 0:
            self._coming_soon_timer -= 1

    def draw(self, surface):
        title_rect = self.assets.title.get_rect(center=(400, 100))
        surface.blit(self.assets.title, title_rect)
        surface.blit(self.assets.board, self.board_rect)
        mx, my = pygame.mouse.get_pos()
        scale_x = self.game.WIDTH / self.game.SCREEN_WIDTH
        scale_y = self.game.HEIGHT / self.game.SCREEN_HEIGHT
        mx *= scale_x
        my *= scale_y

        for i, item in enumerate(self.menu_items):
            center = (
                self.board_rect.centerx,
                self.board_rect.top + 60 + i * self.spacing
            )
            normal_img = self.assets.text_normal[item]
            hover_rect = normal_img.get_rect(center=center)
            hovered = hover_rect.collidepoint(mx, my)

            img = self.assets.text_hovered[item] if hovered else normal_img
            surface.blit(img, img.get_rect(center=center))

        # leaderboard icon — slight glow on hover
        lb_hovered = self.lb_rect.collidepoint(mx, my)
        icon = self.lb_icon
        if lb_hovered:
            icon = pygame.transform.scale(self.lb_icon, (58, 58))
        surface.blit(icon, icon.get_rect(bottomright=(790, 590)))

        # achievements icon
        ach_hovered = self.ach_rect.collidepoint(mx, my)
        ach_draw = pygame.transform.scale(self.ach_icon, (58, 58)) if ach_hovered else self.ach_icon
        surface.blit(ach_draw, ach_draw.get_rect(bottomright=(790 - 52 - 8, 590)))
        # labels
        lb_lbl  = self._label_font.render("SCORES", True, (220, 220, 100))
        ach_lbl = self._label_font.render("AWARDS", True, (100, 220, 100))
        surface.blit(lb_lbl,  lb_lbl.get_rect(centerx=self.lb_rect.centerx,  top=self.lb_rect.top - 16))
        surface.blit(ach_lbl, ach_lbl.get_rect(centerx=self.ach_rect.centerx, top=self.ach_rect.top - 16))

        # "Coming Soon" popup for gamemodes
        if self._coming_soon_timer > 0:
            msg = self._popup_font.render("COMING SOON!", True, (255, 220, 80))
            outline = self._popup_font.render("COMING SOON!", True, (0, 0, 0))
            px = self.board_rect.centerx - msg.get_width() // 2
            py = self.board_rect.top + 60 + 1 * self.spacing - msg.get_height() - 6
            for dx in (-1, 1):
                for dy in (-1, 1):
                    surface.blit(outline, (px + dx, py + dy))
            surface.blit(msg, (px, py))
