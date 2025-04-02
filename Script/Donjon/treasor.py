import random
from Donjon.items import Items
import pygame
import path_config
class Chest:
    def __init__(self, chest_type, x, y, tile_size, niveau):
        """Initialisation d'un coffre avec son type, sa position, et la taille des tuiles."""
        self.chest_type = chest_type
        self.niveau = niveau
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.opened = False
        self.items = self.generate_items()  # Liste d'items dans le coffre
        base_texture_path = path_config.get_base_texture_path() + "Sprite/chest/"
        # Charger l'image du coffre selon son type
        self.images = {
                "classique": pygame.image.load(f"{base_texture_path}common.png"),
                "super": pygame.image.load(f"{base_texture_path}super.png"),
                "mega": pygame.image.load(f"{base_texture_path}mega.png"),
                "legende": pygame.image.load(f"{base_texture_path}legend.png"),
            }
        self.image = pygame.transform.scale(self.images[chest_type], (self.tile_size, self.tile_size))

    def generate_items(self):
        """Génère un nombre aléatoire d'items dans le coffre, avec des probabilités de rareté spécifiques."""
        items = Items(self.niveau)  # Instance de la classe Items pour accéder aux items du niveau actuel
        num_items = random.randint(1, 3)  # Entre 1 et 3 items

        # Charger les items disponibles pour le niveau actuel
        items_for_level = items.get_items()  # Nouvelle méthode de la classe Items pour obtenir les items du niveau

        # Filtrer les items par rareté en fonction du type de coffre
        rarity_probabilities = {
            "classique": [("commun", 0.8), ("rare", 0.15), ("épique", 0.05)],
            "super": [("commun", 0.5), ("rare", 0.4), ("épique", 0.09), ("légendaire", 0.01)],
            "mega": [("commun", 0.3), ("rare", 0.3), ("épique", 0.35), ("légendaire", 0.05)],
            "legende": [("commun", 0.05), ("rare", 0.1), ("épique", 0.65), ("légendaire", 0.2)]
        }

        selected_items = []

        for _ in range(num_items):
            # Choisir une rareté en fonction des probabilités
            rarities, probabilities = zip(*rarity_probabilities[self.chest_type])
            chosen_rarity = random.choices(rarities, probabilities)[0]

            # Filtrer les items par la rareté sélectionnée
            items_in_rarity = [item for item in items_for_level if item.rarity == chosen_rarity]

            if items_in_rarity:
                chosen_item = random.choice(items_in_rarity)
                selected_items.append(chosen_item)

        return selected_items


    def draw(self, screen):
        """Dessine le coffre sur l'écran."""
        if not self.opened:
            screen.blit(self.image, (self.x, self.y))

class ChestManager:
    def __init__(self, map_layout, tile_size, niveau):
        """Gestion des coffres sur la carte."""
        self.map_layout = map_layout
        self.niveau = niveau
        self.tile_size = tile_size  
        self.chests = []
        self.font = pygame.font.SysFont(None, 24)  
        self.spawn_chests()

    def update_layout(self, new_layout):
        """Met à jour la disposition de la salle et génère de nouveaux coffres."""
        self.map_layout = new_layout  
        self.clear_chests()  
        self.spawn_chests()  

    def spawn_chests(self):
        """Génère des coffres aléatoirement à des emplacements spécifiques (où il y a des '3' sur la carte)."""
        self.clear_chests() 
        rows = len(self.map_layout)
        cols = len(self.map_layout[0]) if rows > 0 else 0

        for row in range(rows):
            for col in range(cols):
                if self.map_layout[row][col] == 3:  
                    if random.random() < 0.5:  # 50% de chances qu'un coffre apparaisse
                        chest_type = self.get_random_chest_type()  
                        x = col * self.tile_size
                        y = row * self.tile_size
                        chest = Chest(chest_type, x, y, self.tile_size, self.niveau)
                        self.chests.append(chest)

    def get_random_chest_type(self):
        """Retourne un type de coffre basé sur une probabilité."""
        chest_probabilities = {
            "classique": 0.7,  # 70% de chance
            "super": 0.18,  # 18% de chance
            "mega": 0.08,   # 8% de chance
            "legende": 0.04  # 4% de chance
        }
        return random.choices(
            population=list(chest_probabilities.keys()),
            weights=list(chest_probabilities.values()),
            k=1
        )[0]

    def draw_chests(self, screen, player_rect):
        """Dessine tous les coffres sur l'écran et affiche un texte si le joueur est proche."""
        for chest in self.chests:
            chest.draw(screen)

            # Vérifier si le joueur est à proximité du coffre
            chest_rect = pygame.Rect(chest.x, chest.y, chest.tile_size, chest.tile_size)
            if player_rect.colliderect(chest_rect.inflate(30, 30)): 
                self.show_open_text(screen, chest)

    def show_open_text(self, screen, chest):
        """Affiche un texte au-dessus du coffre pour indiquer qu'il peut être ouvert."""
        text_surface = self.font.render("[O] pour ouvrir", True, (255, 255, 255))  
        text_rect = text_surface.get_rect(center=(chest.x + chest.tile_size // 2, chest.y - 20))  
        screen.blit(text_surface, text_rect)
        

    def clear_chests(self):
        """Vide la liste des coffres pour la nouvelle salle."""
        self.chests = []

    def check_collision_with_player(self, player_rect):
        """Vérifie si le joueur entre en collision avec un coffre."""
        for chest in self.chests:
            chest_rect = pygame.Rect(chest.x, chest.y, chest.tile_size, chest.tile_size)
            if player_rect.colliderect(chest_rect):
                return True
        return False
