import pygame


def draw_text_outline(surface, text, font, color, outline_color, pos):

    x, y = pos

    for dx in range(-2,3):
        for dy in range(-2,3):

            if dx != 0 or dy != 0:
                outline = font.render(text, True, outline_color)
                surface.blit(outline, (x+dx,y+dy))

    text_surface = font.render(text, True, color)
    surface.blit(text_surface,(x,y))