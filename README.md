# Reddit Video Maker

## 🎬 Point d'entrée principal

Lancez **exclusivement** le projet via :

```bash
python src/main.py [options]
```

- `src/main.py` est le **seul main officiel**.
- Tous les autres scripts (ex : `modern_main.py`, `mock_data.py`) sont obsolètes ou supprimés.

## 🔗 Dépendances
- API Reddit (nécessite des identifiants valides dans `.env`)
- Voir `requirements.txt` pour les dépendances Python.

## 🚀 Exemples d'utilisation

```bash
python src/main.py --subreddit news --post-count 20 --video-count 3
```

## 📦 Structure du projet
- `src/main.py` : orchestrateur principal (scraping, audio, vidéo, etc.)
- `src/utils/` : modules utilitaires (scraping, audio, etc.)
- `.env` : variables d'environnement (Reddit API)
- `output/` : vidéos générées

## 🛑 Notes
- **modern_main.py** et **mock_data.py** sont obsolètes/supprimés.
- Le projet ne fonctionne qu'avec des données Reddit réelles (plus de fallback mock).

## 🔒 Sécurité
- Ne partagez jamais vos identifiants Reddit en dur dans le code ou publiquement.
- Changez votre mot de passe Reddit après vos tests si besoin.


This project scrapes Reddit posts and comments and generates audio from the selected content. The project is streamlined to focus on scraping and audio generation only.

## Features
- Scrape posts and comments from Reddit
- Generate audio (TTS) from Reddit comments
- Multiple content categories and subreddit options
- Easy setup and launch via batch scripts

## Requirements
- Python 3.8+
- Reddit API credentials (see `.env.example`)
- FFmpeg (for audio processing)

## Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your Reddit API credentials
4. (Optional) Install FFmpeg if not already installed

## Usage
- To launch the content selector: `launch_content_selector.bat`
- To run the main script directly: `python src/main.py --help`

## Directory Structure
- `src/`: Main source code (scraping & audio)
- `resources/`: Fonts, music, backgrounds, icons
- `output/`: Generated audio and data
- `temp/`: Temporary files

Le script principal accepte plusieurs paramètres pour personnaliser la génération de vidéos :

```bash
python src/main.py --subreddit askreddit --post-count 15 --video-count 5 --sorting hot
```

### Paramètres disponibles

- `--subreddit` : Le subreddit à scraper (ex: askreddit, todayilearned, etc.)
- `--post-count` : Nombre de posts à récupérer (défaut: 15)
- `--video-count` : Nombre de vidéos à générer (défaut: 5)
- `--sorting` : Méthode de tri des posts (hot, new, top, rising, controversial)
- `--timeframe` : Période pour le tri (hour, day, week, month, year, all)
- `--allow-nsfw` : Permet les posts NSFW (désactivé par défaut)
- `--output-dir` : Dossier de sortie personnalisé

## Structure du Scraping

Le scraping est géré par `redditScrape.py` qui :

1. Se connecte à l'API Reddit en mode lecture seule
2. Récupère les posts selon les critères spécifiés
3. Filtre les posts selon :
   - Longueur minimale du titre
   - Présence de commentaires
   - Contenu non NSFW (sauf si --allow-nsfw)
4. Extrait pour chaque post :
   - Titre
   - Auteur
   - Score
   - URL
   - Top commentaires
5. Extrait et télécharge les médias des commentaires :
   - Images (jpg, png, gif, etc.)
   - Vidéos (mp4, webm, etc.)
   - Stockage dans la structure de dossiers du projet

## Fonctionnalités Spéciales

### Extraction de Médias

Le projet est capable d'extraire et d'afficher les médias inclus dans les commentaires Reddit :

- Les URLs d'images et de vidéos sont détectées dans les commentaires
- Les images sont automatiquement téléchargées et intégrées dans les cartes de commentaires
- Les URLs sont supprimées du texte pour la synthèse vocale
- Support des domaines populaires : i.redd.it, v.redd.it, imgur.com, etc.

### Structure des Fichiers

Les fichiers générés sont organisés comme suit :

- `output/[post_id]/` - Dossier principal pour chaque post
  - `audio/` - Fichiers audio (titre, commentaires)
  - `images/` - Images générées (titre, commentaires)
    - `comments_media/` - Images extraites des commentaires
  - `video/` - Fichiers vidéo
    - `comments_media/` - Vidéos extraites des commentaires
  - `final_video.mp4` - Vidéo finale générée

## Exemples de Subreddits Populaires

- r/AskReddit - Questions et réponses variées
- r/todayilearned - Faits intéressants
- r/explainlikeimfive - Explications simplifiées
- r/showerthoughts - Pensées originales
- r/LifeProTips - Conseils utiles
- r/AskHistorians - Questions historiques
- r/science - Actualités scientifiques

## Maintenance

Les vidéos générées sont sauvegardées dans le dossier `output/` avec un format de nom incluant :
- Le subreddit
- Le début du titre
- La date et l'heure

Les fichiers temporaires sont automatiquement nettoyés après la génération.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
