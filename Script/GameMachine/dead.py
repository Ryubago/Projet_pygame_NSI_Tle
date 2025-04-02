import pygame
import sys

class DeadScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 40)
        
        # Définition des couleurs
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.button_color = (192, 0, 0)
        self.hover_color = (255, 0, 0)
        
        # Bouton "Recommencer"
        self.retry_button = pygame.Rect(300, 250, 200, 50)
        # Bouton "Quitter"
        self.quit_button = pygame.Rect(300, 350, 200, 50)

    def draw(self):
        self.screen.fill(self.bg_color)

        # Dessine les boutons avec les labels
        pygame.draw.rect(self.screen, self.button_color, self.retry_button)
        pygame.draw.rect(self.screen, self.button_color, self.quit_button)

        # Ajoute du texte sur les boutons
        retry_text = self.font.render("Recommencer", True, self.text_color)
        quit_text = self.font.render("Quitter", True, self.text_color)
        self.screen.blit(retry_text, (self.retry_button.x + 6, self.retry_button.y + 10))
        self.screen.blit(quit_text, (self.quit_button.x + 50, self.quit_button.y + 10))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.retry_button.collidepoint(event.pos):
                    return "retry"
                elif self.quit_button.collidepoint(event.pos):
                    return "quit"
        return None
