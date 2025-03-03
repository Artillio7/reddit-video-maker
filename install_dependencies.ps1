# Script d'installation des dépendances pour Reddit Video Maker
Write-Host "Installation des dépendances pour Reddit Video Maker..." -ForegroundColor Green

# Fonction pour vérifier si une commande existe
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Vérifier et installer FFmpeg
if (-not (Test-Command "ffmpeg")) {
    Write-Host "Installation de FFmpeg..." -ForegroundColor Yellow
    
    # Créer le dossier FFmpeg s'il n'existe pas
    $ffmpegPath = "C:\ffmpeg"
    if (-not (Test-Path $ffmpegPath)) {
        New-Item -ItemType Directory -Path $ffmpegPath | Out-Null
    }
    
    # Télécharger FFmpeg
    $ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    $ffmpegZip = "ffmpeg.zip"
    
    Write-Host "Téléchargement de FFmpeg..."
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip
    
    # Extraire FFmpeg
    Write-Host "Extraction de FFmpeg..."
    Expand-Archive -Path $ffmpegZip -DestinationPath $ffmpegPath -Force
    
    # Déplacer les fichiers au bon endroit
    Get-ChildItem -Path "$ffmpegPath\ffmpeg-*\bin" | Copy-Item -Destination "$ffmpegPath\bin" -Recurse -Force
    
    # Ajouter FFmpeg au PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*C:\ffmpeg\bin*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;C:\ffmpeg\bin", "User")
    }
    
    # Nettoyer
    Remove-Item $ffmpegZip -Force
    Write-Host "FFmpeg installé avec succès!" -ForegroundColor Green
}

# Vérifier la version de Python
$pythonVersion = python --version 2>&1
if (-not $pythonVersion -like "*Python 3.*") {
    Write-Host "Python 3.8 ou supérieur est requis. Veuillez l'installer depuis python.org" -ForegroundColor Red
    exit 1
}

# Créer l'environnement virtuel s'il n'existe pas
if (-not (Test-Path "venv")) {
    Write-Host "Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
}

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Installer/Mettre à jour pip
Write-Host "Mise à jour de pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Installer les dépendances Python
Write-Host "Installation des dépendances Python..." -ForegroundColor Yellow
pip install -r requirements.txt

# Créer les dossiers nécessaires
$folders = @("resources\music", "temp", "output")
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        Write-Host "Création du dossier $folder..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
}

# Vérifier si le fichier .env existe
if (-not (Test-Path ".env")) {
    Write-Host "Création du fichier .env exemple..." -ForegroundColor Yellow
    @"
# Configuration Reddit API
REDDIT_CLIENT_ID=votre_client_id
REDDIT_CLIENT_SECRET=votre_client_secret
REDDIT_USER_AGENT=script:reddit-video-maker:v1.0 (by /u/votre_username)
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Veuillez éditer le fichier .env avec vos identifiants Reddit API" -ForegroundColor Yellow
}

Write-Host "`nInstallation terminée!" -ForegroundColor Green
Write-Host "Pour générer des vidéos, utilisez la commande:" -ForegroundColor Cyan
Write-Host "python src/main.py --subreddit askreddit --post-count 15 --video-count 5 --sorting hot" -ForegroundColor White
