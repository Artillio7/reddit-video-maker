@echo off
echo ======================================
echo = Reddit Video Maker               =
echo ======================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Aller dans le dossier src
cd src

REM Exécuter le script principal
echo Lancement de la création de vidéo...
python main.py %*

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
