import sys
import pygame
import threading
import queue
import time
import math

# dimensions of the game
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 650

# graphics
COLOR_BG = (18, 24, 38)          # background
COLOR_RIVER_BED = (26, 36, 56)    # Fundo do rio
COLOR_RIVER = (0, 180, 216)       # \água
COLOR_HACKER = (57, 255, 20)      # hackler
COLOR_SERF = (255, 7, 58)         # serf
COLOR_BOAT = (197, 137, 64)       # barco
COLOR_BOAT_DARK = (141, 91, 35)   # barco sombra
COLOR_TEXT_MAIN = (248, 249, 250) # texto
COLOR_TEXT_MUTED = (108, 117, 125)# texto 2   mudar isso dps  ta feio

# Inicializando o jogo
pygame.init()
pygame.display.set_caption("MC504 - Multithread River Crossing Visualizer") #title
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont("Segoe UI", 32, bold=True)
font_bank = pygame.font.SysFont("Segoe UI", 22, bold=True)
font_status = pygame.font.SysFont("Consolas", 16, bold=True)
font_id = pygame.font.SysFont("Segoe UI", 14, bold=True)

# Queue
hacker_queue_list = []
serf_queue_list = []
boat_list = []
boat_current_x = 120  
boat_status_text = "DOCKING - WAITING FOR PASSENGERS"
boat_is_rowing = False
animation_speed = 2
input_command_queue = queue.Queue()
wave_offset = 0 # p animar a correnteza do rio

sys_state = {
    "mutex":"UNLOCKED",
    "barrier": "CLOSED"
}
#logs
event_logs = []
max = 6
font_log = pygame.font.SysFont("Consolas", 13, bold=False)
def add_log(message, color=COLOR_TEXT_MAIN):
    curr_time = time.strftime("%H:%M:%S")
    event_logs.append((f"{curr_time} {message}", color))
    if (len(event_logs) > max):
        event_logs.pop(0)
# Entity Class
class Entity:
    def __init__(self, id, type, current_x, current_y):
        self.id = id
        self.type = type # HACKER ou SERF
        #position 
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
        # movimento com interpolação exponencial
        self.x += (self.target_x - self.x) * 0.12
        self.y += (self.target_y - self.y) * 0.12

