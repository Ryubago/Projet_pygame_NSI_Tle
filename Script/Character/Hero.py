import pygame
import path_config 
from Donjon.items import Item

class Player:
    def __init__(self, x, y, size, map_obj, inventory, scale_factor=0.9):
        self.x = x
        self.y = y
        self.size = size
        self.speed = 1.6
        self.map_obj = map_obj
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.hp = 100
        self.max_hp = 100
        self.inventory = inventory
        self.move_timer = 0
        self.move_interval = 0.001
        self.scale_factor = scale_factor

        # Obtenez le chemin de base des textures du joueur
        base_texture_path = path_config.get_base_texture_path() + "Sprite/player/"

        # Chargement des animations du joueur avec le chemin de base
        self.animations = {
            'up': [pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_up1.png"), 
                                          (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                   pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_up2.png"), 
                                          (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                   pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_up3.png"), 
                                          (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                   pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_up4.png"), 
                                          (int(self.size * self.scale_factor), int(self.size * self.scale_factor)))],
            'down': [pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_down1.png"), 
                                            (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                     pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_down2.png"), 
                                            (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                     pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_down3.png"), 
                                            (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                     pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_down4.png"), 
                                            (int(self.size * self.scale_factor), int(self.size * self.scale_factor)))],
            'left': [pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_left1.png"), 
                                            (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                     pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_left2.png"), 
                                            (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                     pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_left3.png"), 
                                            (int(self.size * self.scale_factor), int(self.size * self.scale_factor)))],
            'right': [pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_right1.png"), 
                                             (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                      pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_right2.png"), 
                                             (int(self.size * self.scale_factor), int(self.size * self.scale_factor))),
                      pygame.transform.scale(pygame.image.load(f"{base_texture_path}walk_right3.png"), 
                                             (int(self.size * self.scale_factor), int(self.size * self.scale_factor)))],
        }

        self.current_animation = 'down'  
        self.current_frame = 0
        self.animation_speed = 0.1  
        self.animation_counter = 0
        self.animation_timer = 0  # Timer pour la mise à jour de l'animation
    @property
    def position(self):
        """Retourne la position actuelle du joueur en termes de coordonnées de grille."""
        return (self.rect.x // self.map_obj.tile_size, self.rect.y // self.map_obj.tile_size)

    @property
    def weapon1(self):
        weapon = self.inventory.items.get(0)
        return weapon if isinstance(weapon, Item) else None

    @property
    def weapon2(self):
        weapon = self.inventory.items.get(1)
        return weapon if isinstance(weapon, Item) else None
    @property
    def shield1(self):
        weapon = self.inventory.items.get(2)
        return weapon if isinstance(weapon, Item) else None
    @property
    def sort1(self):
        weapon = self.inventory.items.get(3)
        return weapon if isinstance(weapon, Item) else None
    @property
    def equipement1(self):
        weapon = self.inventory.items.get(4)
        return weapon if isinstance(weapon, Item) else None
    @property
    def object1(self):
        return self.inventory.items.get(5)  

    @property
    def object2(self):
        return self.inventory.items.get(6)  
    @property
    def object3(self):
        return self.inventory.items.get(7)  


    def draw_player(self, screen):
        # Obtenir l'image actuelle de l'animation
        current_image = self.animations[self.current_animation][int(self.current_frame)]
        # Dessiner l'image actuelle du joueur
        screen.blit(current_image, self.rect.topleft)

    def update_animation(self, delta_time):
        # Met à jour le compteur de frames
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])
            self.animation_timer = 0

        # S'assurer que current_frame est dans les limites
        self.current_frame = min(self.current_frame, len(self.animations[self.current_animation]) - 1)


    def can_move(self, new_rect, monster_manager, chest_manager):
        # Calculer les positions des coins du joueur en termes de grille
        top_left = (new_rect.y // self.map_obj.tile_size, new_rect.x // self.map_obj.tile_size)
        top_right = (new_rect.y // self.map_obj.tile_size, (new_rect.x + self.rect.width) // self.map_obj.tile_size)
        bottom_left = ((new_rect.y + self.rect.height) // self.map_obj.tile_size, new_rect.x // self.map_obj.tile_size)
        bottom_right = ((new_rect.y + self.rect.height) // self.map_obj.tile_size, (new_rect.x + self.rect.width) // self.map_obj.tile_size)
    
        # Vérification que les coordonnées ne sortent pas des limites de la grille
        def within_bounds(coords):
            row, col = coords
            return 0 <= row < self.map_obj.rows and 0 <= col < self.map_obj.cols
    
        if within_bounds(top_left) and within_bounds(top_right) and within_bounds(bottom_left) and within_bounds(bottom_right):
            # Vérifie s'il y a un mur
            if not (self.map_obj.is_wall(*top_left) or
                    self.map_obj.is_wall(*top_right) or
                    self.map_obj.is_wall(*bottom_left) or
                    self.map_obj.is_wall(*bottom_right)):
                # Vérifie les collisions avec les monstres
                if monster_manager.check_collision_with_player(self):
                    return False  # Bloque le mouvement si collision avec un monstre
                # Vérifie les collisions avec les coffres
                if chest_manager.check_collision_with_player(new_rect):
                    return False  # Bloque le mouvement si collision avec un coffre
                return True  # Le mouvement est possible si pas de mur, pas de monstre et pas de coffre
        return False  # Empêche le mouvement si en dehors des limites
    
    def move_player(self, direction, delta_time, monster_manager, chest_manager):
        # Mettre à jour le timer de mouvement
        self.move_timer += delta_time

        # Déplacer le joueur si le timer a dépassé l'intervalle de mouvement
        if self.move_timer >= self.move_interval:
            self.move_timer = 0  # Réinitialiser le timer

            # Copie du rectangle actuel du joueur
            new_rect = self.rect.copy()

            # Déplacement selon la direction 
            if direction == 'up':
                new_rect.y -= self.speed
                self.current_animation = 'up'
            elif direction == 'down':
                new_rect.y += self.speed
                self.current_animation = 'down'
            elif direction == 'left':
                new_rect.x -= self.speed
                self.current_animation = 'left'
            elif direction == 'right':
                new_rect.x += self.speed
                self.current_animation = 'right'

            # Si le déplacement est possible (pas de mur, pas de monstre, pas de coffre, etc.)
            if self.can_move(new_rect, monster_manager, chest_manager):
                self.rect = new_rect

            # Mettre à jour l'animation
            self.update_animation(delta_time)
        
            # Vérification si le joueur est à une extrémité de la salle pour générer une nouvelle salle
            self.check_room_exit()

    def check_room_exit(self):
        """Vérifie si le joueur atteint les limites de la salle et génère une nouvelle salle en le plaçant juste après l'entrée du bas."""
        room_width = self.map_obj.cols * self.map_obj.tile_size
        room_height = self.map_obj.rows * self.map_obj.tile_size
        margin = self.speed * 2  # Marge pour détecter la sortie des bords


        if self.rect.right >= room_width - margin:  # Bord droit
            self.map_obj.generate_new_room()
            self.rect.x = 353  # Centrer horizontalement
            self.rect.y = room_height - self.map_obj.tile_size  # Position juste après l'entrée du bas

        elif self.rect.left <= 0 + margin:  # Bord gauche
            self.map_obj.generate_new_room()
            self.rect.x = 353  # Centrer horizontalement
            self.rect.y = room_height - self.map_obj.tile_size  # Position juste après l'entrée du bas

        elif self.rect.top <= 0 + margin:  # Bord haut
            self.map_obj.generate_new_room()
            self.rect.x = 353  # Centrer horizontalement
            self.rect.y = room_height - self.map_obj.tile_size  # Position juste après l'entrée du bas
