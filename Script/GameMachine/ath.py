import pygame

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SEMI_TRANSPARENT_BLACK = (0, 0, 0, 180)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
LIGHT_GREEN = (0, 255, 0)
DARK_GRAY = (40, 40, 40)
YELLOW = (255, 255, 0)  # Couleur pour le niveau
LEVEL_ICON_COLOR = (255, 165, 0)  # Couleur pour l'icône de niveau

# Police
pygame.init()
font = pygame.font.Font(None, 18)  # Taille de police réduite pour le tutoriel
level_font = pygame.font.Font(None, 24)  # Police pour le niveau

# Texte du tutoriel
tutorial_text = [
    "Utilise ZQSD pour te déplacer",
    "Clic gauche pour selectionner",
    "Espace pour attaquer",
    "Tab pour ouvrir l'inventaire"
]

def afficher_ath(screen, player, level, score):
    """Affiche un ATH avec tutoriel, barre de vie, stats du joueur, niveau et score."""
    
    # Dimensions de l'ATH (pour le tutoriel)
    ath_width = 250  
    ath_height = len(tutorial_text) * 30 + 40  

    # Surface semi-transparente pour l'ATH avec bordures arrondies et dégradé
    ath_surface = pygame.Surface((ath_width, ath_height), pygame.SRCALPHA)
    pygame.draw.rect(ath_surface, DARK_GRAY, (0, 0, ath_width, ath_height), border_radius=10)
    for i in range(ath_height):
        pygame.draw.line(ath_surface, 
                         (0, 0, 0, 255 - int(255 * (i / ath_height))),  
                         (0, i), 
                         (ath_width, i))

    screen.blit(ath_surface, (screen.get_width() - ath_width - 10, 10))  

    y_offset = 20

    # Affichage du tutoriel avec ombres et contour
    for line in tutorial_text:
        text_surface = font.render(line, True, WHITE)
        outline_offset = 2
        for dx in [-outline_offset, outline_offset]:
            for dy in [-outline_offset, outline_offset]:
                shadow_surface = font.render(line, True, BLACK)
                screen.blit(shadow_surface, (screen.get_width() - ath_width - 10 + dx, y_offset + dy))
        screen.blit(text_surface, (screen.get_width() - ath_width - 10, y_offset))
        y_offset += 30  

    # Affichage de la barre de vie
    health_bar_width = 200  
    health_bar_height = 25  
    health_ratio = player.hp / player.max_hp

    for i in range(health_bar_width):
        color = (
            int(RED[0] + (LIGHT_GREEN[0] - RED[0]) * health_ratio),
            int(RED[1] + (LIGHT_GREEN[1] - RED[1]) * health_ratio),
            int(RED[2] + (LIGHT_GREEN[2] - RED[2]) * health_ratio)
        )
        pygame.draw.line(screen, color, (20 + i, 20), (20 + i, 20 + health_bar_height), 1)

    pygame.draw.rect(screen, RED, (20, 20, health_bar_width, health_bar_height), border_radius=10)  
    pygame.draw.rect(screen, WHITE, (20, 20, health_bar_width, health_bar_height), 3, border_radius=10)  
    pygame.draw.rect(screen, GREEN, (20, 20, health_bar_width * health_ratio, health_bar_height), border_radius=10)  

    # Affichage du niveau
    level_surface = level_font.render(f"Niveau: {level}", True, YELLOW)  
    level_rect = level_surface.get_rect()
    level_rect.topright = (screen.get_width() - 10, 10 + ath_height + 10)  

    level_background = pygame.Surface((level_rect.width + 10, level_rect.height + 10), pygame.SRCALPHA)
    level_background.fill(SEMI_TRANSPARENT_BLACK)
    screen.blit(level_background, (level_rect.x - 5, level_rect.y - 5))  

    screen.blit(level_surface, level_rect)

    pygame.draw.circle(screen, LEVEL_ICON_COLOR, (level_rect.x - 30, level_rect.centery), 12)  
    pygame.draw.circle(screen, WHITE, (level_rect.x - 30, level_rect.centery), 12, 2)  

    # Affichage du score en dessous du niveau
    score_surface = level_font.render(f"Score: {score}", True, YELLOW)  
    score_rect = score_surface.get_rect()
    score_rect.topright = (screen.get_width() - 10, level_rect.bottom + 5)  

    score_background = pygame.Surface((score_rect.width + 10, score_rect.height + 10), pygame.SRCALPHA)
    score_background.fill(SEMI_TRANSPARENT_BLACK)
    screen.blit(score_background, (score_rect.x - 5, score_rect.y - 5))  

    screen.blit(score_surface, score_rect)
