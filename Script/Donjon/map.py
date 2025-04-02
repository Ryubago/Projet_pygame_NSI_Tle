import pygame
from .Generate import Generation
from Character.Monsterr import MonsterManager
import path_config

class Map:
    def __init__(self, screen, niveau):
        self.screen = screen
        self.niveau = niveau  # Instance de Niveau pour accéder au niveau actuel
        self.monster_manager = MonsterManager(self, self.niveau)
        self.tile_size = 50
        self.rows = 12
        self.cols = 16
        self.font = pygame.font.SysFont(None, 24)
        
        self.generation = Generation()
        self.layout = self.generation.get_random_room(niveau)
        
        # Appeler load_textures avec le niveau actuel
        self.load_textures()
        
        self.wall_texture_map = []  # Map to store a specific texture for each wall tile
        self.generate_new_room()  #intialize la premiere salle
        self.room_changed = False  # Flag pour savoir si la salle a changé

    def load_textures(self):
        """Charge les textures de mur et de sol en fonction du niveau actuel."""
        level = self.niveau.level  # Obtenir le niveau actuel
        base_texture_path = path_config.get_base_texture_path() + f"Sprite/map/map{level}/"
        
        # Charger les textures spécifiques pour chaque type de mur en fonction du niveau
        self.wall_textures = {
            "mur1": pygame.image.load(base_texture_path + "mur1.png").convert(),
            "mur2": pygame.image.load(base_texture_path + "mur2.png").convert(),
            "mur3": pygame.image.load(base_texture_path + "mur3.png").convert(),
            "mur4": pygame.image.load(base_texture_path + "mur4.png").convert(),
            "mur5": pygame.image.load(base_texture_path + "mur5.png").convert(),
            "mur6": pygame.image.load(base_texture_path + "mur6.png").convert(),
            "mur7": pygame.image.load(base_texture_path + "mur7.png").convert(),
            "mur8": pygame.image.load(base_texture_path + "mur8.png").convert(),
            "mur9": pygame.image.load(base_texture_path + "mur9.png").convert(),
        }

        # Redimensionner les textures des murs pour qu'elles correspondent à la taille des tuiles
        for key, texture in self.wall_textures.items():
            self.wall_textures[key] = pygame.transform.scale(texture, (self.tile_size, self.tile_size))

        # Charger la texture du sol en fonction du niveau
        floor_texture_path = base_texture_path + "sol1.png"
        self.floor_texture = pygame.image.load(floor_texture_path).convert()
        self.floor_texture = pygame.transform.scale(self.floor_texture, (self.tile_size, self.tile_size))

    def generate_new_room(self):
        """Génère une nouvelle salle aléatoire et attribue des textures de mur spécifiques."""
        # Si le niveau a changé, recharger les textures pour le nouveau niveau
        self.load_textures()
        level = level = self.niveau.level
        self.layout = self.generation.get_random_room(level)
        self.wall_texture_map = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        for row in range(self.rows):
            for col in range(self.cols):
                if self.is_wall(row, col):
                    # Attribuer la texture de mur en fonction de la position
                    if row == 0 and col == 0:
                        texture = self.wall_textures["mur8"]  # Coin supérieur gauche
                    elif row == 0 and col == self.cols - 1:
                        texture = self.wall_textures["mur9"]  # Coin supérieur droit
                    elif row == self.rows - 1 and col == 0:
                        texture = self.wall_textures["mur7"]  # Coin inférieur gauche
                    elif row == self.rows - 1 and col == self.cols - 1:
                        texture = self.wall_textures["mur6"]  # Coin inférieur droit
                    elif row == 0:
                        texture = self.wall_textures["mur5"]  # Bord supérieur, sans coins
                    elif row == self.rows - 1:
                        texture = self.wall_textures["mur4"]  # Bord inférieur, sans coins
                    elif col == 0:
                        texture = self.wall_textures["mur2"]  # Bord gauche, sans coins
                    elif col == self.cols - 1:
                        texture = self.wall_textures["mur3"]  # Bord droit, sans coins
                    else:
                        texture = self.wall_textures["mur1"]  # Murs intérieurs
                    
                    self.wall_texture_map[row][col] = texture
        
        self.room_changed = True  # Indiquer que la salle a changé

    def draw_room(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.draw_tile(row, col)

    def draw_tile(self, row, col):
        x = col * self.tile_size
        y = row * self.tile_size

        if self.is_wall(row, col):
            # Utiliser la texture de mur présélectionnée pour cette tuile
            wall_texture = self.wall_texture_map[row][col]
            self.screen.blit(wall_texture, (x, y))
        else:
            self.screen.blit(self.floor_texture, (x, y))

    def is_wall(self, row, col):
        return self.layout[row][col] == 1

    def check_room_exit(self, player):
        """Vérifie si le joueur est à une extrémité de la salle et génère une nouvelle salle si nécessaire."""
        room_width = self.cols * self.tile_size
        room_height = self.rows * self.tile_size

        if player.rect.right >= room_width or player.rect.left <= 0 or player.rect.bottom >= room_height or player.rect.top <= 0:
            # Si le joueur atteint une extrémité, générer une nouvelle salle
            self.generate_new_room()
            self.room_changed = True  # La salle a changé
