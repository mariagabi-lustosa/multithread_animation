import pygame

pygame.init()
pygame.display.set_caption("MC504 - Multithread River Crossing Visualizer")

# dimensions
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 650

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# graphics
COLOR_BG = (18, 24, 38)
COLOR_RIVER_BED = (26, 36, 56)
COLOR_RIVER = (0, 180, 216)
COLOR_HACKER = (57, 255, 20)
COLOR_SERF = (255, 7, 58)
COLOR_BOAT = (197, 137, 64)
COLOR_BOAT_DARK = (141, 91, 35)
COLOR_TEXT_MAIN = (248, 249, 250)
COLOR_TEXT_MUTED = (108, 117, 125)

# fonts
font_title = pygame.font.SysFont("Segoe UI", 32, bold=True)
font_bank = pygame.font.SysFont("Segoe UI", 22, bold=True)
font_status = pygame.font.SysFont("Consolas", 16, bold=True)
font_id = pygame.font.SysFont("Segoe UI", 14, bold=True)
font_log = pygame.font.SysFont("Consolas", 13, bold=False)
