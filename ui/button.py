import pygame
class Button:
    def __init__(self, x, y, text, font):
        self.text = text
        self.font = font
        self.image = font.render(text, True, (255,255,255))
        self.rect = self.image.get_rect(center=(x,y))

    def draw(self, surface, mouse_pos, clicked):
        hovered = self.rect.collidepoint(mouse_pos)
        color = (255,255,0) if hovered else (255,255,255)
        text = self.font.render(self.text, True, color)
        surface.blit(text, self.rect)
        
        if hovered and clicked:
            return True
        return False
