import pygame
import sys
import path_config


# Initialiser Pygame
pygame.init()
# Importer les modules
from GameMachine.menu import Menu  # Importe le script Menu
from Game import Game  # Importe la classe Game depuis Game.py


# Définir les dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("δειτα Tower ")

# Définir icône du jeu
base_texture_path = path_config.get_base_texture_path() + "Sprite/"
pygame_icon = pygame.image.load(f"{base_texture_path}DTicon.png")
pygame.display.set_icon(pygame_icon)

def main_menu():
    # Crée une instance de Menu
    menu = Menu(screen)
    running = True
    while running:
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                menu.check_click(event.pos)

                # Si "Jouer" a été cliqué
                if menu.start_game_called:
                    # Crée une instance du jeu et lance-le  
                    game = Game(screen)
                    game.run()
                    running = False  # Ferme le menu après avoir lancé le jeu

        # Dessiner le menu
        menu.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()
# Dans le main_menu ou après la boucle de jeu
if __name__ == "__main__":
    while True:
        result = main_menu()
        if result == "retry": 
            main_menu()
        else:
            break

