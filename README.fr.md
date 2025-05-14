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
└── .env                           # Variables d'environnement (API keys)
```

## Licence
MIT License
