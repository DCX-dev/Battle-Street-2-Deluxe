import pygame
import random
from settings import *

class Player:
    def __init__(self, username="Player", is_cpu=False):
        self.username = username
        self.is_cpu = is_cpu
        self.coins = STARTING_COINS
        self.hp = 80 if is_cpu else 100
        self.max_hp = 80 if is_cpu else 100
        
        # New inventory system matching original
        self.inventory = ["Fist"] 
        self.current_weapon_name = "Fist"
        
        # Physics
        self.rect = pygame.Rect(100, 300, 40, 60) # Original size was 40x60
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.facing_right = True
        self.speed = 5
        
        # Combat
        self.last_attack_time = 0
        self.attack_cooldown = 0
        self.is_attacking = False
        
        # Original Game Stats
        self.role = "Fighter"
        self.vehicle = "None"
        self.hat = None
        
        # Appearance
        if self.is_cpu:
            self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        else:
            self.color = BLUE

    @property
    def current_weapon(self):
        return WEAPONS_DATA[self.current_weapon_name]

    def equip_weapon(self, weapon_name):
        if weapon_name in self.inventory:
            self.current_weapon_name = weapon_name

    def buy_weapon(self, weapon_name):
        # Handle buying logic in Game class or check cost here
        weapon = WEAPONS_DATA.get(weapon_name)
        if not weapon: return False
        
        if self.coins >= weapon['cost'] and weapon_name not in self.inventory:
            self.coins -= weapon['cost']
            self.inventory.append(weapon_name)
            return True
        return False

    def take_damage(self, amount):
        # Apply defense from original game logic if needed
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self):
        self.hp = self.max_hp

    def reset_position(self):
        self.rect.x = 100
        self.rect.y = 300
        self.hp = self.max_hp
        self.is_attacking = False
        self.vel_y = 0

    def draw(self, screen, weapon_textures=None):
        # Draw shadows
        pygame.draw.ellipse(screen, (0, 0, 0, 100), (self.rect.x, self.rect.bottom - 5, self.rect.width, 10))
        
        # Body
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        # Head
        head_radius = 20
        head_center = (self.rect.centerx, self.rect.top - head_radius + 5)
        pygame.draw.circle(screen, LIGHT_BLUE if self.is_cpu else WHITE, head_center, head_radius)
        pygame.draw.circle(screen, BLACK, head_center, head_radius, 2)
        
        # Eyes (Directional)
        eye_color = BLACK
        look_offset = 3 if self.facing_right else -3
        pygame.draw.circle(screen, eye_color, (head_center[0] - 7 + look_offset, head_center[1] - 2), 3)
        pygame.draw.circle(screen, eye_color, (head_center[0] + 7 + look_offset, head_center[1] - 2), 3)
        
        # Mouth (simple smile if high HP, straight if low)
        if self.hp > 50:
            pygame.draw.arc(screen, BLACK, (head_center[0] - 10, head_center[1], 20, 10), 3.14, 0, 2)
        else:
             pygame.draw.line(screen, BLACK, (head_center[0] - 5, head_center[1] + 10), (head_center[0] + 5, head_center[1] + 10), 2)

        # Arms
        arm_start_y = self.rect.top + 20
        
        # Weapon Handling
        weapon_img = None
        if weapon_textures and self.current_weapon_name in weapon_textures:
            weapon_img = weapon_textures[self.current_weapon_name]
        
        hand_pos = (self.rect.right + 5 if self.facing_right else self.rect.left - 5, arm_start_y + 15)
        
        if self.facing_right:
            # Right Arm (Holding Weapon)
            pygame.draw.line(screen, BLACK, (self.rect.right - 5, arm_start_y), hand_pos, 4)
            if weapon_img:
                # Rotate weapon if attacking?
                # For now just draw it
                img_rect = weapon_img.get_rect(center=hand_pos)
                if self.is_attacking:
                    # Swing effect
                    img_rect.x += 10
                    img_rect.y += 5
                screen.blit(weapon_img, img_rect)
            else:
                 # Default rect weapon
                 pygame.draw.line(screen, GRAY, hand_pos, (hand_pos[0]+20, hand_pos[1]), 5)

            # Left Arm
            pygame.draw.line(screen, BLACK, (self.rect.left + 5, arm_start_y), (self.rect.left - 10, arm_start_y + 10), 4)

        else:
             # Left Arm (Holding Weapon)
            pygame.draw.line(screen, BLACK, (self.rect.left + 5, arm_start_y), hand_pos, 4)
            if weapon_img:
                flipped_img = pygame.transform.flip(weapon_img, True, False)
                img_rect = flipped_img.get_rect(center=hand_pos)
                if self.is_attacking:
                     img_rect.x -= 10
                screen.blit(flipped_img, img_rect)
            else:
                 pygame.draw.line(screen, GRAY, hand_pos, (hand_pos[0]-20, hand_pos[1]), 5)
            
            # Right Arm
            pygame.draw.line(screen, BLACK, (self.rect.right - 5, arm_start_y), (self.rect.right + 10, arm_start_y + 10), 4)

        # Username
        font = pygame.font.SysFont(FONT_NAME, 20)
        text_surf = font.render(self.username, True, BLACK)
        text_rect = text_surf.get_rect(midbottom=(self.rect.centerx, self.rect.top - 45))
        screen.blit(text_surf, text_rect)
        
        # HP Bar
        bar_width = 50
        bar_height = 5
        fill = (self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, RED, (self.rect.centerx - bar_width/2, self.rect.top - 40, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.rect.centerx - bar_width/2, self.rect.top - 40, fill, bar_height))
