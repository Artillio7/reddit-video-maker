@echo off
echo ======================================
echo = Reddit Video Maker - Test         =
echo ======================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Aller dans le dossier src
cd src

REM Exécuter le script de test
echo Lancement de la création de la vidéo de test...
python create_test_video.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Une erreur est survenue lors de l'exécution du script.
    echo Vérifiez les messages ci-dessus pour plus d'informations.
) else (
    echo.
    echo ======================================
    echo = Création de vidéo terminée avec   =
    echo = succès!                          =
    echo ======================================
)

REM Revenir au dossier parent
cd ..

pause
