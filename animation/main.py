import sys
import threading
import queue
import time
import pygame

import renderer
from config import clock, COLOR_HACKER, COLOR_SERF, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
from entity import Entity
from renderer import (
    hacker_queue_list, serf_queue_list, boat_list,
    input_command_queue, sys_state, add_log,
    draw_environment, draw_boat_and_passengers,
    draw_system, draw_logs, draw_final, organize_waiting_queues
)

# input reading thread -> reads stdout from river_crossing and enqueues events
def read_input_thread():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split(":")
        if len(parts) >= 3:
            input_command_queue.put(parts)


def main():
    thread = threading.Thread(target=read_input_thread, daemon=True)
    thread.start()

    # game loop
    running = True
    target_dock_x = 590   # right bank docking position
    original_dock_x = 120 # left bank docking position

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # process commands from the async queue
        try:
            while True:
                parts = input_command_queue.get_nowait()
                action, p_type, idx = parts[0], parts[1].upper(), parts[2]

                if action == "ARRIVED":
                    target_y_pos = 200 if p_type == 'HACKER' else 420
                    new_entity = Entity(idx, p_type, current_x=-40, current_y=target_y_pos)
                    if p_type == "HACKER":
                        hacker_queue_list.append(new_entity)
                    else:
                        serf_queue_list.append(new_entity)
                    cor = COLOR_HACKER if p_type == 'HACKER' else COLOR_SERF
                    add_log(f"Thread created: {p_type} {idx} waiting.", cor)

                elif action == "BOARDED":
                    if p_type == "HACKER":
                        for ent in hacker_queue_list:
                            if ent.id == idx:
                                hacker_queue_list.remove(ent)
                                boat_list.append(ent)
                                break
                    else:
                        for ent in serf_queue_list:
                            if ent.id == idx:
                                serf_queue_list.remove(ent)
                                boat_list.append(ent)
                                break
                    renderer.boat_status_text = f"PASSENGERS BOARDING ({len(boat_list)}/4)"
                    add_log(f"Signal recieved: {p_type} {idx} joined to the boat.", COLOR_TEXT_MAIN)

                elif action == "ROWED":
                    renderer.boat_status_text = f"CRUISING - CAPTAIN: {p_type} {idx} ROWING"
                    renderer.boat_is_rowing = True
                    renderer.total_trips += 1
                    add_log(f"Travel started (Leader: {p_type} {idx}).", (255, 215, 0))

                elif action == "STATUS":
                    key = parts[1].lower()
                    value = parts[2].upper()
                    if key in sys_state:
                        sys_state[key] = value
                    add_log(f"OS Kernel -> {key.upper()} changed to {value}", COLOR_TEXT_MUTED)

                elif action == "Final":
                    renderer.total_h = int(parts[1])
                    renderer.total_s = int(parts[2])
                    renderer.finished = True
                    add_log("Code Finished", (255, 215, 0))

        except queue.Empty:
            pass

        # boat crossing animation
        if renderer.boat_is_rowing:
            if renderer.boat_current_x < target_dock_x:
                renderer.boat_current_x += renderer.animation_speed
            else:
                renderer.boat_is_rowing = False
                renderer.boat_status_text = "ARRIVED! DISEMBARKING..."
                draw_environment()
                draw_boat_and_passengers()
                pygame.display.flip()
                time.sleep(1.2)
                boat_list.clear()
                renderer.boat_current_x = original_dock_x
                renderer.boat_status_text = "DOCKING - WAITING FOR PASSENGERS"

        draw_environment()
        organize_waiting_queues()
        draw_boat_and_passengers()
        draw_system()
        draw_logs()
        if renderer.finished and not renderer.boat_is_rowing and len(boat_list) == 0:
            draw_final()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
