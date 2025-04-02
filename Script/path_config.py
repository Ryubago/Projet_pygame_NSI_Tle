import os

def get_base_texture_path():
    """Retourne automatiquement le chemin du dossier Asset."""
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Chemin du script en cours
    project_dir = os.path.dirname(script_dir)  # Remonte d'un niveau pour atteindre le dossier du projet
    asset_path = os.path.join(project_dir, "Asset")  # Construit le chemin vers le dossier Asset
    return os.path.join(asset_path, '')  # Ajoute un séparateur final si nécessaire

# Test d'affichage
print(get_base_texture_path())
