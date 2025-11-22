import pygame
import sys
import os
import random
from settings import *
from player import Player
from ui import Button
from game_objects import Platform, Projectile, ExplosionParticle, Collectible
from save_manager import save_game, load_game

class Game:
    def __init__(self):
        pygame.init()
        # Get the current screen resolution
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # Set fullscreen with the native resolution
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption(TITLE)
        
        # Calculate scaling/centering offsets if needed (for now, we'll just center the game area)
        # Or better: Update WIDTH/HEIGHT constants to match screen, OR draw to a surface and scale it.
        # Simplest approach for now: Update the logic to use dynamic width/height
        # But wait, our logic relies on WIDTH/HEIGHT constants.
        # Let's override them for this instance or center the gameplay area.
        
        # Strategy: Use a virtual surface for the game (800x600 or 1000x700) and scale it up?
        # User said "doesn't fit the entire screen".
        # If we just change the window size, the game logic (platforms etc) might be small in corner.
        # Let's scale the game view to fit screen.
        
        self.game_surface = pygame.Surface((WIDTH, HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, 32)
        self.running = True
        self.state = "USERNAME" 
        
        # Load Resources
        self.weapon_textures = {}
        self.load_resources()
        
        # Game Objects
        self.player = Player()
        self.input_text = ""
        self.cpu_count_text = ""
        self.num_cpus = 1
        self.battle_cpus = []
        self.platforms = []
        self.projectiles = []
        self.particles = []
        self.collectibles = []
        
        self.message = ""
        self.message_timer = 0
        
        # UI Buttons (Center them based on original coords, we will scale input too)
        self.menu_buttons = [
            Button(WIDTH/2 - 100, HEIGHT/2 + 60, 200, 50, "Play vs CPU"),
            Button(WIDTH/2 - 100, HEIGHT/2 + 120, 200, 50, "Weapon Shop"),
            Button(WIDTH/2 - 100, HEIGHT/2 + 180, 200, 50, "Change Username", font_size=24),
            Button(WIDTH/2 - 100, HEIGHT/2 + 240, 200, 50, "Quit")
        ]
        
        self.shop_buttons = []
        self.shop_scroll = 0
        self.exit_button = Button(10, 10, 100, 40, "Menu", font_size=20)
        
        # Physics Constants
        self.GRAVITY = 0.5
        
        # Initialize default map
        self.load_map("Street")
        
        # Load Save Data
        self.load_save_data()

    def load_save_data(self):
        data = load_game()
        if data:
            self.player.username = data.get("username", "Player")
            self.player.coins = data.get("coins", STARTING_COINS)
            self.player.inventory = data.get("inventory", ["Fist"])
            self.player.current_weapon_name = data.get("current_weapon", "Fist")
            
            # If username is set, skip to menu
            if self.player.username and self.player.username != "Player":
                self.state = "MENU"

    def save_data(self):
        save_game(self.player)

    def load_resources(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        weapons_dir = os.path.join(script_dir, "weapons")
        
        if not os.path.exists(weapons_dir):
            os.makedirs(weapons_dir)
            
        for name, filename in WEAPON_FILES.items():
            path = os.path.join(weapons_dir, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Scale down if too big
                    if img.get_width() > 60:
                        scale = 60 / img.get_width()
                        img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    self.weapon_textures[name] = img
                except Exception as e:
                    print(f"Failed to load {name}: {e}")

    def load_map(self, map_name):
        self.platforms = []
        map_data = MAPS.get(map_name, MAPS["Street"])
        self.current_map_data = map_data
        
        # Floor
        self.platforms.append(Platform(0, HEIGHT - 50, WIDTH, 50, map_data["ground_color"]))
        
        # Some platforms
        self.platforms.append(Platform(200, HEIGHT - 150, 200, 20, map_data["ground_color"]))
        self.platforms.append(Platform(600, HEIGHT - 250, 200, 20, map_data["ground_color"]))
        self.platforms.append(Platform(400, HEIGHT - 400, 200, 20, map_data["ground_color"]))

    def show_message(self, text, duration=2000):
        self.message = text
        self.message_timer = pygame.time.get_ticks() + duration

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.SysFont(FONT_NAME, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.game_surface.blit(text_surface, text_rect)

    def new_game(self):
        self.player.reset_position()
        self.battle_cpus = []
        self.projectiles = []
        self.particles = []
        
        # Create CPUs
        for i in range(self.num_cpus):
            cpu = Player(username=f"CPU {i+1}", is_cpu=True)
            cpu.rect.x = WIDTH - 100 - (i * 100)
            cpu.rect.y = 100
            
            # Match Player Weapon
            weapon_name = self.player.current_weapon_name
            # Ensure CPU has it in inventory
            if weapon_name not in cpu.inventory:
                cpu.inventory.append(weapon_name)
            cpu.equip_weapon(weapon_name)
            
            self.battle_cpus.append(cpu)
        self.run()
        
    def update_shop_buttons(self):
        self.shop_buttons = []
        start_y = 100
        btn_height = 50
        padding = 10
        
        sorted_weapons = sorted(WEAPONS_DATA.items(), key=lambda x: x[1]['cost'])
        
        for i, (name, data) in enumerate(sorted_weapons):
            color = WHITE
            status = f"{data['cost']} Coins"
            if name in self.player.inventory:
                color = LIGHT_BLUE
                status = "Owned"
                if name == self.player.current_weapon_name:
                    color = GREEN
                    status = "Equipped"
            
            btn_text = f"{name} ({data['damage']} dmg) - {status}"
            # Adjust y for scrolling if needed, but for now simple list
            y_pos = start_y + i * (btn_height + padding) - self.shop_scroll
            if 50 < y_pos < HEIGHT - 50:
                self.shop_buttons.append(Button(WIDTH/2 - 250, y_pos, 500, btn_height, btn_text, font_size=24, bg_color=color))

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        # Calculate scaling for mouse input
        scale_w = self.screen_width / WIDTH
        scale_h = self.screen_height / HEIGHT
        scale = min(scale_w, scale_h)
        
        # Calculate offset to center the game
        offset_x = (self.screen_width - WIDTH * scale) / 2
        offset_y = (self.screen_height - HEIGHT * scale) / 2
        
        raw_mouse_pos = pygame.mouse.get_pos()
        # Transform mouse pos to game space
        mouse_x = (raw_mouse_pos[0] - offset_x) / scale
        mouse_y = (raw_mouse_pos[1] - offset_y) / scale
        mouse_pos = (mouse_x, mouse_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass # Ignore window close button

            # Shop scrolling
            if event.type == pygame.MOUSEWHEEL and self.state == "SHOP":
                self.shop_scroll -= event.y * 20
                self.shop_scroll = max(0, self.shop_scroll)
                self.update_shop_buttons()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in ["BATTLE", "SHOP", "CPU_SELECT"]:
                        self.state = "MENU"
                        self.save_data() # Save when returning to menu
                    elif self.state == "MENU":
                         self.save_data()
                         self.running = False
                         pygame.quit()
                         sys.exit()

                if self.state == "USERNAME":
                    if event.key == pygame.K_RETURN:
                        if len(self.input_text) > 0:
                            self.player.username = self.input_text
                            self.state = "MENU"
                            self.save_data() # Save username
                            self.input_text = "" 
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 15: 
                            self.input_text += event.unicode

                elif self.state == "CPU_SELECT":
                    if event.key == pygame.K_RETURN:
                        try:
                            val = int(self.cpu_count_text)
                            if 1 <= val <= 4:
                                self.num_cpus = val
                                self.state = "BATTLE"
                                self.new_game()
                            else:
                                self.cpu_count_text = "" 
                                self.show_message("Sorry only number is one through four")
                        except ValueError:
                            self.cpu_count_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.cpu_count_text = self.cpu_count_text[:-1]
                    else:
                        if event.unicode.isdigit() and len(self.cpu_count_text) < 1:
                            self.cpu_count_text += event.unicode

                elif self.state == "BATTLE":
                    if event.key == pygame.K_k:
                        self.perform_attack(self.player)
            
            # Mouse Events
            if event.type == pygame.MOUSEBUTTONDOWN:
                 if self.state == "BATTLE":
                      # Check if clicking a UI button first
                      if self.exit_button.is_clicked_custom(event, mouse_pos):
                          self.state = "MENU"
                          self.save_data()
                      else:
                          self.perform_attack(self.player)
                          
            if self.state == "MENU":
                for btn in self.menu_buttons:
                    btn.check_hover(mouse_pos)
                    if btn.is_clicked_custom(event, mouse_pos):
                        if btn.text == "Play vs CPU":
                            self.state = "CPU_SELECT"
                            self.cpu_count_text = ""
                        elif btn.text == "Weapon Shop":
                            self.state = "SHOP"
                            self.update_shop_buttons()
                        elif btn.text == "Change Username":
                            self.state = "USERNAME"
                            self.input_text = ""
                        elif btn.text == "Quit":
                            self.save_data()
                            self.running = False
                            pygame.quit()
                            sys.exit()
                            
            elif self.state == "SHOP":
                if self.exit_button.is_clicked_custom(event, mouse_pos):
                    self.state = "MENU"
                    self.save_data()
                    
                for btn in self.shop_buttons:
                    btn.check_hover(mouse_pos)
                    if btn.is_clicked_custom(event, mouse_pos):
                        # Extract name from text (a bit hacky but works for now)
                        text = btn.text.split('(')[0].strip()
                        self.try_buy(text)
                        self.update_shop_buttons() 

            elif self.state == "CPU_SELECT":
                 self.exit_button.check_hover(mouse_pos)
                 if self.exit_button.is_clicked_custom(event, mouse_pos):
                     self.state = "MENU"


    def try_buy(self, weapon_name):
        if weapon_name in self.player.inventory:
            self.player.equip_weapon(weapon_name)
            self.save_data()
        elif self.player.buy_weapon(weapon_name):
            print(f"Bought {weapon_name}")
            self.save_data()
        else:
            self.show_message("Not enough coins!")

    def perform_attack(self, attacker):
        current_time = pygame.time.get_ticks()
        
        # Check cooldown
        if current_time - attacker.last_attack_time < attacker.attack_cooldown:
            return
            
        attacker.last_attack_time = current_time
        attacker.is_attacking = True
        
        weapon = attacker.current_weapon
        
        # Set cooldown based on weapon speed (higher speed = faster?)
        # Original: speed 12. Let's map it. 
        # Maybe 1000ms / speed? e.g. 1000/12 = 83ms. 
        base_cooldown = max(200, 2000 // weapon['speed'])
        if attacker.is_cpu:
            base_cooldown *= 1.5 # Balanced attacks for CPU
        attacker.attack_cooldown = base_cooldown 

        if weapon.get('melee', False):
            # Melee Attack
            hit_box = attacker.rect.copy()
            if attacker.facing_right:
                hit_box.x += hit_box.width
            else:
                hit_box.x -= hit_box.width
            
            # Check collisions
            targets = self.battle_cpus if attacker == self.player else [self.player]
            for target in targets:
                if hit_box.colliderect(target.rect):
                    target.take_damage(weapon['damage'])
                    # Knockback
                    if attacker.rect.centerx < target.rect.centerx:
                        target.rect.x += 10
                    else:
                        target.rect.x -= 10
                    
                    if target.hp <= 0:
                        self.handle_kill(attacker, target)

        else:
            # Ranged Attack (Projectile)
            vx = 10 if attacker.facing_right else -10
            vy = -2 # Slight arc up
            
            # Spawn at weapon position
            start_x = attacker.rect.right if attacker.facing_right else attacker.rect.left
            start_y = attacker.rect.centery
            
            proj = Projectile(start_x, start_y, vx, vy, attacker.current_weapon_name, attacker)
            self.projectiles.append(proj)

    def handle_kill(self, attacker, victim):
        if victim in self.battle_cpus:
            attacker.coins += WIN_REWARD
            self.battle_cpus.remove(victim)
            self.particles.append(ExplosionParticle(victim.rect.centerx, victim.rect.centery, RED))
            if not self.battle_cpus:
                self.state = "MENU" 
                self.show_message(f"You Won! +{WIN_REWARD * self.num_cpus} Coins")
                self.save_data() # Save coins
        elif victim == self.player:
            self.player.coins = max(0, self.player.coins - LOSE_PENALTY)
            self.state = "MENU"
            self.show_message("You Lost! -10 Coins")
            self.save_data() # Save coins

    def update_physics(self, entity):
        # Apply Gravity
        entity.vel_y += self.GRAVITY
        
        # Move Y
        entity.rect.y += entity.vel_y
        entity.on_ground = False
        
        # Check Platform Collisions (Y axis)
        for platform in self.platforms:
            if platform.check_collision(entity, entity.vel_y):
                entity.rect.bottom = platform.y
                entity.vel_y = 0
                entity.on_ground = True
        
        # Keep in bounds
        if entity.rect.bottom > HEIGHT:
            entity.rect.bottom = HEIGHT
            entity.vel_y = 0
            entity.on_ground = True
            
        # Move X (handled by input/AI, but collision check could go here)
        entity.rect.x += entity.vel_x
        if entity.rect.left < 0: entity.rect.left = 0
        if entity.rect.right > WIDTH: entity.rect.right = WIDTH

    def update(self):
        if self.message and pygame.time.get_ticks() > self.message_timer:
            self.message = ""

        if self.state == "BATTLE":
            # Player Movement
            self.player.vel_x = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player.vel_x = -self.player.speed
                self.player.facing_right = False
            if keys[pygame.K_d]:
                self.player.vel_x = self.player.speed
                self.player.facing_right = True
            
            # Jump
            if keys[pygame.K_SPACE] and self.player.on_ground:
                self.player.vel_y = -12

            self.update_physics(self.player)
            
            # Reset attack visual
            if pygame.time.get_ticks() - self.player.last_attack_time > 200:
                 self.player.is_attacking = False
            
            # CPU Logic
            current_time = pygame.time.get_ticks()
            for cpu in self.battle_cpus:
                cpu.vel_x = 0
                dist = abs(cpu.rect.centerx - self.player.rect.centerx)
                
                # Face player always
                if cpu.rect.centerx < self.player.rect.centerx:
                    cpu.facing_right = True
                else:
                    cpu.facing_right = False
                    
                # Move towards player if far
                weapon = cpu.current_weapon
                desired_range = weapon.get('range', 200) if weapon.get('melee') else 300
                
                if dist > desired_range:
                    if cpu.facing_right:
                        cpu.vel_x = cpu.speed * 0.7 # Balanced movement
                    else:
                        cpu.vel_x = -cpu.speed * 0.7
                elif dist < desired_range - 100:
                     # Back up if too close (optional for better AI)
                    if cpu.facing_right:
                        cpu.vel_x = -cpu.speed * 0.7
                    else:
                        cpu.vel_x = cpu.speed * 0.7
                
                # Jump random
                if cpu.on_ground and random.random() < 0.008: # Balanced jumping
                    cpu.vel_y = -10
                
                self.update_physics(cpu)
                
                # Attack
                if dist < desired_range + 50: # Attack range
                     if random.random() < 0.06: # Better reaction time
                        self.perform_attack(cpu)
                     
                if pygame.time.get_ticks() - cpu.last_attack_time > 200:
                    cpu.is_attacking = False

            # Projectiles
            for p in self.projectiles[:]:
                if not p.update():
                    self.projectiles.remove(p)
                    continue
                
                # Check hits
                targets = self.battle_cpus if p.owner == self.player else [self.player]
                hit = False
                for target in targets:
                    if p.rect.colliderect(target.rect):
                        target.take_damage(p.data['damage'])
                        self.particles.append(ExplosionParticle(p.x, p.y, p.color))
                        if target.hp <= 0:
                            self.handle_kill(p.owner, target)
                        hit = True
                        break
                
                if hit:
                    self.projectiles.remove(p)
                else:
                    # Platform collision
                    for plat in self.platforms:
                        if p.rect.colliderect(plat.rect):
                            self.particles.append(ExplosionParticle(p.x, p.y, GRAY))
                            self.projectiles.remove(p)
                            break
            
            # Particles
            for part in self.particles[:]:
                if not part.update():
                    self.particles.remove(part)

    def draw(self):
        # Draw everything to game_surface first
        self.game_surface.fill(LIGHT_BLUE)
        
        if self.state == "BATTLE":
            map_data = self.current_map_data
            self.game_surface.fill(map_data['bg_color'])
            
            # Draw Platforms
            for plat in self.platforms:
                plat.draw(self.game_surface)
            
             # Draw Objects
            for p in self.projectiles:
                p.draw(self.game_surface)
                
            # Draw Player
            self.player.draw(self.game_surface, self.weapon_textures)
            
            # Draw CPUs
            for cpu in self.battle_cpus:
                cpu.draw(self.game_surface, self.weapon_textures)
            
            # Particles
            for part in self.particles:
                part.draw(self.game_surface)
            
            self.draw_text("WASD to Move, Space to Jump, Mouse/K to Attack", 24, WHITE, WIDTH/2, 10)
            self.exit_button.draw(self.game_surface)

        elif self.state == "USERNAME":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,128))
            self.game_surface.blit(overlay, (0,0))
            
            self.draw_text("Enter Username:", 48, WHITE, WIDTH/2, HEIGHT/3)
            pygame.draw.rect(self.game_surface, WHITE, (WIDTH/2 - 150, HEIGHT/2, 300, 50))
            self.draw_text(self.input_text, 48, BLACK, WIDTH/2, HEIGHT/2)
            self.draw_text("Press Enter to Confirm", 22, GRAY, WIDTH/2, HEIGHT * 0.75)

        elif self.state == "MENU":
            self.draw_text(TITLE, 64, RED, WIDTH/2, HEIGHT/4)
            self.draw_text(f"Welcome, {self.player.username}!", 32, BLACK, WIDTH/2, HEIGHT/2 - 40)
            self.draw_text(f"Coins: {self.player.coins}", 32, YELLOW, WIDTH/2, HEIGHT/2)
            self.draw_text("Team Banana Labs Studios", 16, GRAY, WIDTH - 100, HEIGHT - 20)
            
            for btn in self.menu_buttons:
                btn.draw(self.game_surface)

        elif self.state == "CPU_SELECT":
            self.draw_text("How many players (CPUs)?", 48, BLACK, WIDTH/2, HEIGHT/3)
            self.draw_text("(1-4)", 32, BLACK, WIDTH/2, HEIGHT/3 + 50)
            self.draw_text(self.cpu_count_text, 48, BLUE, WIDTH/2, HEIGHT/2)
            self.exit_button.draw(self.game_surface)
            
        elif self.state == "SHOP":
            self.draw_text("Weapon Shop", 48, BLACK, WIDTH/2, 50)
            self.draw_text(f"Your Coins: {self.player.coins}", 32, YELLOW, WIDTH/2, 80)
            
            for btn in self.shop_buttons:
                btn.draw(self.game_surface)
            self.exit_button.draw(self.game_surface)

        if self.message:
            self.draw_text(self.message, 36, RED, WIDTH/2, HEIGHT * 0.8)

        # Scale and blit game_surface to screen
        scale_w = self.screen_width / WIDTH
        scale_h = self.screen_height / HEIGHT
        scale = min(scale_w, scale_h)
        
        new_w = int(WIDTH * scale)
        new_h = int(HEIGHT * scale)
        
        scaled_surface = pygame.transform.scale(self.game_surface, (new_w, new_h))
        
        # Center on screen
        x = (self.screen_width - new_w) // 2
        y = (self.screen_height - new_h) // 2
        
        self.screen.fill(BLACK) # Fill black bars
        self.screen.blit(scaled_surface, (x, y))

        pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.run()
