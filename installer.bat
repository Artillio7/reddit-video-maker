@echo off
echo ======================================
echo = Installation du Reddit Video Maker =
echo ======================================
echo.

REM Exécuter le script PowerShell d'installation
powershell -ExecutionPolicy Bypass -File install_dependencies.ps1

echo.
echo ======================================
echo = Installation terminée avec succès! =
echo ======================================
echo.
echo Pour créer une vidéo, utilisez la commande:
echo    launch.bat
echo.

pause
