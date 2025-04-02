import pygame
import path_config

class Portal:
    def __init__(self, x, y, tile_size):
        """Initialisation du portail avec la position et la taille de la tile."""
        self.x = x
        self.y = y
        self.tile_size = tile_size
        # Charger l'image du portail
        image_path = path_config.get_base_texture_path() + "Sprite/porte.png"
        self.image = pygame.image.load(image_path).convert_alpha()
        # Redimensionner l'image à 100x100
        self.image = pygame.transform.scale(self.image, (100, 100))
        
        self.x -= 25  # Décaler pour centrer l'image horizontalement (100 / 2)

    def draw(self, screen):
        """Affiche le portail à la position donnée."""
        screen.blit(self.image, (self.x, self.y))

    def check_collision_with_player(self, player):
        """Vérifie si le joueur entre en collision avec le portail."""
        portal_rect = pygame.Rect(self.x, self.y, 100, 100)  # Crée un rectangle pour le portail
        return portal_rect.colliderect(player.rect)  # Vérifie si le rectangle du portail intersecte le rectangle du joueur


class PortalManager:
    def __init__(self, map_layout, tile_size):
        """Gestion des portails sur la carte."""
        self.map_layout = map_layout
        self.tile_size = tile_size
        self.portals = []  
        self.spawn_portals()

    def update_layout(self, new_layout):
        """Met à jour la disposition de la salle et génère de nouveaux portails."""
        self.map_layout = new_layout
        self.clear_portals()
        self.spawn_portals()

    def spawn_portals(self):
        """Génère des portails à des emplacements spécifiques (où il y a des '4' sur la carte)."""
        self.clear_portals()
        rows = len(self.map_layout)
        cols = len(self.map_layout[0]) if rows > 0 else 0

        for row in range(rows):
            for col in range(cols):
                if self.map_layout[row][col] == 4:  # Le portail apparait sur les cases '4'
                    x = col * self.tile_size
                    y = row * self.tile_size
                    self.portals.append(Portal(x, y, self.tile_size))

    def clear_portals(self):
        """Supprime tous les portails existants."""
        self.portals = []

    def check_collisions_with_player(self, player):
        """Vérifie si le joueur entre en collision avec l'un des portails."""
        for portal in self.portals:
            if portal.check_collision_with_player(player):
                return portal  # Retourne le portail en collision avec le joueur
        return None  # Si aucune collision n'est détectée

    def draw(self, screen):
        """Dessine tous les portails présents."""
        for portal in self.portals:
            portal.draw(screen)
