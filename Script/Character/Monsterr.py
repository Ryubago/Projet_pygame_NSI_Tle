import random
import pygame
import json
import path_config

class Monster:
    def __init__(self, x, y, monster_type, map_obj):
        self.x = x
        self.y = y
        self.monster_type = monster_type
        self.size = monster_type["size"]
        self.hp = monster_type["hp"]
        self.damage = monster_type["damage"]
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.map_width = map_obj.cols * map_obj.tile_size  
       
        self.image_left = pygame.image.load(path_config.get_base_texture_path() + monster_type["image_left"]).convert_alpha()
        self.image_right = pygame.image.load(path_config.get_base_texture_path() + monster_type["image_right"]).convert_alpha()
        
        self.image_left = pygame.transform.scale(self.image_left, (self.size, self.size))
        self.image_right = pygame.transform.scale(self.image_right, (self.size, self.size))
        
        self.direction = "left" if self.x > self.map_width // 2 else "right"

    def draw_monster(self, screen):
        self.direction = "left" if self.x > self.map_width // 2 else "right"
        if self.direction == "left":
            screen.blit(self.image_left, (self.x, self.y))
        else:
            screen.blit(self.image_right, (self.x, self.y))

    def take_damage(self, amount):
        """Reduit les la vie des monstres."""
        self.hp -= amount
        return self.hp <= 0 


class MonsterManager:
    def __init__(self, map_obj, niveau):
        self.map_obj = map_obj
        self.niveau = niveau  
        self.monsters = []

    def load_monster_types(self):
        """Charge les caractéristiques des monstres depuis un fichier JSON pour le niveau actuel."""
        file_path = path_config.get_base_texture_path() + "data/monstres.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            level_str = str(self.niveau.level)  # Convertir le niveau en chaîne pour correspondre aux clés du JSON
            if level_str in data:
                return data[level_str]  # Retourne les monstres pour le niveau actuel
            else:
                print(f"Aucun monstre trouvé pour le nive {self.niveau.level}")
                return {}

        except FileNotFoundError:
            print(f"Erreur : le fichier {file_path} est introuvable.")
            return {}

    def spawn_monsters(self):
        self.monsters.clear()
        # Charger les monstres du niveau actuel
        self.monster_types = self.load_monster_types()  # Recharger les types de monstres pour le niveau actuel
        
        rows = len(self.map_obj.layout)
        cols = len(self.map_obj.layout[0]) if rows > 0 else 0

        for row in range(rows):
            for col in range(cols):
                if self.map_obj.layout[row][col] == 2:  
                    # 60% de chance de tenter de faire apparaître un monstre
                    if random.random() < 0.6:
                        # Calculer la somme totale des probabilités pour les monstres disponibles
                        total_probability = sum(properties["probability"] for properties in self.monster_types.values())

                        # Générer un nombre aléatoire entre 0 et total_probability
                        rand_value = random.uniform(0, total_probability)
                        cumulative_probability = 0.0

                        # Parcourir les monstres et sélectionner en fonction de la probabilité cumulée
                        for monster_name, properties in self.monster_types.items():
                            cumulative_probability += properties["probability"]
                            if rand_value <= cumulative_probability:
                                x = col * self.map_obj.tile_size + (self.map_obj.tile_size - properties["size"]) // 2
                                y = row * self.map_obj.tile_size + (self.map_obj.tile_size - properties["size"]) // 2
                                monster = Monster(x, y, properties, self.map_obj)
                                self.monsters.append(monster)
                                break  

    def draw_monsters(self, screen):
        for monster in self.monsters:
            monster.draw_monster(screen)

    def check_collision_with_player(self, player):
        for monster in self.monsters:
            if player.rect.colliderect(monster.rect):
                return monster  
        return None 

    def remove_monster(self, monster):
        if monster in self.monsters:
            self.monsters.remove(monster)
