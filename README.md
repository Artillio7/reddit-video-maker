# Reddit Video Maker

Un outil automatisé pour créer des vidéos TikTok à partir de contenu Reddit.

## Configuration requise

- Python 3.8 ou supérieur
- FFmpeg installé et accessible dans le PATH
- Un compte Reddit (pour les identifiants API)

## Installation

1. Cloner le repository
2. Exécuter `installer.bat` ou `install_dependencies.ps1` pour installer toutes les dépendances
3. Créer un fichier `.env` avec vos identifiants Reddit (voir Configuration)

## Configuration

Créez un fichier `.env` à la racine du projet avec les informations suivantes :

```env
REDDIT_CLIENT_ID=votre_client_id
REDDIT_CLIENT_SECRET=votre_client_secret
REDDIT_USER_AGENT=votre_user_agent
```

## Utilisation

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
