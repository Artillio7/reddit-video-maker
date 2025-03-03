@echo off
echo ======================================
echo = Test de la structure du projet    =
echo ======================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Aller dans le dossier src
cd src

REM Exécuter le script de test
python test_structure.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Des problèmes ont été détectés dans la structure du projet.
    echo Veuillez corriger les erreurs avant d'utiliser le générateur de vidéos.
) else (
    echo.
    echo ======================================
    echo = Structure du projet validée       =
    echo = Vous pouvez utiliser launch.bat   =
    echo ======================================
)

REM Revenir au dossier parent
cd ..

pause
