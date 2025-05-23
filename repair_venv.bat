@echo off
echo Réparation de l'environnement virtuel pour l'interface graphique avec barres de progression
echo =====================================================================

echo 1. Suppression de l'ancien environnement virtuel (si existant)...
rmdir /s /q venv

echo 2. Création d'un nouvel environnement virtuel...
python -m venv venv

echo 3. Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo 4. Mise à jour de pip...
python -m pip install --upgrade pip

echo 5. Installation des dépendances requises...
pip install opencv-python pillow praw tqdm python-dotenv ffmpeg-python gTTS pydub pygame mutagen numpy

echo 6. Vérification de l'installation de tkinter...
python -c "import tkinter; print('Tkinter est correctement installé!')" || echo "ERREUR: Tkinter n'est pas installé. Veuillez réinstaller Python en cochant l'option 'tcl/tk and IDLE'."

echo =====================================================================
echo Installation terminée! Pour lancer l'interface graphique, exécutez:
echo python src/launch_video_progress_gui.py
echo =====================================================================

pause