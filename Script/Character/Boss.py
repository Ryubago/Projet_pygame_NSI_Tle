import pygame
import random
import json
import path_config

class Boss:
    def __init__(self, x, y, boss_type, map_obj):
        self.x = x
        self.y = y
        self.boss_type = boss_type
        self.size = boss_type["size"]
        self.hp = boss_type["hp"]
        self.damage = boss_type["damage"]
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.map_width = map_obj.cols * map_obj.tile_size  

        # Charger les images du boss
        self.image_left = pygame.image.load(path_config.get_base_texture_path() + boss_type["image_left"]).convert_alpha()
        self.image_right = pygame.image.load(path_config.get_base_texture_path() + boss_type["image_right"]).convert_alpha()
        
        self.image_left = pygame.transform.scale(self.image_left, (self.size, self.size))
        self.image_right = pygame.transform.scale(self.image_right, (self.size, self.size))
        
        self.direction = "left" if self.x > self.map_width // 2 else "right"

    def draw_boss(self, screen):
        """Affiche le boss à sa position actuelle."""
        self.direction = "left" if self.x > self.map_width // 2 else "right"
        if self.direction == "left":
            screen.blit(self.image_left, (self.x, self.y))
        else:
            screen.blit(self.image_right, (self.x, self.y))

    def take_damage(self, amount):
        """Réduit les points de vie du boss."""
        self.hp -= amount
        return self.hp <= 0  # Retourne True si le boss est vaincu
class BossManager:
    def __init__(self, map_obj, niveau):
        self.map_obj = map_obj
        self.niveau = niveau  
        self.bosses = []

    def load_boss_types(self):
        """Charge les caractéristiques des boss depuis un fichier JSON en fonction du niveau."""
        file_path = path_config.get_base_texture_path() + "data/boss.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            level_str = str(self.niveau.level)  # Convertir le niveau en chaîne
            if level_str in data:
                return data[level_str]  # Retourne les boss pour le niveau actuel
            else:
                print(f"Aucun boss trouvé pour le niveau {self.niveau.level}")
                return {}

        except FileNotFoundError:
            print(f"Erreur : le fichier {file_path} est introuvable.")
            return {}

    def spawn_bosses(self):
        """Fait apparaître les boss sur les cases '5'."""
        self.bosses.clear()
        # Charger les boss du niveau actuel
        self.boss_types = self.load_boss_types()

        rows = len(self.map_obj.layout)
        cols = len(self.map_obj.layout[0]) if rows > 0 else 0

        for row in range(rows):
            for col in range(cols):
                if self.map_obj.layout[row][col] == 5:  
                    # Calculer la somme des probabilités pour les boss disponibles
                    total_probability = sum(properties["probability"] for properties in self.boss_types.values())

                    # Générer un nombre aléatoire entre 0 et total_probability
                    rand_value = random.uniform(0, total_probability)
                    cumulative_probability = 0.0

                    # Parcourir les boss et sélectionner en fonction de la probabilité cumulée
                    for boss_name, properties in self.boss_types.items():
                        cumulative_probability += properties["probability"]
                        if rand_value <= cumulative_probability:
                            x = col * self.map_obj.tile_size + (self.map_obj.tile_size - properties["size"]) // 2
                            y = row * self.map_obj.tile_size + (self.map_obj.tile_size - properties["size"]) // 2
                            boss = Boss(x, y, properties, self.map_obj)
                            self.bosses.append(boss)
                            break

    def draw_bosses(self, screen):
        """Affiche tous les boss."""
        for boss in self.bosses:
            boss.draw_boss(screen)

    def check_collision_with_player(self, player):
        """Vérifie si le joueur entre en collision avec un boss."""
        for boss in self.bosses:
            if player.rect.colliderect(boss.rect):
                return boss  
        return None 

    def remove_boss(self, boss):
        """Supprime un boss vaincu."""
        if boss in self.bosses:
            self.bosses.remove(boss)
