import pygame

class Inventory:
    def __init__(self):
        # Initialisation de l'inventaire avec 8 slots vides
        self.slots = [None] * 8

        # Noms des slots pour indiquer à quoi ils correspondent
        self.slot_types = [
            "Arme 1",  # Slot 1 : Arme
            "Arme 2",  # Slot 2 : Arme
            "Bouclier",  # Slot 3 : Bouclier
            "Livre",  # Slot 4 : Livre
            "Équipement",  # Slot 5 : Equipement
            "Objet 1",  # Slot 6 : Objet usage unique
            "Objet 2",  # Slot 7 : Objet usage unique
            "Objet 3"  # Slot 8 : Objet usage unique
        ]
        self.slot_to_item_type = {
            0: "arme",
            1: "arme",
            2: "bouclier",
            3: "livre",
            4: "équipement",
            5: "objet usage unique",
            6: "objet usage unique",
            7: "objet usage unique"
        }

        # Dictionnaire des objets présents dans l'inventaire
        self.items = {
            0: None,  # Slot 1 : Arme
            1: None,  # Slot 2 : Arme
            2: None,  # Slot 3 : Bouclier
            3: None,  # Slot 4 : Livre
            4: None,  # Slot 5 : Equipement
            5: None,  # Slot 6 : Objet usage unique
            6: None,  # Slot 7 : Objet usage unique
            7: None,  # Slot 8 : Objet usage unique
        }
        self.items = {i: None for i in range(8)}
        self.is_visible = False  # Inventaire visible ou non
    def is_slot_clicked(self, index, mouse_x, mouse_y, screen):
        """Vérifie si un slot d'inventaire est cliqué."""
        slot_width, slot_height = 80, 80
        margin = 15
        inventory_y = screen.get_height() - slot_height - 20
        slot_x = (screen.get_width() - (slot_width + margin) * 8) // 2 + index * (slot_width + margin)
        slot_rect = pygame.Rect(slot_x, inventory_y, slot_width, slot_height)
        return slot_rect.collidepoint(mouse_x, mouse_y)

    def is_slot_hovered(self, mouse_x, mouse_y, screen):
        """Vérifie si un slot d'inventaire est survolé."""
        return any(self.is_slot_clicked(i, mouse_x, mouse_y, screen) for i in range(8))

    def get_hovered_slot(self, mouse_x, mouse_y, screen):
        """Retourne l'index du slot d'inventaire survolé par la souris."""
        for i in range(8):
            if self.is_slot_clicked(i, mouse_x, mouse_y, screen):
                return i
        return None
    def toggle_inventory(self):
        """Afficher ou masquer l'inventaire lorsque TAB est pressé."""
        self.is_visible = not self.is_visible

    def add_item(self, slot, item):
        """Ajouter un item dans un slot spécifique."""
        if self.items[slot] is None:  # Le slot est vide
            self.items[slot] = item
        else:
            print(f"Le slot {slot + 1} est déjà occupé par {self.items[slot]} !")

    def remove_item(self, slot):
        """Supprimer un item d'un slot."""
        if self.items[slot] is not None:
            self.items[slot] = None
        else:
            print(f"Le slot {slot + 1} est déjà vide.")

    def draw_inventory(self, screen):
        """Dessiner l'inventaire du joueur avec les couleurs de rareté."""
        if self.is_visible:
            slot_width, slot_height = 80, 80
            margin = 15
            inventory_y = screen.get_height() - slot_height - 20

            mouse_x, mouse_y = pygame.mouse.get_pos()

            for i in range(8):
                slot_x = (screen.get_width() - (slot_width + margin) * 8) // 2 + i * (slot_width + margin)
                slot_y = inventory_y

                # Couleur de bordure de rareté
                item = self.items[i]
                rarity_color = self.get_rarity_color(item.rarity) if item else (200, 200, 200)

                # Dessiner le slot avec la couleur de rareté
                pygame.draw.rect(screen, rarity_color, (slot_x, slot_y, slot_width, slot_height), 3)

                font = pygame.font.SysFont(None, 18)
                slot_text = font.render(self.slot_types[i], True, (255, 255, 255))
                screen.blit(slot_text, (slot_x + 5, slot_y + 5))

                if item:
                    try:
                        item_texture = pygame.image.load(item.texture).convert_alpha()
                        item_texture = pygame.transform.scale(item_texture, (65, 65))
                        texture_rect = item_texture.get_rect(center=(slot_x + slot_width // 2, slot_y + slot_height // 2))
                        screen.blit(item_texture, texture_rect)
                    except Exception as e:
                        print(f"Erreur lors du chargement de la texture pour {item.name}: {e}")

                    slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
                    if slot_rect.collidepoint(mouse_x, mouse_y):
                        self.display_item_info(screen, item, mouse_x, mouse_y)


    def display_item_info(self, screen, item, mouse_x, mouse_y):
        """Affiche les informations détaillées d'un item en survol."""
        info_width, info_height = 200, 120
        info_bg = pygame.Surface((info_width, info_height))
        info_bg.fill((30, 30, 30))
        pygame.draw.rect(info_bg, (255, 255, 255), info_bg.get_rect(), 2)
        screen.blit(info_bg, (mouse_x, mouse_y))

        font = pygame.font.SysFont(None, 20)

        # Nom de l'item
        item_name = font.render(item.name, True, (255, 255, 0))
        screen.blit(item_name, (mouse_x + 10, mouse_y + 5))

        # Rareté avec couleur
        rarity_color = self.get_rarity_color(item.rarity)
        rarity_text = font.render(f"{item.rarity.capitalize()}", True, rarity_color)
        screen.blit(rarity_text, (mouse_x + 10, mouse_y + 25))

        # Attributs
        for i, (attr_name, attr_value) in enumerate(item.attributes.items()):
            attr_text = font.render(f"{attr_name}: {attr_value}", True, (255, 255, 255))
            screen.blit(attr_text, (mouse_x + 10, mouse_y + 45 + i * 15))
    def get_rarity_color(self, rarity):

        """Retourne une couleur selon la rareté de l'item."""
        colors = {
            "commun": (192, 192, 192),
            "rare": (0, 0, 255),
            "épique": (128, 0, 128),
            "légendaire": (255, 215, 0),
        }
        return colors.get(rarity, (255, 255, 255))
    def get_item_by_name(self, name):
        """Retourne l'item correspondant au nom donné."""
        for item in self.items.values():
            if item is not None and item.name == name:
                return item
        return None  # Si aucun item ne correspond