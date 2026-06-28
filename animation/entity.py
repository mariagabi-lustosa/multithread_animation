import pygame
import math

from config import screen, font_id, COLOR_HACKER, COLOR_SERF, COLOR_BG, COLOR_TEXT_MAIN


class Entity:
    def __init__(self, id, type, current_x, current_y):
        self.id = id
        self.type = type  # HACKER or SERF
        self.x = current_x
        self.y = current_y
        self.radius = 16
        self.target_x = current_x
        self.target_y = current_y
        self.pulse = 0

    def draw(self):
        self.pulse += 0.1
        pulse_radius = self.radius + int(math.sin(self.pulse) * 3)
        base_color = COLOR_HACKER if self.type == 'HACKER' else COLOR_SERF

        # shine effect
        glow_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*base_color, 60), (pulse_radius, pulse_radius), pulse_radius)
        screen.blit(glow_surface, (int(self.x - pulse_radius), int(self.y - pulse_radius)))

        # body of the entity
        pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, COLOR_BG, (int(self.x), int(self.y)), self.radius - 3)
        pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), self.radius - 6)

        id_surf = font_id.render(f"{'H' if self.type == 'HACKER' else 'S'}{self.id}", True, COLOR_TEXT_MAIN)
        id_rect = id_surf.get_rect(center=(self.x, self.y))
        screen.blit(id_surf, id_rect)

    def update(self):
        # exponential interpolation movement
        self.x += (self.target_x - self.x) * 0.12
        self.y += (self.target_y - self.y) * 0.12
