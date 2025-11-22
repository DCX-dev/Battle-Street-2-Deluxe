import pygame
import math
import random
from settings import *

class Platform:
    def __init__(self, x, y, width, height, color=(100, 100, 100)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, screen):
        # Draw platform with 3D effect
        pygame.draw.rect(screen, self.color, self.rect)
        # Top highlight
        pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in self.color), 
                        (self.x, self.y, self.width, 3))
        # Bottom shadow
        pygame.draw.rect(screen, tuple(max(c - 30, 0) for c in self.color), 
                        (self.x, self.y + self.height - 3, self.width, 3))
        # Side shadow
        pygame.draw.rect(screen, tuple(max(c - 20, 0) for c in self.color), 
                        (self.x + self.width - 3, self.y, 3, self.height))
    
    def check_collision(self, player, player_vy):
        """Check if player is landing on this platform"""
        # Player must be falling (velocity_y > 0)
        if player_vy <= 0:
            return False
            
        # Check if player is above and overlapping horizontally
        player_bottom = player.rect.bottom
        player_left = player.rect.left
        player_right = player.rect.right
        
        # Check horizontal overlap
        if player_right < self.x or player_left > self.x + self.width:
            return False
            
        # Check if player is landing on platform (from above)
        # We check previous position or just a small range
        if player_bottom >= self.y and player_bottom <= self.y + self.height + abs(player_vy) + 5:
            return True
            
        return False

class Collectible:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type  # "coin", "health", "speed", "damage"
        self.size = 20
        self.lifetime = 600  # 10 seconds at 60 FPS
        self.bounce_offset = 0
        self.bounce_speed = 0.1
        self.rect = pygame.Rect(x - self.size, y - self.size, self.size * 2, self.size * 2)
        
    def update(self):
        self.lifetime -= 1
        self.bounce_offset = math.sin(pygame.time.get_ticks() * self.bounce_speed * 0.01) * 5
        self.rect.y = self.y + self.bounce_offset
        return self.lifetime > 0
        
    def draw(self, screen):
        y = self.y + self.bounce_offset
        if self.type == "coin":
            # Draw coin
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(y)), self.size)
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(y)), self.size - 5)
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(y)), self.size - 8)
        elif self.type == "health":
            # Draw health pack
            pygame.draw.circle(screen, WHITE, (int(self.x), int(y)), self.size)
            pygame.draw.circle(screen, RED, (int(self.x), int(y)), self.size - 3)
            # Cross
            pygame.draw.line(screen, WHITE, (self.x - 8, y), (self.x + 8, y), 3)
            pygame.draw.line(screen, WHITE, (self.x, y - 8), (self.x, y + 8), 3)
        elif self.type == "speed":
            # Draw speed boost
            pygame.draw.circle(screen, CYAN, (int(self.x), int(y)), self.size)
            pygame.draw.polygon(screen, WHITE, [
                (self.x - 5, y + 5),
                (self.x + 10, y),
                (self.x - 5, y - 5)
            ])
        elif self.type == "damage":
            # Draw damage boost
            pygame.draw.circle(screen, (255, 100, 100), (int(self.x), int(y)), self.size)
            pygame.draw.polygon(screen, WHITE, [
                (self.x, y - 8),
                (self.x + 8, y + 8),
                (self.x - 8, y + 8)
            ])
            
    def check_collision(self, player):
        return self.rect.colliderect(player.rect)

class ExplosionParticle:
    """Cartoon explosion particle for visual effects"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.base_color = color
        self.particles = []
        # Create particles in a burst pattern
        for i in range(15):
            angle = (i / 15) * 2 * math.pi
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(3, 8),
                'life': random.randint(20, 40),
                'max_life': 40
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
        return len(self.particles) > 0  # Return True if still alive
    
    def draw(self, screen):
        for particle in self.particles:
            # Fade out as life decreases
            life_ratio = particle['life'] / particle['max_life']
            size = int(particle['size'] * life_ratio)
            if size > 0:
                # Create colorful cartoon explosion with multiple colors
                colors = [self.base_color, YELLOW, ORANGE, RED, WHITE]
                color_idx = int((1 - life_ratio) * (len(colors) - 1))
                color = colors[min(color_idx, len(colors) - 1)]
                pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), size)

class Projectile:
    def __init__(self, x, y, vx, vy, weapon_name, owner):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.weapon_name = weapon_name
        self.data = WEAPONS_DATA[weapon_name]
        self.owner = owner
        self.radius = 5
        self.color = self.data['color']
        self.rect = pygame.Rect(x, y, 10, 10)
        self.life = 100
        
        # Gravity for grenades
        self.gravity = 0.5 if self.data.get('explosion') else 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.rect.x = self.x
        self.rect.y = self.y
        self.life -= 1
        
        # Check bounds
        if self.y > HEIGHT or self.x < 0 or self.x > WIDTH:
            self.life = 0
            
        return self.life > 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

