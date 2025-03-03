# Guide d'Installation - Reddit Video Maker

## Prérequis Système

1. **Python**
   - Version 3.8 ou supérieure
   - Peut être téléchargé depuis [python.org](https://www.python.org/downloads/)

2. **FFmpeg**
   - Nécessaire pour le traitement audio/vidéo
   - Installation automatique via le script d'installation

3. **Git** (optionnel)
   - Pour cloner le projet
   - [Télécharger Git](https://git-scm.com/downloads)

## Structure des Dossiers

```
reddit-video-maker/
├── resources/
│   └── music/          # Musique de fond (fichiers .mp3)
├── src/                # Code source
├── temp/              # Fichiers temporaires
├── output/            # Vidéos générées
├── .env              # Configuration
├── requirements.txt   # Dépendances Python
└── installer.bat      # Script d'installation
```

## Installation Automatique

1. **Exécutez `installer.bat`**
   - Crée l'environnement virtuel
   - Installe les dépendances Python
   - Configure le projet

## Installation Manuelle

1. **Créer l'environnement virtuel**
```bash
python -m venv venv
```

2. **Activer l'environnement virtuel**
```bash
# Windows
venv\Scripts\activate
```

3. **Installer les dépendances Python**
```bash
pip install -r requirements.txt
```

## Configuration

1. **Fichier .env**
```env
# Reddit API credentials
REDDIT_CLIENT_ID=votre_client_id
REDDIT_CLIENT_SECRET=votre_client_secret
REDDIT_USER_AGENT=RedditVideoMaker by /u/your_reddit_username

# TTS Engine Configuration
TTS_ENGINE=edge
VOICE_NAME=fr-FR-HenriNeural
LANGUAGE=fr-FR

# Audio Configuration
BACKGROUND_VOLUME=0.2
AUDIO_NORMALIZE=True
AUDIO_DUCK=True

# Video Configuration
VIDEO_FPS=30
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
```

## Dépendances Python

```
praw==7.7.1
Pillow==10.0.0
moviepy==1.0.3
gTTS==2.3.2
pydub==0.25.1
numpy>=1.24.0
sounddevice==0.5.1
soundfile==0.13.1
scipy>=1.11.3
requests>=2.31.0
python-dotenv==1.0.0
```

## Utilisation

1. **Lancer le programme**
```bash
launch.bat
```

## Dépannage

1. **FFmpeg non trouvé**
   - Vérifiez que FFmpeg est installé
   - Vérifiez que FFmpeg est dans le PATH système

2. **Erreurs audio**
   - Vérifiez que les fichiers de musique sont au format MP3
   - Vérifiez que FFmpeg est correctement installé

3. **Erreurs Reddit API**
   - Vérifiez vos identifiants Reddit dans le fichier .env
   - Assurez-vous que votre application Reddit est correctement configurée

## Support

En cas de problème :
1. Vérifiez les logs dans la console
2. Assurez-vous que toutes les dépendances sont installées
3. Vérifiez que les fichiers de configuration sont corrects
