#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reddit Content Selector
-----------------------
Script pour générer des vidéos à partir de différentes catégories de contenu Reddit.
"""

import os
import sys
import subprocess
import argparse
import json
import time
from collections import OrderedDict

# Configuration des catégories de contenu
CONTENT_CATEGORIES = {
    "1": {
        "name": "Actualités Mondiales",
        "description": "Dernières actualités et événements mondiaux",
        "options": [
            {"subreddit": "worldnews", "sorting": "hot", "timeframe": "day", "post_count": 20, "video_count": 5},
            {"subreddit": "news", "sorting": "hot", "timeframe": "day", "post_count": 20, "video_count": 5},
            {"subreddit": "politics", "sorting": "hot", "timeframe": "day", "post_count": 15, "video_count": 3},
            {"subreddit": "geopolitics", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3}
        ]
    },
    "2": {
        "name": "Intelligence Artificielle",
        "description": "Discussions et avancées en IA",
        "options": [
            {"subreddit": "artificial", "sorting": "hot", "timeframe": "week", "post_count": 20, "video_count": 5},
            {"subreddit": "MachineLearning", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "GPT3", "sorting": "hot", "timeframe": "week", "post_count": 15, "video_count": 3}
        ]
    },
    "3": {
        "name": "Développement Web",
        "description": "Programmation et développement fullstack",
        "options": [
            {"subreddit": "webdev", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "programming", "sorting": "hot", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "learnprogramming", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3}
        ]
    },
    "4": {
        "name": "Beauté et Cosmétiques",
        "description": "Produits de beauté, revues et conseils",
        "options": [
            {"subreddit": "MakeupAddiction", "sorting": "hot", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "SkincareAddiction", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "Sephora", "sorting": "hot", "timeframe": "month", "post_count": 15, "video_count": 3}
        ]
    },
    "5": {
        "name": "Humour et Divertissement",
        "description": "Blagues, histoires drôles et contenus divertissants",
        "options": [
            {"subreddit": "jokes", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 5},
            {"subreddit": "funny", "sorting": "hot", "timeframe": "day", "post_count": 15, "video_count": 5},
            {"subreddit": "tifu", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "maliciouscompliance", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3}
        ]
    },
    "6": {
        "name": "Contenu Viral à Fort Engagement",
        "description": "Posts avec le plus fort taux d'engagement",
        "options": [
            {"subreddit": "askreddit", "sorting": "hot", "timeframe": "day", "post_count": 20, "video_count": 5},
            {"subreddit": "amitheasshole", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "unpopularopinion", "sorting": "controversial", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "relationship_advice", "sorting": "hot", "timeframe": "day", "post_count": 15, "video_count": 3}
        ]
    },
    "7": {
        "name": "Conseils et Explications",
        "description": "Conseils pratiques et explications de concepts",
        "options": [
            {"subreddit": "lifeprotips", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "explainlikeimfive", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3},
            {"subreddit": "YouShouldKnow", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3}
        ]
    },
    "8": {
        "name": "Questions les Plus Populaires",
        "description": "Questions qui ont généré le plus de réponses",
        "options": [
            {"subreddit": "askreddit", "sorting": "top", "timeframe": "day", "post_count": 20, "video_count": 5, "comment_sort": "most_comments"},
            {"subreddit": "askreddit", "sorting": "top", "timeframe": "week", "post_count": 20, "video_count": 5, "comment_sort": "most_comments"},
            {"subreddit": "askreddit", "sorting": "top", "timeframe": "month", "post_count": 20, "video_count": 5, "comment_sort": "most_comments"},
            {"subreddit": "nostupidquestions", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3, "comment_sort": "most_comments"},
            {"subreddit": "AskMen", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3, "comment_sort": "most_comments"},
            {"subreddit": "AskWomen", "sorting": "top", "timeframe": "week", "post_count": 15, "video_count": 3, "comment_sort": "most_comments"}
        ]
    }
}

def clear_screen():
    """Efface l'écran du terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Affiche l'en-tête du programme."""
    clear_screen()
    print("\n" + "=" * 60)
    print("  GÉNÉRATEUR DE CONTENU REDDIT  ".center(60))
    print("=" * 60 + "\n")

def print_categories():
    """Affiche les catégories de contenu disponibles."""
    print("Catégories de contenu disponibles :\n")
    for key, category in CONTENT_CATEGORIES.items():
        print(f"{key}. {category['name']} - {category['description']}")
    print("\n0. Quitter\n")

def run_command(args):
    """
    Exécute une commande Python dans un processus séparé.
    
    Args:
        args: Liste des arguments de la commande
    """
    # Chemin absolu vers l'environnement Python
    python_exe = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "venv", "Scripts", "python.exe")
    
    # S'assurer que python_exe existe
    if not os.path.exists(python_exe):
        python_exe = "python"  # Fallback sur python du système
    
    # Construire la commande complète
    full_command = [python_exe] + args
    
    # Convertir la commande en string pour l'affichage
    cmd_str = " ".join(full_command)
    print(f"Exécution de: {cmd_str}")
    
    # Exécuter directement avec os.system pour éviter les problèmes d'entrée/sortie
    return os.system(cmd_str)

def generate_videos(category_key, option_index):
    """
    Génère des vidéos en fonction de la catégorie et de l'option sélectionnées.
    
    Args:
        category_key: Clé de la catégorie sélectionnée
        option_index: Index de l'option sélectionnée dans la catégorie
    """
    if category_key not in CONTENT_CATEGORIES:
        print("Catégorie invalide.")
        return
    
    if option_index >= len(CONTENT_CATEGORIES[category_key]["options"]):
        print("Option invalide.")
        return
    
    selected_option = CONTENT_CATEGORIES[category_key]["options"][option_index]
    
    # Chemin vers le script principal
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    
    # Construire les arguments
    args = [
        script_path,
        f"--subreddit", selected_option["subreddit"],
        f"--sorting", selected_option["sorting"],
        f"--timeframe", selected_option["timeframe"],
        f"--post-count", str(selected_option["post_count"]),
        f"--video-count", str(selected_option["video_count"])
    ]
    
    if "comment_sort" in selected_option:
        args.extend([f"--comment-sort", selected_option["comment_sort"]])
    
    print("\nGénération de vidéos en cours...\n")
    print(f"Subreddit: r/{selected_option['subreddit']}")
    print(f"Tri: {selected_option['sorting']}")
    print(f"Période: {selected_option['timeframe']}")
    print(f"Nombre de posts: {selected_option['post_count']}")
    print(f"Nombre de vidéos: {selected_option['video_count']}")
    if "comment_sort" in selected_option:
        print(f"Tri des commentaires: {selected_option['comment_sort']}")
    print("\nLancement de la génération...\n")
    
    # Exécuter la commande
    result = run_command(args)
    
    if result == 0:
        print("\nLes vidéos ont été générées avec succès !")
    else:
        print(f"\nUne erreur s'est produite lors de la génération des vidéos (code: {result}).")
    
    input("\nAppuyez sur Entrée pour continuer...")

def select_option(category_key):
    """
    Affiche les options disponibles pour une catégorie et laisse l'utilisateur en choisir une.
    
    Args:
        category_key: Clé de la catégorie sélectionnée
    """
    clear_screen()
    category = CONTENT_CATEGORIES[category_key]
    print(f"\n{category['name']} - {category['description']}\n")
    print("Options disponibles :\n")
    
    for i, option in enumerate(category["options"]):
        print(f"{i+1}. r/{option['subreddit']} - Tri: {option['sorting']} - Période: {option['timeframe']}")
    
    print("\n0. Retour\n")
    
    try:
        choice = input("Choisissez une option (0-{}): ".format(len(category["options"])))
        
        if choice == "0":
            return
        
        option_index = int(choice) - 1
        if 0 <= option_index < len(category["options"]):
            generate_videos(category_key, option_index)
        else:
            print("Option invalide. Veuillez réessayer.")
            input("Appuyez sur Entrée pour continuer...")
    except ValueError:
        print("Entrée invalide. Veuillez entrer un nombre.")
        input("Appuyez sur Entrée pour continuer...")
    except EOFError:
        print("Erreur de lecture d'entrée. Retour au menu principal.")
        time.sleep(2)

def main():
    """Fonction principale."""
    try:
        while True:
            print_header()
            print_categories()
            
            try:
                choice = input("Choisissez une catégorie (0-{}): ".format(len(CONTENT_CATEGORIES)))
                
                if choice == "0":
                    clear_screen()
                    print("Merci d'avoir utilisé le Générateur de Contenu Reddit !")
                    break
                
                if choice in CONTENT_CATEGORIES:
                    select_option(choice)
                else:
                    print("Catégorie invalide. Veuillez réessayer.")
                    input("Appuyez sur Entrée pour continuer...")
            except EOFError:
                print("Erreur d'entrée. Sortie du programme.")
                break
            except KeyboardInterrupt:
                print("\nInterruption détectée. Sortie du programme.")
                break
    except Exception as e:
        print(f"Une erreur est survenue: {e}")
        input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
