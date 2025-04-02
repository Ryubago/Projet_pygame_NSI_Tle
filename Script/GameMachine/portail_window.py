import pygame
import sys
import time
import json
import random
from PIL import Image
import path_config

class PortalWindow:
    def __init__(self, screen, niveau):
        self.screen = screen
        self.niveau = niveau  # Instance de Niveau pour la gestion des niveaux
        self.base_texture_path = path_config.get_base_texture_path() + "Sprite/Space Background.png"
        self.font = pygame.font.SysFont('Arial', 36)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.running = True
        self.gif_path = path_config.get_base_texture_path() + "video/giphy.webp"

        # Charger le GIF avec Pillow
        self.gif = Image.open(self.gif_path)
        self.frames = []
        self.frame_durations = []
        
        screen_width, screen_height = self.screen.get_size()
        try:
            while True:
                frame = self.gif.copy()
                frame = frame.resize((screen_width, screen_height), Image.LANCZOS)
                self.frames.append(pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha())
                self.frame_durations.append(self.gif.info['duration'])
                self.gif.seek(self.gif.tell() + 1)
        except EOFError:
            pass

        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()

        
        # Variables pour l'énigme
        self.riddle_text = ""
        self.user_answer = ""
        self.show_riddle = False
        self.riddles = self.load_riddles()
        self.current_riddle = self.get_random_riddle()
        self.background_image = pygame.image.load(self.base_texture_path)
        self.background_image = pygame.transform.scale(self.background_image, (screen_width, screen_height))

        # Message de feedback pour la réponse
        self.feedback_message = ""
        self.feedback_time = 0
        self.feedback_displayed = False

    def load_riddles(self):
        # Construire un chemin dynamique pour `énigme.json`
        riddle_path = path_config.get_base_texture_path() + "data/énigme.json"
        try:
            with open(riddle_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erreur : le fichier {riddle_path} est introuvable.")
            return []


    def get_random_riddle(self):
        return random.choice(self.riddles)

    def wrap_text(self, text, width):
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            if self.font.size(current_line + word)[0] <= width:
                current_line += (word + ' ')
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines

    def draw(self):
        if not self.show_riddle:
            self.screen.fill((0, 0, 0))
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time > self.frame_durations[self.current_frame_index]:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
                self.last_frame_time = current_time

            frame = self.frames[self.current_frame_index]
            self.screen.blit(frame, (0, 0))
            pygame.display.flip()
        else:
            self.screen.blit(self.background_image, (0, 0))

            riddle_lines = self.wrap_text(self.current_riddle['riddle'], self.screen.get_width() - 40)
            max_text_width = max(self.font.size(line)[0] for line in riddle_lines)
            text_box_width = max_text_width + 40
            text_box_height = len(riddle_lines) * (self.font.get_height() + 5) + 20

            text_box_x = self.screen.get_width() // 2 - text_box_width // 2
            text_box_y = self.screen.get_height() // 2 - text_box_height // 2

            pygame.draw.rect(self.screen, (0, 0, 0), (text_box_x, text_box_y, text_box_width, text_box_height))
            y_offset = text_box_y + 10
            for line in riddle_lines:
                riddle_surface = self.font.render(line, True, (255, 255, 255))
                shadow_surface = self.font.render(line, True, (0, 0, 0))
                self.screen.blit(shadow_surface, 
                                (text_box_x + (text_box_width - riddle_surface.get_width()) // 2 + 2, y_offset + 2))
                self.screen.blit(riddle_surface, 
                                (text_box_x + (text_box_width - riddle_surface.get_width()) // 2, y_offset))
                y_offset += self.font.get_height() + 5

            answer_surface = self.font_small.render(self.user_answer, True, (255, 255, 0))
            pygame.draw.rect(self.screen, (255, 255, 255), 
                            (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 + len(riddle_lines) * 40, 200, 40), 2)
            self.screen.blit(answer_surface, 
                            (self.screen.get_width() // 2 - 90, self.screen.get_height() // 2 + len(riddle_lines) * 40 + 5))

            if self.feedback_message:
                feedback_surface = self.font_small.render(self.feedback_message, True, (255, 255, 255))
                self.screen.blit(feedback_surface, 
                                (self.screen.get_width() // 2 - feedback_surface.get_width() // 2, 
                                 self.screen.get_height() // 2 + len(riddle_lines) * 40 + 50))

            pygame.display.flip()

    def run(self):
        start_time = time.time()
        while self.running:
            current_time = time.time()
            
            if not self.show_riddle and current_time - start_time > 8:
                self.show_riddle = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if self.show_riddle and not self.feedback_displayed:
                        if event.key == pygame.K_RETURN:
                            if self.user_answer.lower() == self.current_riddle['answer'].lower():
                                self.feedback_message = "Réponse correcte !"
                                self.niveau.avancer_niveau()  # Avancer au niveau suivant en cas de bonne réponse
                            else:
                                self.feedback_message = f"Réponse incorrecte ! La bonne réponse était : {self.current_riddle['answer']}"
                            
                            self.feedback_time = time.time()
                            self.feedback_displayed = True
                            self.user_answer = ""  
                        elif event.key == pygame.K_BACKSPACE:
                            self.user_answer = self.user_answer[:-1]
                        else:
                            self.user_answer += event.unicode

            if self.feedback_displayed and time.time() - self.feedback_time > 3:
                self.running = False

            self.draw()
