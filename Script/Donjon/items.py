import os
import json
import path_config

class Item:
    def __init__(self, name, item_type, rarity, texture, **attributes):
        """Initialisation d'un objet avec son nom, son type, sa rareté, sa texture et ses caractéristiques supplémentaires."""
        self.name = name
        self.type = item_type  
        self.rarity = rarity  
        self.texture = texture
        self.attributes = attributes  

    def __repr__(self):
        """Affiche le nom de l'objet, sa rareté, ses caractéristiques et la texture."""
        attributes_str = ', '.join([f"{key}: {value}" for key, value in self.attributes.items()])
        return f"{self.name} ({self.rarity}) - {attributes_str} - Texture: {self.texture}"

class Items:
    def __init__(self, niveau):
        """Initialisation des items en fonction du niveau."""
        self.niveau = niveau  # Instance de Niveau pour obtenir le niveau actuel
        self.texture_dir = os.path.join(path_config.get_base_texture_path(), "Sprite/icon_items")
        self.items = self.load_items_for_level(self.niveau.level)

    def get_texture_path(self, filename):
        """Retourne le chemin complet vers une texture et vérifie si le fichier existe."""
        full_path = os.path.join(self.texture_dir, filename)
        if not os.path.exists(full_path):
            print(f"Erreur: Le fichier {filename} est introuvable à {full_path}")
        return full_path

    def load_items_for_level(self, level):
        """Charge les items spécifiques au niveau donné."""
        file_path = path_config.get_base_texture_path() + "data/items.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            level_str = str(level)
            if level_str in data:
                return [
                    Item(
                        item_data["name"],
                        item_data["type"],
                        item_data["rarity"],
                        self.get_texture_path(item_data["texture"]),
                        **item_data["attributes"]
                    )
                    for item_data in data[level_str]
                ]
            else:
                print(f"Aucun item trouvé pour le niveau {level}.")
                return []

        except FileNotFoundError:
            print(f"Erreur : le fichier {file_path} est introuvable.")
            return []

    def get_items(self):
        """Retourne la liste des items actuellement disponibles."""
        return self.items
