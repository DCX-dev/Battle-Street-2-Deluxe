import pygame
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, font_size=32, bg_color=WHITE, text_color=BLACK, hover_color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont(FONT_NAME, font_size)
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.bg_color
        # Draw button shadow
        pygame.draw.rect(screen, BLACK, (self.rect.x + 2, self.rect.y + 2, self.rect.width, self.rect.height), border_radius=5)
        # Draw button body
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        # Draw border
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        # Original method, still here for backward compatibility or direct calls
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

    def is_clicked_custom(self, event, mouse_pos):
        # New method to check click with transformed mouse coordinates
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
             if self.rect.collidepoint(mouse_pos):
                return True
        return False
