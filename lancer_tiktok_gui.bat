@echo off
echo Lancement de l'interface TikTok pour Reddit Video Maker...

:: Vérifier si l'environnement virtuel existe
if not exist "venv\Scripts\activate.bat" (
    echo L'environnement virtuel n'existe pas. Exécution de install.bat...
    call install.bat
)

:: Activer l'environnement virtuel et lancer l'interface
call venv\Scripts\activate.bat
python src\tiktok_gui.py

pause