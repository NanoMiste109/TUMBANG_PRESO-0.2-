import pygame
import sys
from game import Game
from resource_path import resource_path

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(resource_path("ASSETS/SOUND/moodmode-retro-game-arcade-236133.mp3"))
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1)
game = Game()
clock = pygame.time.Clock()

while True:
    mouse_clicked = False
    mouse_x, mouse_y = pygame.mouse.get_pos()
    scale_x = game.WIDTH / game.SCREEN_WIDTH
    scale_y = game.HEIGHT / game.SCREEN_HEIGHT
    mouse_pos = (mouse_x * scale_x, mouse_y * scale_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.VIDEORESIZE:
            game.SCREEN_WIDTH, game.SCREEN_HEIGHT = event.w, event.h
            game.screen = pygame.display.set_mode((game.SCREEN_WIDTH, game.SCREEN_HEIGHT), pygame.RESIZABLE)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

        if game.manager.game_state == "name_entry":
            game.screens["name_entry"].handle_event(event)
            
    game.update(mouse_pos, mouse_clicked)
    game.draw()
    scaled_surface = pygame.transform.scale(game.surface, (game.SCREEN_WIDTH, game.SCREEN_HEIGHT))
    game.screen.blit(scaled_surface, (0, 0))
    pygame.display.update()
    clock.tick(60)
