# Guide d'Installation et de Dépannage

## Problème avec l'environnement virtuel

Le message d'erreur que vous avez rencontré indique un problème avec l'installation de pip dans votre environnement virtuel. L'erreur spécifique est :

```
ImportError: cannot import name 'RequirementInformation' from 'pip._vendor.resolvelib.structs'
```

Cette erreur est généralement causée par une installation corrompue de pip ou un conflit de versions dans l'environnement virtuel.

## Solution : Réparer l'environnement virtuel

J'ai créé un script de réparation automatique qui va :
1. Supprimer l'ancien environnement virtuel corrompu
2. Créer un nouvel environnement virtuel propre
3. Installer toutes les dépendances nécessaires
4. Vérifier l'installation de tkinter

### Pour utiliser le script de réparation :

1. Ouvrez une invite de commande PowerShell
2. Naviguez vers le répertoire du projet
3. Exécutez le script de réparation :

```powershell
.\repair_venv.bat
```

## Vérification de tkinter

Tkinter est nécessaire pour l'interface graphique et est inclus dans l'installation standard de Python, mais il n'est pas installable via pip.

Si le script indique que tkinter n'est pas installé, vous devrez réinstaller Python en vous assurant de cocher l'option "tcl/tk and IDLE" lors de l'installation.

## Lancement de l'interface graphique

Après avoir réparé l'environnement virtuel, vous pouvez lancer l'interface graphique avec :

```powershell
python src/launch_video_progress_gui.py
```

## Problèmes courants et solutions

### Erreur "tiktok_gui.py not found"

Le fichier mentionné dans votre terminal (`tiktok_gui.py`) n'existe pas dans le répertoire `src`. Utilisez plutôt :

```powershell
python src/launch_video_progress_gui.py
```

### Problèmes avec OpenCV (cv2)

Si vous rencontrez des erreurs liées à OpenCV, essayez :

```powershell
pip uninstall opencv-python
pip install opencv-python-headless
```

### Autres problèmes

Si vous rencontrez d'autres problèmes après avoir suivi ces étapes, vérifiez :

1. Que Python est correctement installé (version 3.6 ou supérieure recommandée)
2. Que tous les chemins sont correctement configurés dans les variables d'environnement
3. Que vous n'avez pas de conflits avec d'autres installations Python sur votre système

## Fichiers créés ou modifiés

- `src/config.py` : Fichier de configuration manquant nécessaire au fonctionnement de l'interface
- `repair_venv.bat` : Script de réparation automatique de l'environnement virtuel
- `GUIDE_INSTALLATION.md` : Ce guide d'installation et de dépannage