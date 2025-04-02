class Niveau:
    def __init__(self):
        self.level = 1
        self.level_max = 5  # Niveau maximum

    def avancer_niveau(self):
        """Avance au niveau suivant, jusqu'au niveau max"""
        if self.level < self.level_max:
            self.level += 1
            print(f"Vous avez atteint le niveau {self.level} !")
        else:
            print("Vous avez atteint le niveau maximum. Vous ne pouvez pas aller plus loin")

    def reset_niveau(self):
        """Réinitialise le niveau."""
        self.level = 1
        print("Niveau réinitialisé au niveau 1.")

    def obtenir_niveau(self):
        """Retourne le niveau actuel."""
        return self.level
