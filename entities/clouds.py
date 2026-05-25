import pygame
import random
import math


class Clouds:

    def __init__(self, width, height, cloud_images):
        self.WIDTH = width
        self.HEIGHT = height
        self.clouds = []
        chosen = random.sample(cloud_images, min(3, len(cloud_images)))

        for i, img in enumerate(chosen):
            scale = random.uniform(0.35, 0.55)
            img_scaled = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            cloud = {
                "image": img_scaled,
                "x": i * (self.WIDTH // 3) + random.randint(0, 80),
                "base_y": random.randint(0, self.HEIGHT // 3),
                "y": 0,
                "speed": random.uniform(0.2, 0.8)
            }
            cloud["y"] = cloud["base_y"]
            self.clouds.append(cloud)

    def update(self, time):
        for cloud in self.clouds:
            cloud["x"] -= cloud["speed"]
            cloud["y"] = cloud["base_y"] + math.sin(time + cloud["x"] * 0.01) * 5
            if cloud["x"] < -cloud["image"].get_width():
                cloud["x"] = self.WIDTH
                cloud["base_y"] = random.randint(0, self.HEIGHT // 3)
                cloud["y"] = cloud["base_y"]
                
    def draw(self, surface):
        for cloud in self.clouds:
            surface.blit(cloud["image"], (cloud["x"], cloud["y"]))
