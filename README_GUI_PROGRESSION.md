# Interface Graphique avec Barres de Progression pour Générateur de Vidéos Reddit

Cette extension ajoute une interface graphique avec des barres de progression pour suivre l'avancement de la génération de vidéos Reddit.

## Fonctionnalités

- Affichage des barres de progression pour chaque étape de la génération de vidéos
- Prévisualisation des images générées en temps réel
- Configuration des paramètres de génération (subreddit, période, nombre de posts)
- Suivi en pourcentage de l'avancement de chaque étape

## Installation des dépendances

Avant d'utiliser l'interface graphique, assurez-vous d'avoir installé toutes les dépendances nécessaires :

```bash
pip install opencv-python pillow
```

**Note importante** : tkinter est inclus dans l'installation standard de Python et ne peut pas être installé via pip. Si vous recevez une erreur concernant tkinter, c'est que votre installation Python n'inclut pas ce module par défaut.

Si vous utilisez un environnement virtuel, activez-le d'abord :

```bash
# Sur Windows
.\venv\Scripts\activate

# Sur Linux/Mac
source venv/bin/activate
```

## Utilisation

Pour lancer l'interface graphique avec les barres de progression :

```bash
python src/launch_video_progress_gui.py
```

## Structure des fichiers

- `video_progress_gui.py` : Interface graphique principale avec les barres de progression
- `launch_video_progress_gui.py` : Script de lancement avec configuration avancée
- `silent_video_creator.py` : Générateur de vidéos modifié pour supporter les callbacks de progression

## Comment ça fonctionne

L'interface graphique est divisée en deux parties principales :

1. **Zone de prévisualisation** (à gauche) : Affiche l'image en cours de traitement
2. **Zone de progression** (à droite) : Affiche les barres de progression pour chaque étape

Les étapes suivies sont :
1. Récupération des posts Reddit
2. Création de l'image du titre
3. Création des images de commentaires
4. Génération de la vidéo
5. Transitions et effets
6. Finalisation

Chaque étape est représentée par une barre de progression qui se met à jour en temps réel pendant le processus de génération.

## Personnalisation

Vous pouvez personnaliser les paramètres de génération directement dans l'interface :

- **Subreddit** : Le subreddit à partir duquel récupérer les posts
- **Période** : La période de temps pour les posts (jour, semaine, mois, etc.)
- **Nombre de posts** : Le nombre de posts à traiter

## Dépannage

Si vous rencontrez des erreurs liées aux modules manquants, assurez-vous d'avoir installé toutes les dépendances requises.

Pour les problèmes liés à OpenCV (cv2), vous pouvez essayer :

```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

Pour les problèmes liés à tkinter :

- **Windows** : Tkinter est normalement inclus dans l'installation standard de Python. Si ce n'est pas le cas, réinstallez Python en vous assurant de cocher l'option "tcl/tk and IDLE" lors de l'installation.

- **Linux** : Sur certaines distributions Linux, vous devrez peut-être installer tkinter séparément :
  ```bash
  # Pour Debian/Ubuntu
  sudo apt-get install python3-tk
  
  # Pour Fedora
  sudo dnf install python3-tkinter
  
  # Pour Arch Linux
  sudo pacman -S tk
  ```

- **macOS** : Si vous utilisez Homebrew, assurez-vous d'installer Python avec l'option tkinter :
  ```bash
  brew install python-tk
  ```

- **Vérification de l'installation** : Pour vérifier si tkinter est correctement installé, exécutez cette commande dans votre terminal :
  ```bash
  python -c "import tkinter; tkinter._test()"
  ```
  Une fenêtre devrait s'ouvrir si tkinter est correctement installé.