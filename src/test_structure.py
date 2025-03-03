#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de la structure du projet et des dépendances
"""

import os
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_imports():
    """Teste les imports des modules du projet"""
    try:
        import config
        logging.info("✓ Module config importé avec succès")
    except ImportError as e:
        logging.error(f"✗ Erreur d'importation du module config: {e}")
        return False
    
    try:
        from utils.modern_audio import ModernAudioMaker
        logging.info("✓ Module modern_audio importé avec succès")
    except ImportError as e:
        logging.error(f"✗ Erreur d'importation du module modern_audio: {e}")
        return False
    
    try:
        from utils.modern_video import TikTokVideoMaker
        logging.info("✓ Module modern_video importé avec succès")
    except ImportError as e:
        logging.error(f"✗ Erreur d'importation du module modern_video: {e}")
        return False
    
    try:
        from utils.modern_captions import ModernCaptionMaker
        logging.info("✓ Module modern_captions importé avec succès")
    except ImportError as e:
        logging.error(f"✗ Erreur d'importation du module modern_captions: {e}")
        return False
    
    try:
        from utils.redditScrape import RedditScraper
        logging.info("✓ Module redditScrape importé avec succès")
    except ImportError as e:
        logging.error(f"✗ Erreur d'importation du module redditScrape: {e}")
        return False
    
    return True

def test_resources():
    """Teste l'accès aux ressources du projet"""
    base_dir = Path(__file__).parent.parent
    
    resources = [
        ("Musique", base_dir / "resources" / "music"),
        ("Polices", base_dir / "resources" / "fonts"),
        ("Arrière-plans", base_dir / "resources" / "backgrounds"),
        ("Icônes", base_dir / "resources" / "icons")
    ]
    
    all_ok = True
    
    for name, path in resources:
        if path.exists():
            count = len(list(path.glob('*')))
            logging.info(f"✓ Ressource {name} trouvée avec {count} fichiers")
        else:
            logging.error(f"✗ Ressource {name} introuvable: {path}")
            all_ok = False
    
    return all_ok

def test_structure():
    """Teste la structure générale du projet"""
    base_dir = Path(__file__).parent.parent
    
    # Vérifier les dossiers essentiels
    folders = [
        ("src", base_dir / "src"),
        ("utils", base_dir / "src" / "utils"),
        ("output", base_dir / "output"),
        ("resources", base_dir / "resources"),
        ("temp", base_dir / "temp")
    ]
    
    all_ok = True
    
    for name, path in folders:
        if path.exists():
            logging.info(f"✓ Dossier {name} trouvé")
        else:
            logging.error(f"✗ Dossier {name} introuvable: {path}")
            all_ok = False
    
    # Vérifier les fichiers essentiels
    files = [
        ("Configuration", base_dir / "src" / "config.py"),
        ("Script principal", base_dir / "src" / "main.py"),
        ("Environnement", base_dir / ".env"),
        ("README", base_dir / "README.md")
    ]
    
    for name, path in files:
        if path.exists():
            logging.info(f"✓ Fichier {name} trouvé")
        else:
            logging.error(f"✗ Fichier {name} introuvable: {path}")
            all_ok = False
    
    return all_ok

def main():
    """Fonction principale de test"""
    logging.info("=== Test de la structure du projet ===")
    structure_ok = test_structure()
    
    logging.info("\n=== Test des imports ===")
    imports_ok = test_imports()
    
    logging.info("\n=== Test des ressources ===")
    resources_ok = test_resources()
    
    if structure_ok and imports_ok and resources_ok:
        logging.info("\n✅ Tous les tests sont passés avec succès")
        logging.info("La structure du projet est correcte et prête à l'utilisation")
        return 0
    else:
        logging.error("\n❌ Certains tests ont échoué")
        logging.error("Veuillez corriger les erreurs ci-dessus avant d'utiliser le projet")
        return 1

if __name__ == "__main__":
    sys.exit(main())
