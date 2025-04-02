import pygame
import sys
from .combat_window import CombatWindow  

class Combat:
    def __init__(self, screen, player, monster, map_obj):
        self.screen = screen
        self.player = player
        self.monster = monster
        self.map_obj = map_obj
        self.font = pygame.font.SysFont(None, 36)
        self.running = True
        self.actions = ["Attaquer", "Fuir"]
        self.selected_action = 0
        self.message = ""

    def draw_combat_window(self):
        self.screen.fill((0, 0, 0))

        # Dessiner les boutons d'action
        button_width, button_height = 200, 50
        button_x = 50  
        button_y_start = (self.screen.get_height() - (button_height + 10) * len(self.actions)) // 2

        for i, action in enumerate(self.actions):
            color = (255, 255, 255) if i == self.selected_action else (150, 150, 150)
            text = self.font.render(action, True, color)
            button_y = button_y_start + i * (button_height + 10)
            self.screen.blit(text, (button_x, button_y))

        # Utiliser la taille réelle du monstre
        monster_display_size = self.monster.size *3
        monster_x = self.screen.get_width() - monster_display_size - 50  
        monster_y = (self.screen.get_height() - monster_display_size) // 2

        # Redimensionner l'image du monstre à sa taille réelle
        monster_image = pygame.transform.scale(
            self.monster.image_left, (monster_display_size, monster_display_size)
        )

        # Dessiner l'image du monstre
        self.screen.blit(monster_image, (monster_x, monster_y))

        # Afficher le message s'il y en a un
        if self.message:
            message_text = self.font.render(self.message, True, (255, 255, 0))
            self.screen.blit(message_text, (self.screen.get_width() // 2 - 100, 500))

        pygame.display.flip()


    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.selected_action = (self.selected_action - 1) % len(self.actions)
        elif keys[pygame.K_DOWN]:
            self.selected_action = (self.selected_action + 1) % len(self.actions)

        if keys[pygame.K_RETURN]:
            self.execute_action()

    def execute_action(self):
        action = self.actions[self.selected_action]
        if action == "Attaquer":
            
            combat_window = CombatWindow(self.screen, self.player, self.monster)
            combat_window.run()
            self.running = False  
            self.message = "Monster Defeated" if self.monster.hp <= 0 else "" 
        elif action == "Fuir":
            self.message = "Vous avez fui !"  
            self.teleport_player_to_bottom()
            self.running = False  
    def teleport_player_to_bottom(self):

        self.player.rect.x = 353
        self.player.rect.y = 550

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            self.draw_combat_window()
