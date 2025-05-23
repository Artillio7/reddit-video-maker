# Script de test pour vérifier l'installation de tkinter et les dépendances
import sys
import os

def check_module(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

print("=== Test des dépendances pour l'interface graphique avec barres de progression ===")
print(f"Python version: {sys.version}")
print(f"Chemin d'exécution: {sys.executable}")
print("\nVérification des modules requis:")

# Liste des modules à vérifier
modules = [
    "tkinter",
    "PIL",  # Pillow
    "cv2",  # OpenCV
    "numpy",
    "praw",
    "tqdm",
    "dotenv",
    "ffmpeg",
    "gtts",
    "pydub",
    "pygame",
    "mutagen"
]

all_modules_installed = True

for module in modules:
    is_installed = check_module(module)
    status = "✓ Installé" if is_installed else "✗ NON INSTALLÉ"
    print(f"  {module}: {status}")
    
    if not is_installed:
        all_modules_installed = False

print("\nRésultat:")
if all_modules_installed:
    print("✓ Toutes les dépendances sont installées correctement!")
    print("  Vous pouvez lancer l'interface graphique avec: python src/launch_video_progress_gui.py")
else:
    print("✗ Certaines dépendances sont manquantes.")
    print("  Exécutez le script repair_venv.bat pour réparer l'installation.")

input("\nAppuyez sur Entrée pour quitter...")