@echo off
title Générateur de Contenu Reddit
mode con: cols=100 lines=40
color 0A

echo ============================================================
echo                GÉNÉRATEUR DE CONTENU REDDIT                
echo ============================================================
echo.
echo Lancement du sélecteur de contenu Reddit...
echo.

cd /d "%~dp0"

REM Vérifier si l'environnement virtuel existe
if not exist "venv\Scripts\python.exe" (
    echo L'environnement virtuel n'existe pas.
    echo Exécution du script d'installation...
    call install_dependencies.ps1
)

REM Lancer le sélecteur de contenu
.\venv\Scripts\python.exe src\content_selector.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Une erreur s'est produite lors de l'exécution du script.
    echo Code d'erreur: %ERRORLEVEL%
)

echo.
echo Merci d'avoir utilisé le Générateur de Contenu Reddit !
pause
