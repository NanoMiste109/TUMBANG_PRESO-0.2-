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

        # leaderboard icon
        icon_src = pygame.image.load(resource_path("ASSETS/MENU/retrostyle-pixel-art-golden-trophy-260nw-2637425725-Photoroom.png")).convert_alpha()
        icon_size = 52
        self.lb_icon = pygame.transform.scale(icon_src, (icon_size, icon_size))
        self.lb_rect = self.lb_icon.get_rect(bottomright=(790, 590))

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

        if hovered_item != self._last_hovered and hovered_item is not None:
            self.assets.sfx_hover.play()
        self._last_hovered = hovered_item

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
