# Guide d'utilisation de l'interface TikTok pour Reddit Video Maker

## Introduction

L'interface TikTok pour Reddit Video Maker est un outil qui vous permet de créer facilement des vidéos au format TikTok à partir de contenus Reddit. Cette interface graphique offre des options spécifiques pour optimiser vos vidéos pour la plateforme TikTok.

## Installation

Aucune installation supplémentaire n'est nécessaire si vous avez déjà configuré Reddit Video Maker. Si ce n'est pas le cas, suivez les instructions dans le fichier `INSTALLATION.md` à la racine du projet.

## Lancement de l'interface

Pour lancer l'interface TikTok, vous avez deux options :

### Option 1 : Utiliser le fichier batch

Double-cliquez simplement sur le fichier `lancer_tiktok_gui.bat` à la racine du projet. Ce fichier batch activera automatiquement l'environnement virtuel et lancera l'interface.

### Option 2 : Via la ligne de commande

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\activate

# Lancer l'interface TikTok
python src\tiktok_gui.py
```

## Utilisation de l'interface

L'interface TikTok propose plusieurs options spécifiques :

1. **Configuration de base** :
   - Subreddit : le subreddit à partir duquel extraire le contenu (par défaut : askreddit)
   - Période : la période de temps pour le tri des posts (hour, day, week, month, year, all)
   - Nombre de posts : combien de posts traiter (1-5)
   - Nombre de commentaires : combien de commentaires inclure par post (3-20)

2. **Options TikTok** :
   - Format vertical (9:16) : optimisé pour TikTok
   - Ajouter musique de fond : inclut une musique de fond dans la vidéo
   - Ajouter effets visuels : ajoute des transitions et effets visuels

3. **Prévisualisation** :
   - La partie gauche de l'interface affiche une prévisualisation en temps réel des images générées

4. **Progression** :
   - Des barres de progression indiquent l'avancement de chaque étape

## Résolution des problèmes

Si vous rencontrez des erreurs lors de l'utilisation de l'interface TikTok :

1. Vérifiez que tous les fichiers nécessaires sont présents dans le répertoire `src`
2. Assurez-vous que l'environnement virtuel est correctement configuré
3. Consultez les logs dans le fichier `reddit_video_maker.log`

## Remarque

Les vidéos générées seront sauvegardées dans le dossier `output` avec un préfixe `tiktok_video_` suivi de la date et l'heure de création.