import pygame
import sys
import math
import path_config
from Donjon.items import Item
from Character.inventaire import Inventory
from GameMachine.dead import DeadScreen

class CombatWindow:
    def __init__(self, screen, player, monster, name="Monstre"):
        self.name = name
        self.screen = screen
        self.player = player
        self.monster = monster
        self.font = pygame.font.SysFont("Arial", 26)
        self.running = True
        self.buttons = ["Attaquer", "Action", "Objet"]
        self.selected_button = 0
        self.attack_mode = False
        self.action_mode = False  
        self.object_mode = False
        self.selected_weapon = 0
        self.selection_cooldown = 300
        self.last_selection_time = 0
        self.attack_wait_time = 1000
        self.confirm_attack_mode = False  
        # Gauge attributes
        self.gauge_active = False
        self.gauge_position = 0  
        self.gauge_direction = 1 
        self.gauge_speed = 0.0035
        self.multiplier = 1.0
        self.white_zone = (0.0, 1.0)  
        self.yellow_zone = (0.3, 0.7) 
        self.blue_zone = (0.45, 0.55) 

        # Load heart icon
        heart_image_path = path_config.get_base_texture_path() + "Sprite/heart.png"
        self.heart_image = pygame.image.load(heart_image_path).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (50, 50))

        # Load player image
        self.walk_right2_image = pygame.image.load(path_config.get_base_texture_path() + "Sprite/player/walk_right2.png").convert_alpha()
        self.walk_right2_image = pygame.transform.scale(self.walk_right2_image, (100, 100))

        # initialise le monstre et load son image
        self.monster.hp = self.monster.hp
        self.monster.max_hp = self.monster.hp
        self.monster.damage = self.monster.damage
        self.monster_image = pygame.transform.scale(
            self.monster.image_left, (150, 150)  
        )
        # initialise perso stat
        self.weapon_one = self.player.weapon1
        self.weapon_two = self.player.weapon2
        self.shield = self.player.shield1
        self.equipement = self.player.equipement1
        self.speed = (
            (self.shield.attributes.get('speed', 0) if self.shield else 0) + 
            (self.equipement.attributes.get('speed', 0) if  self.equipement else 0)
            )
        self.strength = (
            (self.shield.attributes.get('strength', 0) if self.shield else 0) + 
            (self.equipement.attributes.get('strength', 0) if  self.equipement else 0)
            )
        self.accuracy = (
            (self.shield.attributes.get('accuracy', 0) if self.shield else 0) + 
            (self.equipement.attributes.get('accuracy', 0) if  self.equipement else 0)
            )
        self.protection = (
            (self.shield.attributes.get('protection', 0) if self.shield else 0) + 
            (self.equipement.attributes.get('protection', 0) if  self.equipement else 0)
        )
    
    def draw_combat_scene(self):
        self.screen.fill((30, 30, 30))  # Fond sombre
        center_y = self.screen.get_height() // 2

        # Dessiner le joueur
        player_margin_x = 100
        player_rect = self.walk_right2_image.get_rect(topleft=(player_margin_x, center_y - 50))
        self.screen.blit(self.walk_right2_image, player_rect.topleft)
        self.draw_health_bar(self.player, player_rect.x, player_rect.y - 45)

        # Dessiner le monstre avec sa taille réelle
        monster_display_size = self.monster.size * 1.9  # Taille réelle du monstre (augmentée)
        monster_margin_x = 150
        monster_x = self.screen.get_width() - monster_margin_x - monster_display_size

        # Fixer la position Y pour que le monstre reste aligné verticalement
        fixed_y = center_y - 100  # Position Y de base
        monster_y = fixed_y + (150 - monster_display_size) // 2  # Ajustement pour centrer le monstre

        # Redimensionner l'image du monstre à sa taille réelle
        resized_monster_image = pygame.transform.scale(
            self.monster_image, (monster_display_size, monster_display_size)
        )

        # Afficher le monstre redimensionné
        self.screen.blit(resized_monster_image, (monster_x, monster_y))
        self.draw_health_bar(self.monster, monster_x, monster_y - 45)

        # Afficher les options en fonction du mode actif
        if self.gauge_active:
            self.draw_gauge()
        elif self.attack_mode:
            self.draw_attack_options()
        elif self.action_mode:
            self.draw_action_options()
        elif self.object_mode:
            self.draw_object_options()
        else:
            self.draw_buttons()

        pygame.display.flip()

    def draw_gauge(self):
        gauge_center = (self.screen.get_width() // 2, self.screen.get_height() - 100)  
        gauge_radius = 100  
        gauge_thickness = 10

        self.draw_zone(gauge_center, gauge_radius, gauge_thickness, self.white_zone, (255, 255, 255), (200, 200, 200))
        self.draw_zone(gauge_center, gauge_radius, gauge_thickness, self.yellow_zone, (255, 255, 0), (255, 215, 0))
        self.draw_zone(gauge_center, gauge_radius, gauge_thickness, self.blue_zone, (0, 0, 255), (0, 191, 255))

        current_angle = math.radians(180) * (1 - self.gauge_position) 
        indicator_x = gauge_center[0] + int((gauge_radius - gauge_thickness // 2) * math.cos(current_angle))
        indicator_y = gauge_center[1] - int((gauge_radius - gauge_thickness // 2) * math.sin(current_angle))

        self.draw_pointer(indicator_x, indicator_y)

    def draw_zone(self, center, radius, thickness, zone_range, color, gradient_color):
        start_deg = 180 - (180 * zone_range[1]) 
        end_deg = 180 - (180 * zone_range[0])      
       
        for angle in range(int(start_deg), int(end_deg)):
            rad = math.radians(angle)
            x = center[0] + int(radius * math.cos(rad))
            y = center[1] - int(radius * math.sin(rad))
            color_ratio = (angle - start_deg) / (end_deg - start_deg)
            
            current_color = (
                max(0, min(255, int(color[0] * (1 - color_ratio) + gradient_color[0] * color_ratio))),
                max(0, min(255, int(color[1] * (1 - color_ratio) + gradient_color[1] * color_ratio))),
                max(0, min(255, int(color[2] * (1 - color_ratio) + gradient_color[2] * color_ratio)))
            )
            
            pygame.draw.circle(self.screen, current_color, (x, y), thickness // 2)

    def draw_pointer(self, x, y):
        pointer_color = (255, 0, 0)  
        pointer_radius = 8  
        pygame.draw.circle(self.screen, pointer_color, (x, y), pointer_radius)

    def update_gauge(self):
        if not self.gauge_active:
            return

        adjusted_speed = max(0.001, self.gauge_speed - (self.speed / 10000))  
        self.gauge_position += self.gauge_direction * adjusted_speed

        if self.gauge_position <= 0 or self.gauge_position >= 1:
            self.gauge_direction *= -1  

    def stop_gauge(self):
        if self.blue_zone[0] <= self.gauge_position <= self.blue_zone[1]:
            self.multiplier = 1.25
        elif self.yellow_zone[0] <= self.gauge_position <= self.yellow_zone[1]:
            self.multiplier = 1.0
        else:
            self.multiplier = 0.75
        print(f"Multiplier based on gauge: {self.multiplier}")
        self.gauge_active = False
        self.attack_mode = False  
        self.apply_damage()

    def apply_damage(self):
        """Applique les dégâts au monstre en utilisant le multiplicateur et la force du joueur comme facteur."""
        weapon = self.player.weapon1 if self.selected_weapon == 0 else self.player.weapon2
       
        if weapon is None:
            # Si le joueur n'a pas d'arme équipée, inflige des dégâts basés sur la force du joueur
            base_damage = 10  # Dégâts de base sans arme
            force_multiplier = 1 + (self.strength / 100) if self.strength > 0 else 1
            damage = int(base_damage * self.multiplier * force_multiplier)
            self.monster.hp -= damage
            print(f"Le monstre reçoit {damage} points de dégâts avec un multiplicateur de {self.multiplier} et une force de {self.strength}.")
        if isinstance(weapon, Item):
            base_damage = weapon.attributes.get('damage', 0)
            force_multiplier = 1 + (self.strength / 100)
            damage = int(base_damage * self.multiplier * force_multiplier)
            self.monster.hp -= damage
            print(f"Le monstre reçoit {damage} points de dégâts avec un multiplicateur de {self.multiplier} et une force de {self.strength}.")
        # MODIF : Animation de lumière lors de l'attaque du joueur
        self.animate_light(attacker="player")

        self.monster.hp = max(self.monster.hp, 0)
        if self.monster.hp <= 0:
            print("Le monstre est vaincu !")
            self.message = "Monster Defeated"  
            self.end_combat()
        else:
            self.monster_attack()

    def draw_health_bar(self, entity, x, y):
        bar_width = 200
        bar_height = 25
        health_ratio = entity.hp / entity.max_hp
        health_bar_width = int(bar_width * health_ratio)
        health_bar_width = min(health_bar_width, bar_width - 4)

        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (250, 20, 20), (x + 2, y + 2, health_bar_width, bar_height - 4))
        
        health_text = f"{entity.hp} / {entity.max_hp}"
        text_surface = self.font.render(health_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
        self.screen.blit(text_surface, text_rect)

        heart_x = x - 45
        heart_y = y - (bar_height // 2)
        self.screen.blit(self.heart_image, (heart_x, heart_y))

    def draw_buttons(self):
        button_width = 150
        button_height = 50
        button_x = (self.screen.get_width() - (button_width * len(self.buttons))) // 2
        button_y = self.screen.get_height() - 70

        for i, button in enumerate(self.buttons):
            button_rect = pygame.Rect(button_x + i * button_width, button_y, button_width, button_height)
            color = (255, 255, 255) if button_rect.collidepoint(pygame.mouse.get_pos()) else (100, 100, 100)
            
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2, border_radius=10)  
            text = self.font.render(button, True, (0, 0, 0))  
            self.screen.blit(text, (button_rect.x + 10, button_rect.y + 10))

    def draw_attack_options(self):
        option_width = 180
        option_height = 60
        option_x = (self.screen.get_width() - option_width * 2) // 2
        option_y = self.screen.get_height() - 150
        weapons = [self.player.weapon1, self.player.weapon2]
        self.option_rects = []  

        mouse_x, mouse_y = pygame.mouse.get_pos() 

        for i, weapon in enumerate(weapons):
            option_rect = pygame.Rect(option_x + i * option_width, option_y, option_width, option_height)
            self.option_rects.append(option_rect)  

            if option_rect.collidepoint(mouse_x, mouse_y):
                color = (255, 200, 20) 
                if pygame.mouse.get_pressed()[0]:
                    self.selected_weapon = i
                    weapon_name = weapon.name if weapon else "Aucune"
                    print(f"Vous avez sélectionné {weapon_name}")
                    self.confirm_attack()  
                    break
            else:
                color = (70, 70, 70)  

            pygame.draw.rect(self.screen, color, option_rect, border_radius=10)  
            pygame.draw.rect(self.screen, (0, 0, 0), option_rect, 2, border_radius=10)  
            weapon_text = weapon.name if weapon else "Aucune"
            text_surface = self.font.render(weapon_text, True, (255, 255, 255))  
            text_rect = text_surface.get_rect(center=option_rect.center)
            self.screen.blit(text_surface, text_rect)

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        if self.gauge_active:
            if keys[pygame.K_SPACE]:
                self.stop_gauge()
            return  

        if self.attack_mode:
            if not self.confirm_attack_mode:
                if pygame.mouse.get_pressed()[0]:
                    for i, option_rect in enumerate(self.option_rects):
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_weapon = i
                            weapon = self.player.weapon1 if self.selected_weapon == 0 else self.player.weapon2
                            weapon_name = weapon.name if weapon else "Aucune"
                            print(f"Vous avez sélectionné {weapon_name}")
                            self.confirm_attack()
                            break
                elif keys[pygame.K_BACKSPACE]:
                    self.attack_mode = False  
        elif self.action_mode:
            if pygame.mouse.get_pressed()[0]:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        action_name = ["Dialogue", "Utiliser Sort", "Inspecter", "Fuite"][i]
                        self.perform_action(action_name)
                        break
            elif keys[pygame.K_BACKSPACE]:
                self.action_mode = False  
        else:
            if current_time - self.last_selection_time > self.selection_cooldown:
                for i in range(len(self.buttons)):
                    button_rect = pygame.Rect((self.screen.get_width() - (150 * len(self.buttons))) // 2 + i * 150, self.screen.get_height() - 70, 150, 50)
                    if button_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
                        self.selected_button = i
                        self.execute_button_action()
                        break

    def execute_button_action(self):
        action = self.buttons[self.selected_button]
        if action == "Attaquer":
            self.attack_mode = True
            self.confirm_attack_mode = False
        elif action == "Action":
            self.action_mode = True
        elif action == "Objet":
            self.object_mode = True  

    def perform_action(self, action_name):
        if action_name == "Dialogue":
            print("Vous engagez une discussion avec le monstre, mais il ne peut pas répondre.")
        elif action_name == "Utiliser Sort":
            if hasattr(self.player, 'sort1'):
                sort = self.player.sort1

                if sort:
                    print(f"Vous utilisez le sort {sort.name} !")

                    damage = sort.attributes.get('damage', 0)
                    repeat = sort.attributes.get('repeat', False)
                    duration = sort.attributes.get('duration', 0)
                    stealth = sort.attributes.get('stealth', False)
                    weakness = sort.attributes.get('weakness', 0)
                    regeneration = sort.attributes.get('regeneration', False)
                    double_damage = sort.attributes.get('double_damage', False)
                    if damage > 0:
                        total_damage = damage
                        if repeat:
                            pass
                        else:
                            print(f"Le sort inflige {total_damage} dégâts au monstre")
                        self.monster.hp = max(self.monster.hp - total_damage, 0)
                    if weakness > 0:
                        print(f"Le monstre subit une réduction de dégâts de {weakness} pour {duration} tours.")
                        self.monster.damage = max(self.monster.damage - weakness, 0)
                    if regeneration:
                        regen_amount = sort.attributes.get('regeneration', 10)
                        self.player.hp = min(self.player.hp + regen_amount, self.player.max_hp)
                        print(f"Le sort régénère {regen_amount} PV pour le joueur. PV actuel: {self.player.hp}/{self.player.max_hp}.")
                    if stealth:
                        print("Le sort garantit une fuite réussie.")
                        self.fuite_reussie = True
                    if double_damage:
                        print("Les dégâts seront doublés lors de la prochaine attaque.")
                    
                    self.monster_attack()
            else:
                print("Aucun sort n'est défini pour le joueur.")
        elif action_name == "Inspecter":
            print(f"Statistiques du monstre: HP = {self.monster.hp}/{self.monster.max_hp}, Dégâts = {self.monster.damage}")
        elif action_name == "Fuite":
            if hasattr(self, 'fuite_reussie') and self.fuite_reussie:
                print("Vous vous enfuyez avec succès grâce à l'effet de furtivité du sort.")
                self.running = False
            else:
                print("Vous tentez de fuir le combat, mais cela n'est pas encore implémenté.")
        self.action_mode = False  
    
        weapon = self.player.weapon1 if self.selected_weapon == 0 else self.player.weapon2 
        if weapon:
            print(f"Vous attaquez avec {weapon.name} !")
            pygame.time.delay(self.attack_wait_time)
        else:
            print("Aucune arme équipée pour attaquer.")            
        self.attack_mode = True  
        self.confirm_attack_mode = True  

    def draw_action_options(self):
        action_names = ["Dialogue", "Utiliser Sort", "Inspecter", "Fuite"]
        option_width = 180
        option_height = 60
        option_x = (self.screen.get_width() - option_width * len(action_names)) // 2
        option_y = self.screen.get_height() - 150
        self.option_rects = []

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for i, action_name in enumerate(action_names):
            option_rect = pygame.Rect(option_x + i * option_width, option_y, option_width, option_height)
            self.option_rects.append(option_rect)
            color = (255, 200, 20) if option_rect.collidepoint(mouse_x, mouse_y) else (70, 70, 70)
            pygame.draw.rect(self.screen, color, option_rect, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), option_rect, 2, border_radius=10)
            text_surface = self.font.render(action_name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=option_rect.center)
            self.screen.blit(text_surface, text_rect)

            if option_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
                self.perform_action(action_name)
    
    def draw_object_options(self):
        object_ids = [5, 6, 7]
        option_width = 180
        option_height = 60
        option_x = (self.screen.get_width() - option_width * len(object_ids)) // 2
        option_y = self.screen.get_height() - 150
        self.option_rects = []

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for i, object_id in enumerate(object_ids):
            obj = self.player.inventory.items.get(object_id)
            option_rect = pygame.Rect(option_x + i * option_width, option_y, option_width, option_height)
            self.option_rects.append(option_rect)

            color = (255, 200, 20) if option_rect.collidepoint(mouse_x, mouse_y) else (70, 70, 70)
            pygame.draw.rect(self.screen, color, option_rect, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), option_rect, 2, border_radius=10)

            object_text = obj.name if obj else "Aucun"
            text_surface = self.font.render(object_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=option_rect.center)
            self.screen.blit(text_surface, text_rect)

            if option_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
                self.use_object(object_id)
                self.object_mode = False

    def confirm_attack(self):
        """Start the gauge when confirming an attack, and reduce weapon durability."""
        weapon = self.player.weapon1 if self.selected_weapon == 0 else self.player.weapon2
        if  weapon is None : 
            print("Aucune arme équipée pour attaquer.")
            self.gauge_active = True
    
        elif weapon and hasattr(weapon, 'attributes') and 'durability' in weapon.attributes:
            weapon.attributes['durability'] -= 1
            print(f"Vous attaquez avec {weapon.name}! Durabilité restante: {weapon.attributes['durability']}")
            if weapon.attributes['durability'] <= 0:
                print(f"L'arme {weapon.name} est cassée et disparaît!")
                for object_id, item in enumerate(self.player.inventory.items):
                    if item == weapon:
                        self.player.inventory.items[object_id] = None
                        break
                if self.selected_weapon == 0:
                    self.player.inventory.remove_item(0)
                else:
                    self.player.inventory.remove_item(1)

            self.gauge_active = True 
        elif weapon:
            print(f"Vous attaquez avec {weapon.name} !")
            self.gauge_active = True
        else:
            print("Aucune arme équipée pour attaquer.")
        
        self.attack_mode = False

    def monster_attack(self):
        """Le monstre attaque le joueur, réduisant ses HP en fonction de la protection du joueur"""
        # Animation de lumière lors de l'attaque du monstre
        self.animate_light(attacker="monster")
        effective_damage = max(self.monster.damage - self.protection, 0) 
        self.player.hp -= effective_damage
        print(f"Le joueur reçoit {effective_damage} points de dégâts après protection de {self.protection}")

        if self.player.hp <= 0:
            print("Le joueur est vaincu !")
            self.message = "Player Defeated"  
            self.end_combat()
            self.show_dead_screen()
        else:
            print(f"Il reste {self.player.hp} HP au joueur")

    def end_combat(self):
        """Ends the combat."""
        print("Le combat est terminé.")
        self.running = False

    # MODIF : Nouvelle méthode d'animation de lumière pour les attaques
    def animate_light(self, attacker="player"):
        flash_surface = pygame.Surface(self.screen.get_size())
        # Choix de la couleur selon l'attaquant : blanc pour le joueur, rouge pour le monstre
        flash_color = (255, 255, 255) if attacker == "player" else (255, 0, 0)
        flash_surface.fill(flash_color)
        
        # Animation d'apparition
        for alpha in range(0, 180, 30):
            flash_surface.set_alpha(alpha)
            self.draw_combat_scene()  # Redessine la scène de combat en fond
            self.screen.blit(flash_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)
        
        # Animation de disparition 
        for alpha in range(180, 0, -30):
            flash_surface.set_alpha(alpha)
            self.draw_combat_scene()
            self.screen.blit(flash_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            if self.gauge_active:
                self.update_gauge()
            self.draw_combat_scene()

    def use_object(self, object_id):
        """Utilise un objet unique pour modifier les statistiques du joueur."""
        obj = self.player.inventory.items.get(object_id)

        if obj:
            print(f"Vous utilisez l'objet : {obj.name}")

            hp_boost = obj.attributes.get('healing', 0)
            strength_boost = obj.attributes.get('strength', 0)
            speed_boost = obj.attributes.get('speed', 0)
            accuracy_boost = obj.attributes.get('accuracy', 0)
            protection_boost = obj.attributes.get('protection', 0)

            self.player.hp = min(self.player.hp + hp_boost, self.player.max_hp)
            self.strength += strength_boost
            self.speed += speed_boost
            self.accuracy += accuracy_boost
            self.protection += protection_boost

            print(f"Effets appliqués : +{hp_boost} HP, +{strength_boost} force, +{speed_boost} vitesse, +{accuracy_boost} précision.")

            self.player.inventory.items[object_id] = None
        else:
            print(f"L'objet avec l'ID {object_id} n'est pas disponible ou a déjà été utilisé.")

    def show_dead_screen(self):
        """Affiche l'écran de mort et gère les événements."""
        dead_screen = DeadScreen(self.screen)
        while True:
            dead_screen.draw()
            action = dead_screen.handle_events()

            if action == "retry":
                self.reset_game()  
                break
            elif action == "quit":
                pygame.quit()
                sys.exit()