#render the scenario
def draw_environment():
    screen.fill(COLOR_BG)
    global wave_offset
    wave_offset += 0.5
    
    # Draw the boat
    river_x, river_width = 350, 400
    pygame.draw.rect(screen, COLOR_RIVER_BED, (river_x, 0, river_width, SCREEN_HEIGHT))
    pygame.draw.rect(screen, COLOR_RIVER, (river_x + 10, 0, river_width - 20, SCREEN_HEIGHT))
    
    # animate the water - "waves"
    for y in range(0, SCREEN_HEIGHT, 40):
        y_pos = (y + int(wave_offset)) % SCREEN_HEIGHT
        pygame.draw.line(screen, (255, 255, 255, 40), (river_x + 50, y_pos), (river_x + 80, y_pos + 10), 2)
        pygame.draw.line(screen, (255, 255, 255, 40), (river_x + 200, y_pos - 15), (river_x + 240, y_pos - 5), 2)
        pygame.draw.line(screen, (255, 255, 255, 40), (river_x + 320, y_pos + 10), (river_x + 350, y_pos + 20), 2)

    # desenha os píers de pro barquinho
    pygame.draw.rect(screen, (45, 55, 72), (250, (SCREEN_HEIGHT // 2) - 60, 100, 120), border_radius=5) # Píer esquerdo
    pygame.draw.rect(screen, (45, 55, 72), (750, (SCREEN_HEIGHT // 2) - 60, 100, 120), border_radius=5) # Píer direito

    # cabeçalho e textos
    title_surf = font_title.render("RIVER CROSSING VISUALIZER", True, COLOR_TEXT_MAIN)
    screen.blit(title_surf, (50, 30))
    
    sub_surf = font_status.render("Operating Systems Project - Unicamp", True, COLOR_TEXT_MUTED)
    screen.blit(sub_surf, (50, 75))
    
    screen.blit(font_bank.render("LEFT BANK", True, COLOR_TEXT_MAIN), (50, 140))
    screen.blit(font_bank.render("RIGHT BANK", True, COLOR_TEXT_MAIN), (SCREEN_WIDTH - 200, 140))

def draw_system():
    width = 2
    height = 110
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, (10, 15, 25, 210), (0, 0, width, height), border_radius=8)
    pygame.draw.rect(surface, (60, 70, 90, 255), (0, 0, width, height), width=2, border_radius=8)

    begin_x, begin_y = SCREEN_WIDTH - 300,20
    screen.blit(surface, (begin_x, begin_y))
    screen.blit(font_status.render("Operational System State", True, (255,215,0)), (begin_x + 15, begin_y + 15))

    mutex_color = COLOR_SERF if sys_state["mutex"] == "LOCKED" else COLOR_HACKER
    screen.blit(font_status.render(f"Mutex:   {sys_state['mutex']}", True, mutex_color), (begin_x + 15, begin_y + 45))

    barrier_color = COLOR_SERF if sys_state["barrier"] == "CLOSED" else COLOR_HACKER
    screen.blit(font_status.render(f"Barrier: {sys_state['barrier']}", True, barrier_color), (begin_x + 15, begin_y + 70))

def draw_logs():
    width = 420
    height = 150
    begin_x = 50
    begin_y = SCREEN_HEIGHT - height - 10

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, (10,15,25,220), (0,0,width,height), border_radius=6)
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
    
    # desenha o formato do barco
    points = [
        (boat_current_x, boat_y + 10),
        (boat_current_x + boat_width - 30, boat_y),
        (boat_current_x + boat_width, boat_y + boat_height // 2), # Bico
        (boat_current_x + boat_width - 30, boat_y + boat_height),
        (boat_current_x, boat_y + boat_height - 10)
    ]
    pygame.draw.polygon(screen, COLOR_BOAT_DARK, [(p[0], p[1] + 5) for p in points]) # Sombra
    pygame.draw.polygon(screen, COLOR_BOAT, points)
    
    # desenha os banquinhos do barco
    seat_positions = [
        (boat_current_x + 25,  boat_y + boat_height // 2),
        (boat_current_x + 60,  boat_y + boat_height // 2),
        (boat_current_x + 95,  boat_y + boat_height // 2),
        (boat_current_x + 130, boat_y + boat_height // 2)
    ]
    
    for i in range(4):
        bx, by = seat_positions[i]
        pygame.draw.rect(screen, COLOR_BOAT_DARK, (bx - 12, boat_y + 12, 24, boat_height - 24), border_radius=3)

    # flutuando barco em X
    status_surf = font_status.render(boat_status_text, True, (255, 215, 0) if "CRUISING" in boat_status_text else COLOR_TEXT_MAIN)
    status_rect = status_surf.get_rect(center=(boat_current_x + boat_width // 2, boat_y - 25))
    screen.blit(status_surf, status_rect)
    
    # atualiza e desenha os passageiros nos assentos corretos
    for i, entity in enumerate(boat_list):
        if i < 4:
            seat_x, seat_y = seat_positions[i]
            
            # se o barco estiver parado carregando, o boneco vai flutuando até o assento
            if not boat_is_rowing:
                entity.target_x = seat_x
                entity.target_y = seat_y
                entity.update()
            else:
                # se o barco tiver andando., boneco trava instantaneamente no assento
                # para não dar efeito de "atraso" ou ficar flutuando fora
                entity.x = seat_x
                entity.target_x = seat_x
                entity.y = seat_y
                entity.target_y = seat_y
                
            entity.draw()
def organize_waiting_queues():
    # grid organizado na margem esquerda para as filas de espera
    start_x, start_y, gap = 60, 200, 45
    
    # Render dos Hackers
    hacker_label = font_status.render(f"Hackers Waiting: {len(hacker_queue_list)}", True, COLOR_HACKER)
    screen.blit(hacker_label, (start_x, start_y - 25))
    for i, hacker in enumerate(hacker_queue_list):
        row = i // 5
        col = i % 5
        hacker.target_x = start_x + (col * gap)
        hacker.target_y = start_y + (row * gap)
        hacker.update()
        hacker.draw()

    # render dos Serfs 
    serf_start_y = 420
    serf_label = font_status.render(f"Serfs Waiting: {len(serf_queue_list)}", True, COLOR_SERF)
    screen.blit(serf_label, (start_x, serf_start_y - 25))
    for i, serf in enumerate(serf_queue_list):
        row = i // 5
        col = i % 5
        serf.target_x = start_x + (col * gap)
        serf.target_y = serf_start_y + (row * gap)
        serf.update()
        serf.draw()

# input Reading Thread (link com o cod river_crossing
def read_input_thread():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        parts = line.split(":")
        if len(parts) >= 3:
            input_command_queue.put(parts)

thread = threading.Thread(target=read_input_thread, daemon=True)
thread.start()

# loop do jogo
running = True
target_dock_x = 590   # ponto de parada na margem direita
original_dock_x = 120 # P]ponto de parada na margem esquerda

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # processamento de comandos da fila assíncrona
    try:
        while True:
            parts = input_command_queue.get_nowait()
            action, p_type, idx = parts[0], parts[1].upper(), parts[2]
            
            if action == "CHEGOU":
                
                target_y_pos = 200 if p_type == 'HACKER' else 420
                new_entity = Entity(idx, p_type, current_x=-40, current_y=target_y_pos)
                if p_type == "HACKER":
                    hacker_queue_list.append(new_entity)
                else:
                    serf_queue_list.append(new_entity)
                
                cor = COLOR_HACKER if p_type == 'HACKER' else COLOR_SERF
                add_log(f"Thread created: {p_type} {idx} waiting.", cor)
                    
            elif action == "EMBARCOU":
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
                boat_status_text = f"PASSENGERS BOARDING ({len(boat_list)}/4)"
                add_log(f"Signal recieved: {p_type} {idx} joined to the boat.", COLOR_TEXT_MAIN)
                
            elif action == "REMOU":
                boat_status_text = f"CRUISING - CAPTAIN: {p_type} {idx} ROWING"
                boat_is_rowing = True
                add_log(f"Travel started (Leader: {p_type} {idx}).", (255, 215, 0))

            elif action == "STATUS":
                key = parts[1].lower()
                value = parts[2].upper()
                if key in sys_state:
                    sys_state[key] = value 
                add_log(f"OS Kernel -> {key.upper()} changed to {value}", COLOR_TEXT_MUTED)

    except queue.Empty:
        pass

    # travessia do barco
    if boat_is_rowing:
        if boat_current_x < target_dock_x:
            boat_current_x += animation_speed
        else:
            boat_is_rowing = False
            boat_status_text = "ARRIVED! DISEMBARKING..."
            draw_environment()
            draw_boat_and_passengers()
            pygame.display.flip()
            time.sleep(1.2) 
            boat_list.clear()
            boat_current_x = original_dock_x
            boat_status_text = "DOCKING - WAITING FOR PASSENGERS"

    # rodar na tela
    draw_environment()
    organize_waiting_queues()
    draw_boat_and_passengers()
    draw_system()
    draw_logs()
    
    pygame.display.flip()
    clock.tick(60)
    

pygame.quit()
sys.exit()