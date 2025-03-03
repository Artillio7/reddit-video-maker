# Reddit Video Maker - Version Améliorée

Ce projet permet de générer automatiquement des vidéos à partir de posts Reddit, avec des fonctionnalités audio et visuelles améliorées.

## Structure du Projet

```
reddit-video-maker-main/
├── askreddit/                     # Code principal du projet
│   ├── utils/                    # Modules utilitaires
│   │   ├── modern_audio.py       # Gestion audio améliorée
│   │   ├── modern_captions.py    # Création de sous-titres modernes
│   │   ├── modern_video.py       # Création vidéo améliorée
│   │   └── redditScrape.py       # Scraping de Reddit
│   ├── config.py                 # Configuration du projet
│   └── modern_main.py            # Script principal
├── bg_vids/                       # Vidéos d'arrière-plan
├── fonts/                         # Polices utilisées
├── music/                         # Musique de fond
├── output/                        # Dossier de sortie des vidéos
├── pfp/                           # Images de profil
├── subreddit_icon/                # Icônes des subreddits
└── .env                           # Variables d'environnement (API keys)
```

## Fonctionnalités

1. **Structure Organisée** : Chaque sujet/post possède son propre dossier unique contenant des sous-dossiers pour les titres, commentaires, audio et vidéos.

2. **Gestion Audio Améliorée**:
   - Normalisation audio
   - Effet de "ducking" (réduction du volume de la musique quand il y a de la voix)
   - Conversion automatique des fichiers MP3 en WAV
   - Paramètres de mixage configurables

3. **Effets Vidéo**:
   - Animations et effets de zoom
   - Transition entre les éléments visuels
   - Meilleure synchronisation audio/vidéo

4. **Interface Visuelle**:
   - Cartes de titre et commentaires améliorées
   - Effets visuels modernes (ombres, dégradés, badges)
   - Indicateurs de position des commentaires

## Utilisation

Pour créer une nouvelle vidéo, il suffit d'exécuter le fichier batch `creer_video.bat` qui lancera le processus complet.

## Configuration

Tous les paramètres sont configurables dans le fichier `askreddit/config.py`, notamment:
- Les paramètres de Reddit
- Les dimensions de la vidéo
- Les paramètres audio
- Les chemins des dossiers
