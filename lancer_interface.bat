@echo off
echo Lancement de l'interface graphique avec barres de progression
echo =====================================================================

echo Vérification des dépendances...
python test_tkinter.py

echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo Lancement de l'interface graphique...
python src/launch_video_progress_gui.py

pause