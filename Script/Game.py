import pygame
from Donjon.map import Map  
from Character.Hero import Player  
from Character.Monsterr import MonsterManager  
from GameMachine.combat import Combat
from GameMachine.portail_window import PortalWindow
from Character.inventaire import Inventory
from Donjon.items import Items  
from Donjon.treasor import ChestManager
from Donjon.portal import PortalManager
from Character.Boss import BossManager
from GameMachine.niveau import Niveau
from GameMachine.ath import afficher_ath
clock = pygame.time.Clock()
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.niveau = Niveau()
        self.monsters = []  # Liste pour un accès facile à tous les monstres
        self.chests = []
        self.running = True
        self.tile_size = 50
        self.score = 0
        self.map = Map(screen, self.niveau)
        self.inventory = Inventory()  
        self.player = Player(x=353, y=550, size=45, map_obj=self.map, inventory=self.inventory)
        self.monster_manager = MonsterManager(self.map, self.niveau)
        self.boss_manager = BossManager(self.map, self.niveau)
        self.portal_manager = PortalManager(self.map.layout, self.tile_size) 
        self.items = Items(self.niveau)
        self.chest_manager = ChestManager(self.map.layout, self.tile_size, self.niveau)
        self.give_starting_items()
        self.monster_manager.spawn_monsters()
        self.nearby_chest = None
        self.opened_chest = None
        self.selected_item = None
        self.selected_item_origin = None
        self.selected_slot_index = None
        self.inventory_locked = False
         
    
       
        self.portal_window = None

    @property
    def monsters_manager(self):
        """Vérifie si des monstres sont présents."""
        return len(self.monsters) > 0

    def toggle_inventory(self):
        """Afficher ou masquer l'inventaire personnel, avec verrouillage du glisser-déposer si aucun coffre n'est ouvert."""
        self.inventory.toggle_inventory()
        # Verrouille le glisser-déposer uniquement si l'inventaire personnel est ouvert sans coffre
        if self.inventory.is_visible and not self.opened_chest:
            self.inventory_locked = True
        else:
            self.inventory_locked = False
    def give_starting_items(self):
        """Ajoute des items de départ dans l'inventaire du joueur."""
        common_items = [item for item in self.items.get_items() if item.rarity == "commun"]  # Filtrer les items communs

        if len(common_items) >= 3:  # Vérifier qu'il y a au moins 3 items communs
            self.inventory.add_item(0, common_items[0])  # Épée d'acier
            self.inventory.add_item(2, common_items[1])  # Bouclier en bois
            self.inventory.add_item(5, common_items[3])  # Poulet
        else:
            print("Erreur : Pas assez d'items communs disponibles pour le niveau actuel.")

    def display_chest_inventory(self, chest):
        """Affiche l'inventaire du coffre."""
        inventory_bg_height = 150
        slot_width, slot_height = 80, 80
        margin = 30

        # Fond de l'inventaire du coffre
        inventory_bg = pygame.Surface((self.screen.get_width(), inventory_bg_height))
        inventory_bg.fill((50, 50, 50))
        self.screen.blit(inventory_bg, (0, 0))

        # Titre de l'inventaire du coffre
        font = pygame.font.SysFont(None, 24)
        title_text = font.render("Items du Coffre:", True, (255, 255, 0))
        self.screen.blit(title_text, (10, 10))

        # Position de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Placer les slots pour les items du coffre
        for i, item in enumerate(chest.items):
            slot_x = (self.screen.get_width() - (slot_width + margin) * 3) // 2 + i * (slot_width + margin)
            slot_y = 40

            # Couleur de bordure en fonction de la rareté
            rarity_color = self.get_rarity_color(item.rarity if item else "commun")
            pygame.draw.rect(self.screen, rarity_color, (slot_x, slot_y, slot_width, slot_height), 3)

            # Afficher l'image de l'item
            if item:
                try:
                    item_texture = pygame.image.load(item.texture).convert_alpha()
                    item_texture = pygame.transform.scale(item_texture, (65, 65))
                    texture_rect = item_texture.get_rect(center=(slot_x + slot_width // 2, slot_y + slot_height // 2))
                    self.screen.blit(item_texture, texture_rect)
                except Exception as e:
                    print(f"Erreur lors du chargement de la texture pour {item.name}: {e}")

                # Détection de survol de la souris
                slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    self.display_item_info(item, mouse_x, mouse_y)
    def open_chest_inventory(self, chest):
        """Affiche l'inventaire du coffre en plus de l'inventaire personnel, sans verrouiller le glisser-déposer."""
        self.inventory.toggle_inventory()  # Affiche ou masque l'inventaire
        self.opened_chest = chest if self.inventory.is_visible else None
        # Désactive le verrouillage pour permettre le glisser-déposer avec le coffre
        self.inventory_locked = False
    def swap_items(self, source, destination, source_index, destination_index):
        """Échange les items entre deux inventaires, avec vérification du type pour l'inventaire uniquement."""
        item_to_move = source[source_index]

        # Vérification si le slot de destination est une case de l'inventaire
        if destination == self.inventory.items:
            # Vérifie que le type de l'item correspond au type attendu par le slot d'inventaire
            expected_type = self.inventory.slot_to_item_type.get(destination_index)
            if item_to_move and item_to_move.type != expected_type:
                print(f"Impossible de déplacer {item_to_move.name} dans le slot de type '{expected_type}'")
                return  # Annule l'échange si le type ne correspond pas

        # Échange des items entre source et destination si les conditions sont remplies
        source[source_index], destination[destination_index] = destination[destination_index], source[source_index]



    def is_chest_slot_hovered(self, mouse_x, mouse_y):
        """Vérifie si un slot de coffre est survolé."""
        # Vérifie que le coffre est ouvert
        if self.opened_chest is None:
            return None

        slot_width, slot_height = 80, 80
        margin = 30

        # Parcourt tous les slots du coffre pour voir si l'un est survolé
        for i in range(len(self.opened_chest.items)):
            slot_x = (self.screen.get_width() - (slot_width + margin) * 3) // 2 + i * (slot_width + margin)
            slot_y = 40
            slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
            if slot_rect.collidepoint(mouse_x, mouse_y):
                return i  # Retourne l'index du slot survolé
        return None
    def handle_mouse_events(self, event):
        """Gère les événements de la souris pour le glisser-déposer entre inventaire et coffre."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
    
            # Bloque le glisser-déposer dans l'inventaire personnel si inventory_locked est True
            if self.inventory_locked:
                return
    
            # Sélection d'un item dans l'inventaire
            for i, item in self.inventory.items.items():
                if item and self.inventory.is_slot_clicked(i, mouse_x, mouse_y, self.screen):
                    self.selected_item = item
                    self.selected_item_origin = "inventory"
                    self.selected_slot_index = i
                    return
    
            # Sélection d'un item dans le coffre
            if self.opened_chest:
                for i, item in enumerate(self.opened_chest.items):
                    if item and self.is_chest_slot_clicked(i, mouse_x, mouse_y):
                        self.selected_item = item
                        self.selected_item_origin = "chest"
                        self.selected_slot_index = i
                        return
    
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Bloque le dépôt d'items si inventory_locked est True
            if self.inventory_locked:
                return
    
            if self.selected_item:
                mouse_x, mouse_y = event.pos
    
                # Déposer l'item dans l'inventaire (si compatible)
                if self.selected_item_origin == "chest" and self.inventory.is_slot_hovered(mouse_x, mouse_y, self.screen):
                    target_slot = self.inventory.get_hovered_slot(mouse_x, mouse_y, self.screen)
                    if target_slot is not None:
                        # Vérifie la compatibilité de type
                        expected_type = self.inventory.slot_to_item_type.get(target_slot)
                        if expected_type == self.selected_item.type:
                            self.swap_items(self.opened_chest.items, self.inventory.items, self.selected_slot_index, target_slot)
                        else:
                            print(f"Impossible de déplacer {self.selected_item.name} dans un slot de type '{expected_type}'")
    
                # Déposer l'item dans le coffre (aucune restriction de type)
                elif self.selected_item_origin == "inventory" and self.is_chest_slot_hovered(mouse_x, mouse_y) is not None:
                    target_slot = self.is_chest_slot_hovered(mouse_x, mouse_y)
                    if target_slot is not None:
                        self.swap_items(self.inventory.items, self.opened_chest.items, self.selected_slot_index, target_slot)
    
                # Réinitialisation de l'état de sélection
                self.selected_item = None
                self.selected_item_origin = None
                self.selected_slot_index = None

    def get_rarity_color(self, rarity):
        """Retourne une couleur selon la rareté de l'item."""
        colors = {
            "commun": (192, 192, 192),
            "rare": (0, 0, 255),
            "épique": (128, 0, 128),
            "légendaire": (255, 215, 0),
        }
        return colors.get(rarity, (255, 255, 255))  # Blanc par défaut

    def display_item_info(self, item, mouse_x, mouse_y):
        """Affiche les informations détaillées d'un item en survol."""
        # Créer une surface pour les informations de l'item
        info_width, info_height = 200, 120
        info_bg = pygame.Surface((info_width, info_height))
        info_bg.fill((30, 30, 30))  # Fond sombre pour les informations
        pygame.draw.rect(info_bg, (255, 255, 255), info_bg.get_rect(), 2)  # Bordure blanche

        # Positionner le panneau juste en dessous de la souris
        self.screen.blit(info_bg, (mouse_x, mouse_y))

        # Initialiser la police pour le texte
        font = pygame.font.SysFont(None, 20)

        # Nom de l'item
        item_name = font.render(item.name, True, (255, 255, 0))
        self.screen.blit(item_name, (mouse_x + 10, mouse_y + 5))

        # Rareté de l'item (avec couleur spécifique)
        rarity_color = self.get_rarity_color(item.rarity)
        rarity_text = font.render(f"{item.rarity.capitalize()}", True, rarity_color)
        self.screen.blit(rarity_text, (mouse_x + 10, mouse_y + 25))

        # Afficher les attributs de l'item sous la rareté
        for i, (attr_name, attr_value) in enumerate(item.attributes.items()):
            attr_text = font.render(f"{attr_name}: {attr_value}", True, (255, 255, 255))
            self.screen.blit(attr_text, (mouse_x + 10, mouse_y + 45 + i * 15))
    def is_chest_slot_clicked(self, index, mouse_x, mouse_y):
        """Vérifie si le slot du coffre est cliqué."""
        slot_width, slot_height = 80, 80  # Dimensions des slots
        margin = 30  # Espace entre les slots

        # Calculer la position x et y du slot du coffre
        slot_x = (self.screen.get_width() - (slot_width + margin) * 3) // 2 + index * (slot_width + margin)
        slot_y = 40  # Position fixe pour les slots

        # Créer un rectangle pour le slot
        slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)

        # Vérifier si la position de la souris est dans le rectangle
        return slot_rect.collidepoint(mouse_x, mouse_y)
    def run(self):
            while self.running:
                delta_time = clock.tick(60) / 1000.0
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            self.inventory.toggle_inventory()
                        if event.key == pygame.K_o and self.nearby_chest:
                            self.open_chest_inventory(self.nearby_chest)

                    self.handle_mouse_events(event)

                if not self.inventory.is_visible:
                    
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_z] or keys[pygame.K_UP]:
                        self.player.move_player('up', delta_time, self.monster_manager, self.chest_manager)
                    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                        self.player.move_player('down', delta_time, self.monster_manager, self.chest_manager)
                    elif keys[pygame.K_q] or keys[pygame.K_LEFT]:
                        self.player.move_player('left', delta_time, self.monster_manager, self.chest_manager)
                    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                        self.player.move_player('right', delta_time, self.monster_manager, self.chest_manager)

                    self.nearby_chest = None
                    for chest in self.chest_manager.chests:
                        chest_rect = pygame.Rect(chest.x, chest.y, chest.tile_size, chest.tile_size)
                        if self.player.rect.colliderect(chest_rect.inflate(30, 30)):
                            self.nearby_chest = chest
                            break

                    # Détection de la collision avec le portail
                    collided_portal = self.portal_manager.check_collisions_with_player(self.player)
                    if collided_portal:
                        # Réinitialiser l'instance de PortalWindow à chaque collision avec un portail
                        self.portal_window = PortalWindow(self.screen, self.niveau)
                        
                        # Affiche la fenêtre de l'énigme et vérifie la réponse
                        self.portal_window.run()

                        # Si le joueur a réussi l'énigme, générez une nouvelle salle
                        if self.portal_window.running == False:
                            self.map.generate_new_room()
                            self.portal_manager.update_layout(self.map.layout)
                            self.chest_manager.update_layout(self.map.layout)
                            self.chest_manager.spawn_chests()
                            self.monster_manager.spawn_monsters()

                            # Positionner le joueur dans la nouvelle salle, par exemple en bas de la salle
                            self.player.rect.x = 353
                            self.player.rect.y = 550

                    if self.map.room_changed:
                        self.chest_manager.update_layout(self.map.layout)
                        self.chest_manager.spawn_chests()
                        self.monster_manager.spawn_monsters()
                        self.boss_manager.spawn_bosses()
                        self.portal_manager.update_layout(self.map.layout)
                        self.map.room_changed = False
                        self.score += self.niveau.level * 2

                    collided_monster = self.monster_manager.check_collision_with_player(self.player)
                    collided_boss = self.boss_manager.check_collision_with_player(self.player)
                    if collided_boss:
                        combat = Combat(self.screen, self.player, collided_boss, self.map)
                        combat.run()

                        if combat.message == "Monster Defeated":
                            self.boss_manager.remove_boss(collided_boss)
                            self.score += 500
                            self.niveau.avancer_niveau()
                        elif combat.message == "Vous avez fui !":
                            continue
                    if collided_monster:
                        combat = Combat(self.screen, self.player, collided_monster, self.map)
                        combat.run()

                        if combat.message == "Monster Defeated":
                            self.monster_manager.remove_monster(collided_monster)
                            if combat.message == "Monster Defeated":
                                    self.monster_manager.remove_monster(collided_monster)
                                    self.score += self.niveau.level * 10
                        elif combat.message == "Vous avez fui !":
                            continue

                self.screen.fill((0, 0, 0))
                
                if not self.inventory.is_visible:
                    self.map.draw_room()
                    self.monster_manager.draw_monsters(self.screen)
                    self.boss_manager.draw_bosses(self.screen)
                    self.chest_manager.draw_chests(self.screen, self.player.rect)
                    self.portal_manager.draw(self.screen)
                    self.player.draw_player(self.screen)
                    afficher_ath(self.screen, self.player, self.niveau.level, self.score)

                if self.inventory.is_visible:
                    if self.opened_chest:
                        self.display_chest_inventory(self.opened_chest)
                    self.inventory.draw_inventory(self.screen)

                if self.selected_item:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    item_texture = pygame.image.load(self.selected_item.texture).convert_alpha()
                    item_texture = pygame.transform.scale(item_texture, (65, 65))
                    self.screen.blit(item_texture, (mouse_x - 32, mouse_y - 32))

                pygame.display.flip()
