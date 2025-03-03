@echo off
setlocal enabledelayedexpansion

echo Reddit Video Maker - Demarrage rapide
echo.

rem Verifier si Python est installe
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Python 3.7 ou superieur.
    pause
    exit /b 1
)

rem Verifier si c'est la premiere execution
if not exist "venv" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installation des dependances...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Erreur lors de l'installation des dependances.
        pause
        exit /b 1
    )
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Choisissez une operation:
echo 1 - Generer des videos
echo 2 - Nettoyer les dossiers vides
echo 3 - Quitter
echo.

set /p choix=Votre choix (1-3): 

if "%choix%"=="1" (
    echo.
    echo Entrez le nom du subreddit (par defaut: AskReddit):
    set /p subreddit=Subreddit: 
    if "!subreddit!"=="" set subreddit=AskReddit
    
    echo.
    echo Entrez le nombre de posts a recuperer (par defaut: 5):
    set /p count=Nombre de posts: 
    if "!count!"=="" set count=5
    
    echo.
    echo Choisissez le mode de tri:
    echo 1 - Hot (Populaire)
    echo 2 - Top
    echo 3 - New (Nouveau)
    echo 4 - Rising (En hausse)
    set /p mode=Mode (1-4): 
    
    set sort=hot
    if "!mode!"=="2" set sort=top
    if "!mode!"=="3" set sort=new
    if "!mode!"=="4" set sort=rising
    
    echo.
    echo Parametres de generation:
    echo - Subreddit: !subreddit!
    echo - Nombre de posts: !count!
    echo - Mode de tri: !sort!
    echo.
    
    python src\main.py --subreddit !subreddit! --post-count !count! --sorting !sort!

) else if "%choix%"=="2" (
    echo.
    echo Nettoyage des dossiers vides...
    python src\main.py --cleanup
    
) else (
    echo Au revoir!
    exit /b 0
)

pause
