import pygame
import time
import queue

from config import (
    screen, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_RIVER_BED, COLOR_RIVER,
    COLOR_HACKER, COLOR_SERF, COLOR_BOAT, COLOR_BOAT_DARK,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    font_title, font_bank, font_status, font_log
)
from entity import Entity

# game state
hacker_queue_list = []
serf_queue_list = []
boat_list = []
boat_current_x = 120
boat_status_text = "DOCKING - WAITING FOR PASSENGERS"
boat_is_rowing = False
animation_speed = 2
input_command_queue = queue.Queue()
wave_offset = 0

sys_state = {
    "mutex": "UNLOCKED",
    "barrier": "CLOSED"
}

event_logs = []
MAX_LOG_LINES = 6

finished = False
total_h = 0
total_s = 0
total_trips = 0


def add_log(message, color=COLOR_TEXT_MAIN):
    curr_time = time.strftime("%H:%M:%S")
    event_logs.append((f"{curr_time} {message}", color))
    if len(event_logs) > MAX_LOG_LINES:
        event_logs.pop(0)


def draw_environment():
    screen.fill(COLOR_BG)
    global wave_offset
    wave_offset += 0.5

    # Draw the river
    river_x, river_width = 350, 400
    pygame.draw.rect(screen, COLOR_RIVER_BED, (river_x, 0, river_width, SCREEN_HEIGHT))
    pygame.draw.rect(screen, COLOR_RIVER, (river_x + 10, 0, river_width - 20, SCREEN_HEIGHT))

    # animate the water - "waves"
    for y in range(0, SCREEN_HEIGHT, 40):
        y_pos = (y + int(wave_offset)) % SCREEN_HEIGHT
        pygame.draw.line(screen, (255, 255, 255, 40), (river_x + 50, y_pos), (river_x + 80, y_pos + 10), 2)
        pygame.draw.line(screen, (255, 255, 255, 40), (river_x + 200, y_pos - 15), (river_x + 240, y_pos - 5), 2)
        pygame.draw.line(screen, (255, 255, 255, 40), (river_x + 320, y_pos + 10), (river_x + 350, y_pos + 20), 2)

    # draws the piers
    pygame.draw.rect(screen, (45, 55, 72), (250, (SCREEN_HEIGHT // 2) - 60, 100, 120), border_radius=5)  # left pier
    pygame.draw.rect(screen, (45, 55, 72), (750, (SCREEN_HEIGHT // 2) - 60, 100, 120), border_radius=5)  # right pier

    # header and labels
    title_surf = font_title.render("RIVER CROSSING VISUALIZER", True, COLOR_TEXT_MAIN)
    screen.blit(title_surf, (50, 30))

    sub_surf = font_status.render("Operating Systems Project - Unicamp", True, COLOR_TEXT_MUTED)
    screen.blit(sub_surf, (50, 75))

    screen.blit(font_bank.render("LEFT BANK", True, COLOR_TEXT_MAIN), (50, 130))
    screen.blit(font_bank.render("RIGHT BANK", True, COLOR_TEXT_MAIN), (SCREEN_WIDTH - 200, 130))


def draw_system():
    width = 2
    height = 110
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, (10, 15, 25, 210), (0, 0, width, height), border_radius=8)
    pygame.draw.rect(surface, (60, 70, 90, 255), (0, 0, width, height), width=2, border_radius=8)

    begin_x, begin_y = SCREEN_WIDTH - 300, 20
    screen.blit(surface, (begin_x, begin_y))
    screen.blit(font_status.render("Operational System State", True, (255, 215, 0)), (begin_x + 15, begin_y + 15))

    mutex_color = COLOR_SERF if sys_state["mutex"] == "LOCKED" else COLOR_HACKER
    screen.blit(font_status.render(f"Mutex:   {sys_state['mutex']}", True, mutex_color), (begin_x + 15, begin_y + 45))

    barrier_color = COLOR_SERF if sys_state["barrier"] == "CLOSED" else COLOR_HACKER
    screen.blit(font_status.render(f"Barrier: {sys_state['barrier']}", True, barrier_color), (begin_x + 15, begin_y + 70))


def draw_logs():
    width = 450
    height = 150
    begin_x = 50
    begin_y = SCREEN_HEIGHT - height - 10

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, (10, 15, 25, 220), (0, 0, width, height), border_radius=6)
    pygame.draw.rect(surface, (60, 70, 90, 255), (0, 0, width, height), width=1, border_radius=6)
    screen.blit(surface, (begin_x, begin_y))

    screen.blit(font_status.render("OS Event Log", True, COLOR_TEXT_MUTED), (begin_x + 10, begin_y + 8))
    pygame.draw.line(screen, (60, 70, 90), (begin_x + 10, begin_y + 28), (begin_x + width - 10, begin_y + 28))

    for i, (msg, color) in enumerate(event_logs):
        surf = font_log.render(msg, True, color)
        screen.blit(surf, (begin_x + 10, begin_y + 35 + (i * 17)))


def draw_boat_and_passengers():
    boat_width = 190
    boat_height = 70
    boat_y = (SCREEN_HEIGHT // 2) - (boat_height // 2)

    # draws the boat shape
    points = [
        (boat_current_x, boat_y + 10),
        (boat_current_x + boat_width - 30, boat_y),
        (boat_current_x + boat_width, boat_y + boat_height // 2),  # bow
        (boat_current_x + boat_width - 30, boat_y + boat_height),
        (boat_current_x, boat_y + boat_height - 10)
    ]
    pygame.draw.polygon(screen, COLOR_BOAT_DARK, [(p[0], p[1] + 5) for p in points])  # shadow
    pygame.draw.polygon(screen, COLOR_BOAT, points)

    # draws the boat seats
    seat_positions = [
        (boat_current_x + 25,  boat_y + boat_height // 2),
        (boat_current_x + 60,  boat_y + boat_height // 2),
        (boat_current_x + 95,  boat_y + boat_height // 2),
        (boat_current_x + 130, boat_y + boat_height // 2)
    ]

    for i in range(4):
        bx, by = seat_positions[i]
        pygame.draw.rect(screen, COLOR_BOAT_DARK, (bx - 12, boat_y + 12, 24, boat_height - 24), border_radius=3)

    # boat status label floating above
    status_surf = font_status.render(boat_status_text, True, (255, 215, 0) if "CRUISING" in boat_status_text else COLOR_TEXT_MAIN)
    status_rect = status_surf.get_rect(center=(boat_current_x + boat_width // 2, boat_y - 25))
    screen.blit(status_surf, status_rect)

    # updates and draws passengers in their correct seats
    for i, entity in enumerate(boat_list):
        if i < 4:
            seat_x, seat_y = seat_positions[i]

            # while docked and boarding, entity floats smoothly to its seat
            if not boat_is_rowing:
                entity.target_x = seat_x
                entity.target_y = seat_y
                entity.update()
            else:
                # while rowing, snap to seat to avoid lag or floating outside the boat
                entity.x = seat_x
                entity.target_x = seat_x
                entity.y = seat_y
                entity.target_y = seat_y

            entity.draw()


def draw_final():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 210))
    screen.blit(overlay, (0, 0))
    # central box
    box_width, box_height = 400, 260
    start_x = (SCREEN_WIDTH - box_width) // 2
    start_y = (SCREEN_HEIGHT - box_height) // 2
    pygame.draw.rect(screen, (30, 40, 60), (start_x, start_y, box_width, box_height), border_radius=10)
    pygame.draw.rect(screen, COLOR_RIVER, (start_x, start_y, box_width, box_height), width=2, border_radius=10)

    # text and analytics
    title = font_title.render("Finish", True, (255, 215, 0))
    screen.blit(title, (start_x + box_width // 2 - title.get_width() // 2, start_y + 30))
    screen.blit(font_bank.render(f"Total Number of Hackers: {total_h}", True, COLOR_HACKER), (start_x + 60, start_y + 90))
    screen.blit(font_bank.render(f"Total Number of Serfs: {total_s}", True, COLOR_SERF), (start_x + 60, start_y + 130))
    screen.blit(font_bank.render(f"Trips Realized: {total_trips}", True, COLOR_TEXT_MAIN), (start_x + 60, start_y + 170))


def organize_waiting_queues():
    # organized grid on the left bank for the waiting queues
    start_x, start_y, gap = 50, 200, 45

    # render hackers
    hacker_label = font_status.render(f"Hackers Waiting: {len(hacker_queue_list)}", True, COLOR_HACKER)
    screen.blit(hacker_label, (start_x, start_y - 35))
    for i, hacker in enumerate(hacker_queue_list):
        row = i // 5
        col = i % 5
        hacker.target_x = start_x + hacker.radius + (col * gap)
        hacker.target_y = start_y + (row * gap)
        hacker.update()
        hacker.draw()

    # render serfs
    serf_start_y = 420
    serf_label = font_status.render(f"Serfs Waiting: {len(serf_queue_list)}", True, COLOR_SERF)
    screen.blit(serf_label, (start_x, serf_start_y - 35))
    for i, serf in enumerate(serf_queue_list):
        row = i // 5
        col = i % 5
        serf.target_x = start_x + serf.radius + (col * gap)
        serf.target_y = serf_start_y + (row * gap)
        serf.update()
        serf.draw()
