import pygame
import sys
import path_config

WHITE = (230, 230, 235)
TEXT = (255, 255, 255)
TITLE = (0, 0, 0)
BUTTON_COLOR = (100, 195, 160)
BUTTON_HOVER_COLOR = (80, 150, 190)
WIDTH, HEIGHT = 800, 600
pygame.font.init()

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 50)
        self.title_font = pygame.font.SysFont('Power Red and Green', 130)
        self.base_texture_path = path_config.get_base_texture_path()
        self.start_game_called = False  # Variable pour indiquer si "Jouer" a été cliqué
        self.buttons = [
            {"text": "Jouer", "pos": (WIDTH // 2, HEIGHT // 2), "action": self.start_game},
            {"text": "Options", "pos": (WIDTH // 2, HEIGHT // 1.325), "action": self.show_options},
            {"text": "Quitter", "pos": (WIDTH // 2, HEIGHT // 1.6), "action": self.quit_game}
        ]
        # 25/03/2025
        # importer musique du menu
    def load_music(self):
        pygame.mixer.music.load(self.base_texture_path + "Music/musique_menu.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()

    def draw(self):
        self.screen.fill(WHITE)

        # importer l'arrière plan
        background = pygame.image.load(self.base_texture_path  + "Sprite/background_menu.png")
        background = background.convert()

        # Redimensionner l'image en fonction de la taille de la fenêtre
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))

        # appliquer l'arrière plan
        self.screen.blit(background, (0, 0))

        # ajout d'un encart pour le titre
        title_banner = pygame.image.load(self.base_texture_path  + "Sprite/title_banner.png")
        title_banner = title_banner.convert()
        title_banner = pygame.transform.scale(title_banner, (WIDTH, 150))
        self.screen.blit(title_banner, (0, 50))

        # affichage d'un titre
        title_text = self.title_font.render("Delta Tower", True, TITLE)
        title_position = (125, 70)
        self.screen.blit(title_text, title_position)

        for button in self.buttons:
            mouse_pos = pygame.mouse.get_pos()
            text_surface = self.small_font.render(button["text"], True, TEXT)
            text_rect = text_surface.get_rect(center=button["pos"])
            button_rect = pygame.Rect(text_rect.left - 20, text_rect.top - 10, text_rect.width + 40, text_rect.height + 20)
            
            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR, button_rect, border_radius=14)
            else:
                pygame.draw.rect(self.screen, BUTTON_COLOR, button_rect, border_radius=14)
        
            self.screen.blit(text_surface, text_rect)

        # mettre a jour l'écran
        pygame.display.flip()

    def check_click(self, pos):
        for button in self.buttons:
            text_surface = self.small_font.render(button["text"], True, WHITE)
            text_rect = text_surface.get_rect(center=button["pos"])
            button_rect = pygame.Rect(text_rect.left - 20, text_rect.top - 10, text_rect.width + 40, text_rect.height + 20)
            if button_rect.collidepoint(pos):
                button["action"]()

    def start_game(self):
        self.start_game_called = True  # Change la valeur pour indiquer que "Jouer" a été cliqué
        self.stop_music()

    def show_options(self):
        print("Affichage des options...")

    def quit_game(self):
        pygame.quit()
        sys.exit()
