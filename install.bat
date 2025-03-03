@echo off
echo ======================================
echo = Installation du Reddit Video Maker =
echo ======================================
echo.

REM Créer l'environnement virtuel s'il n'existe pas
if not exist venv (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Mettre à jour pip
python -m pip install --upgrade pip

REM Installer les dépendances une par une
echo Installation des dependances...
pip install praw==7.7.1
pip install pillow==10.0.0
pip install moviepy==1.0.3
pip install gtts==2.3.2
pip install pydub==0.25.1
pip install numpy>=1.24.0
pip install sounddevice==0.5.1
pip install soundfile==0.13.1
pip install scipy>=1.11.3
pip install requests>=2.31.0
pip install python-dotenv==1.0.0

REM Créer les dossiers nécessaires
if not exist "resources\music" mkdir "resources\music"
if not exist "temp" mkdir "temp"
if not exist "output" mkdir "output"

REM Télécharger FFmpeg
echo Telechargement de FFmpeg...
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

REM Extraire FFmpeg
echo Extraction de FFmpeg...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'C:\ffmpeg' -Force"

REM Ajouter FFmpeg au PATH
setx PATH "%PATH%;C:\ffmpeg\bin"

REM Nettoyer
del ffmpeg.zip

echo.
echo ======================================
echo = Installation terminee avec succes! =
echo ======================================
echo.
echo Pour creer une video, utilisez la commande:
echo    launch.bat
echo.

pause
