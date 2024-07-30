import pygame
import os
import time
from backend.classes import buttons, spritesheet
from backend.player import player, randomPlayer
import json

pygame.init()

# Start MainMenu
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

# Game variables
MENU = 0
GAME_CONNECT = 1
GAME_PVP = 2
GAME_PVE = 3
SETTING = 4
ERROR = 5
TEST = 6
END = 7

ATTACK = 10
MOVE = 11
DONE_MOVE = 12
DONE_ATTACK = 13
port = 2000


game_state = MENU
client = None
prev_status = None
my_player = player(port)
bot = randomPlayer()

shipsName = ["s", "c", "w"]
ships = [pygame.Rect(32, 100, 35, 35), pygame.Rect(25, 200, 50, 50), pygame.Rect(18, 300, 65, 65)] 
shipsPos = [(32, 100), (25, 200), (18, 300)]
shipsCord = [None, None, None]
active_ship = None
my_turn = None
first_turn = None
movable = True
action = None
turn_time = None

move_data = None
attack_data = None
before_move = None


# Functions
def draw_text(text, size, col, x, y, shadow=False, font_name=os.path.join("assets", "Grand9K Pixel.ttf")):
    font = pygame.font.Font(font_name, size)
    if shadow == True:
        offset = 1 + (size // 15)
        shadow_img = font.render(text, True, (128,128,128))
        screen.blit(shadow_img, (x+offset, y+offset))
    img = font.render(text, True, col)
    screen.blit(img, (x, y))
       
def draw_map(sea1, sea2, background):
    global screen
    screen.blit(background, (0, 0))
    # Let game map be at (150, 50)
    for row in range(5):
        for col in range(5):
            if (row % 2 != 0 and col % 2 == 0) or (row % 2 == 0 and col % 2 != 0):
                screen.blit(sea2, (150+100*col, 50+100*row))
            else:
                screen.blit(sea1, (150+100*col, 50+100*row))

def decide_position(x, y, mode=None): # return indexes in matrix
    global shipsCord, active_ship
    if x > (150 + 500) or x < (150) or y < 50 or y > (50 + 500):
        return None
    if mode == "move":
        prev_x, prev_y = shipsCord[active_ship]
        if (x > 150+(prev_x+1)*100 or x < 150+prev_x*100) and (y > 50+(prev_y+1)*100 or y < 50+prev_y*100):
            return None
    px = (x - 150) // 100
    py = (y - 50) // 100
    return (px, py)

def center_pos(px, py, w, h):
    centered_x = 150 + px * 100 + 50 - w // 2
    centered_y = 50 + py * 100 + 50 - h // 2
    return (centered_x, centered_y)

def draw_attackable():
    global shipsCord, screen
    colorImage = pygame.Surface((100, 100)).convert_alpha()
    colorImage.fill("red")
    for ship in range(len(shipsCord)):
        if shipsCord[ship] != None:
            x = shipsCord[ship][0]
            y = shipsCord[ship][1]
            for draw_x in [x-1, x, x+1]:
                for draw_y in [y-1, y, y+1]:
                    if draw_x < 0 or draw_x > 4 or draw_y < 0 or draw_y > 4 or (draw_x == x and draw_y == y):
                        continue
                    else:
                        screen.blit(colorImage, (150+100*draw_x, 50+100*draw_y), special_flags = pygame.BLEND_RGBA_MULT)

def draw_movable():
    global active_ship, shipsCord, screen
    x = shipsCord[active_ship][0]
    y = shipsCord[active_ship][1]
    colorImage = pygame.Surface((100, 100)).convert_alpha()
    colorImage.fill((0, 51, 102))
    for i in range(5):
        if i != x:
            screen.blit(colorImage, (150 + i * 100, 50 + y * 100), special_flags=pygame.BLEND_RGBA_MULT)
        if i != y:
            screen.blit(colorImage, (150 + x * 100, 50 + i * 100), special_flags=pygame.BLEND_RGBA_MULT)

def decide_acctackable(px, py):
    global shipsCord
    for ship in range(len(shipsCord)):
        if shipsCord[ship] != None:
            x = shipsCord[ship][0]
            y = shipsCord[ship][1]
            if abs(px-x) <= 1 and abs(py-y) <= 1 and not (px == x and py == y):
                return True
    return False

def decide_movable(px, py):
    global shipsCord
    for ship in range(len(shipsCord)):
        if shipsCord[ship] != None:
            x = shipsCord[ship][0]
            y = shipsCord[ship][1]
            if x == px or y == py:
                return True
    return False



# Get assets
menu_spritesheet = spritesheet(os.path.join(os.getcwd(), "assets", "HUD_Menus.png"))
background = pygame.image.load(os.path.join(os.getcwd(), "assets", "background.png"))
background = pygame.transform.scale(background, (int(background.get_width() * 2.2), int(background.get_width() * 2)))
button_img = menu_spritesheet.image_at(pygame.Rect(449,347,388,149)) # asset position: https://getspritexy.netlify.app

sea1 = pygame.Surface((100, 100)) # Let each tile be 100*100
sea1.fill((201, 246, 253)) 
sea2 = pygame.Surface((100, 100))
sea2.fill((178,221,228)) 
black = pygame.Surface((800, 600))
black.fill((0, 0, 0))

# Buttons
pvp_button = buttons(303,120,button_img,0.5)
pve_button = buttons(303,220,button_img,0.5)
#setting_button = buttons(303,320,button_img,0.5)
quit_button = buttons(303,320,button_img,0.5)

ready_button = buttons(670, 300, button_img, 0.3)
attack_button = buttons(670, 200, button_img, 0.3)
move_button = buttons(670, 250, button_img, 0.3)
redo_button = buttons(670, 350, button_img, 0.3)


RUN = True
while RUN:
    screen.blit(background, (0, -100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and movable == True:
                for num, ship in enumerate(ships):
                    if ship.collidepoint(event.pos):
                        active_ship = num
        
        if event.type == pygame.MOUSEMOTION:
             if active_ship != None:
                ships[active_ship].move_ip(event.rel)


        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and active_ship != None:
                if action == MOVE:
                    stored_activeShip = active_ship
                    prev_pos = shipsPos[active_ship]
                    prev_cord = shipsCord[active_ship]
                    pPos = decide_position(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], mode="move")

                else:
                    pPos = decide_position(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

                if pPos == None or (pPos in shipsCord) or (action == MOVE and decide_movable(pPos[0], pPos[1]) == None):
                    ships[active_ship].update(shipsPos[active_ship], ships[active_ship].size)
                    active_ship = None
                else:
                    centeredPos = center_pos(pPos[0], pPos[1], ships[active_ship].width, ships[active_ship].height)
                    ships[active_ship].update(centeredPos, ships[active_ship].size)
                    shipsPos[active_ship] = centeredPos
                    shipsCord[active_ship] = pPos
                    if action == MOVE:
                        move_data = f"Player 2 moved {shipsName[active_ship]} by {pPos[0]-prev_cord[0]}, {pPos[1]-prev_cord[1]}"
                        action = DONE_MOVE
                    active_ship = None
            
            elif event.button == 1 and action == ATTACK:
                pPos = decide_position(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                if pPos != None:
                    if decide_acctackable(pPos[0], pPos[1]):
                        #print(f"Attack {pPos}")
                        centeredPos = center_pos(pPos[0], pPos[1], 25, 25)
                        draw_text("!", 25, (0,0,0), centeredPos[0], centeredPos[1])
                        attack_data = pPos
                        action = DONE_ATTACK




    if game_state == MENU:
        if pvp_button.draw(screen):
            game_state = GAME_CONNECT
        if pve_button.draw(screen):
            game_state = GAME_PVE
        #if setting_button.draw(screen):
        #    game_state = SETTING
        if quit_button.draw(screen):
            RUN = False
        draw_text("A Submarine Game", 40, (0,0,0), 220, 25, shadow=True)
        draw_text("PvP", 30, (255,255,255), 373, 130)
        draw_text("PvE", 30, (255,255,255), 373, 230)
        #draw_text("SETTING", 30, (255,255,255), 333, 330)
        draw_text("QUIT", 30, (255,255,255), 363, 330)
    

    elif game_state == GAME_CONNECT:
        try: 
            if client == None:
                client = my_player.connect()
                client.setblocking(False)
            else:
                try: 
                    info = client.recv(1024).decode()
                    if info == "FIRST":
                        first_turn = True
                    elif info == "SECOND":
                        first_turn = False
                    game_state = GAME_PVP
                except BlockingIOError:
                    draw_text("Waiting for another player to join...", 25, (0,0,0), 200, 200)
        except Exception as e:
            error_time = time.time()
            print(e)
            game_state = ERROR


    elif game_state == ERROR:
        draw_text("Can't connect to the server :(", 25, (0,0,0), 200, 200)
        draw_text("Going back to main menu...", 25, (0,0,0), 225, 300)
        if time.time() - error_time > 5:
            game_state = MENU

    
    elif game_state == GAME_PVP or game_state == GAME_PVE:
        draw_map(sea1, sea2, black)
        for i in range(len(ships)):
            if i == 0:
                pygame.draw.rect(screen, (0, 153, 76), ships[i])
            elif i == 1: 
                pygame.draw.rect(screen, (102, 102, 255), ships[i])
            else:
                pygame.draw.rect(screen, "orange", ships[i])
        if my_player.enemy_attack != None:
            draw_text(f"Player 2 attacked {my_player.enemy_attack}!", 15, (255, 255, 255), 250, 20)
        elif my_player.enemy_move != None:
            draw_text(f"{my_player.enemy_move}", 15, (255, 255, 255), 250, 20)
        else:
            draw_text("Player 2 didn't move or attack.", 15, (255, 255, 255), 250, 20)
        
        if my_turn != None:
            draw_text(f"My hps:", 15, (255, 255, 255), 20, 100)
            draw_text(f"s(green):  {my_player.hps['s']}", 15, (255, 255, 255), 20, 120)
            draw_text(f"c(blue):  {my_player.hps['c']}", 15, (255, 255, 255), 20, 140)
            draw_text(f"w(orange):  {my_player.hps['w']}", 15, (255, 255, 255), 20, 160)
            draw_text(f"Enemy hps:", 15, (255, 255, 255), 20, 220)
            draw_text(f"s(green):  {my_player.enemy_hps['s']}", 15, (255, 255, 255), 20, 240)
            draw_text(f"c(blue):  {my_player.enemy_hps['c']}", 15, (255, 255, 255), 20, 260)
            draw_text(f"w(orange):  {my_player.enemy_hps['w']}", 15, (255, 255, 255), 20, 280)
            

        if my_turn == None:
            draw_text("Place your ships and click Ready. ", 15, (255, 255, 255), 250, 570)
            if ready_button.draw(screen):
                if None not in shipsCord:
                    movable = False
                    if game_state == GAME_PVP:
                        client.sendall("READY".encode())
                        my_turn = "wait"
                    elif game_state == GAME_PVE:
                        my_turn = True
                        turn_time = time.time()
            draw_text("ready", 15, (255, 255, 255), 680, 310)
                   

        elif my_turn == "wait":
            draw_text("Another player is not ready...", 25, (0,0,0), 170, 200)
            try:
                client.recv(1024).decode()
                if first_turn:
                    my_turn = True
                    turn_time = time.time()
                else:
                    my_turn = False
            except BlockingIOError:
                pass



        elif my_turn == True:
            countdown = time.time() - turn_time
            draw_text(f'Countdown:  {str(90 - int(countdown))}', 15, (255, 255, 255), 10, 350)
            if 90 - int(countdown) == 0:
                if game_state == GAME_PVP:
                    my_player.send_data(client)
                my_turn = False

            if action == ATTACK:
                draw_attackable()
                if redo_button.draw(screen):
                    action = None
                    attack_data = None
                draw_text("redo", 15, (255, 255, 255), 680, 360)

            elif action == MOVE:
                movable = True
                if active_ship != None:
                    draw_movable()
                if redo_button.draw(screen):
                    action = None
                    movable = False
                draw_text("redo", 15, (255, 255, 255), 680, 360)
            
            elif action == DONE_MOVE:
                movable = False
                if redo_button.draw(screen):
                    action = None
                    move_data = None
                    shipsCord[stored_activeShip] = prev_cord
                    shipsPos[stored_activeShip] = prev_pos
                    ships[stored_activeShip].update(prev_pos, ships[stored_activeShip].size)
                if ready_button.draw(screen):
                    if game_state == GAME_PVP:
                        my_player.send_data(client, move=move_data)
                    my_turn = False
                draw_text("redo", 15, (255, 255, 255), 680, 360)
                draw_text("ready", 15, (255, 255, 255), 680, 310)
            
            elif action == DONE_ATTACK:
                centeredPos = center_pos(attack_data[0], attack_data[1], 30, 30)
                draw_text("!", 30, (255,0,0), centeredPos[0], centeredPos[1])
                if redo_button.draw(screen):
                    action = None
                    attack_data = None
                if ready_button.draw(screen):
                    if  game_state == GAME_PVP:
                        my_player.send_data(client, attack=attack_data)
                    elif game_state == GAME_PVE:
                        bot._handle_attack(attack_data)
                    my_turn = False
                draw_text("redo", 15, (255, 255, 255), 680, 360)
                draw_text("ready", 15, (255, 255, 255), 680, 310)

            else:
                draw_text("Select your action. ", 15, (255, 255, 255), 250, 570)
                if attack_button.draw(screen):
                    action = ATTACK
                if move_button.draw(screen):
                    action = MOVE
                if ready_button.draw(screen): # No action
                    if game_state == GAME_PVP:
                        my_player.send_data(client)
                    my_turn = False
                draw_text("attack", 15, (255, 255, 255), 680, 210)
                draw_text("move", 15, (255, 255, 255), 680, 260)
                draw_text("ready", 15, (255, 255, 255), 680, 310)

        elif not my_turn:
            my_player.update_positions(shipsCord)
            draw_text("Waiting for another player's action...", 25, (0,0,0), 170, 200)
            try:
                if game_state == GAME_PVP:
                    another_player = client.recv(1024) # Status of another player
                    another_player = json.loads(another_player.decode('utf-8'))
                    prevAction = my_player.receive_data(another_player, client)
                elif game_state == GAME_PVE:
                    another_player = bot.action()
                    prevAction = my_player.receive_data(another_player, None)
                if prevAction == "Win" or prevAction == "Lose":
                    game_state = END
                    end_time = time.time()
                my_turn = True
                action = None
                move_data = None
                attack_data = None
                for key, value in my_player.hps.items():
                    if key == 's' and value == 0:
                        shipsCord[0] = None
                        ships[0].update((-100, -100), ships[0].size)
                    if key == 'c' and value == 0:
                        shipsCord[1] = None
                        ships[1].update((-100, -100), ships[1].size)
                    if key == 'w' and value == 0:
                        shipsCord[2] = None
                        ships[2].update((-100, -100), ships[2].size)
                turn_time = time.time()
            except BlockingIOError:
                pass
        
    elif game_state == END:
        draw_text(f"You {prevAction}!", 25, (0, 0, 0), 200, 200)
        if game_state == GAME_PVP:
            client.close()
        if time.time() - end_time > 5:
            game_state = MENU
            client = None
            prev_status = None
            my_player = player(port)

            shipsName = ["s", "c", "w"]
            ships = [pygame.Rect(32, 100, 35, 35), pygame.Rect(25, 200, 50, 50), pygame.Rect(18, 300, 65, 65)] 
            shipsPos = [(32, 100), (25, 200), (18, 300)]
            shipsCord = [None, None, None]
            active_ship = None
            my_turn = None
            first_turn = None
            movable = True
            action = None
            turn_time = None

            move_data = None
            attack_data = None
            before_move = None
    


                
        


        

    pygame.display.update()


    # Event Handler for Main Menu