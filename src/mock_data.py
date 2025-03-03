#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Données fictives pour tester la création de vidéos sans connexion à l'API Reddit
"""

mock_post = {
    "title": "Quel est le conseil le plus important que vous donneriez à quelqu'un qui commence à programmer ?",
    "author": "ProgrammeurCurieux",
    "url": "https://www.reddit.com/r/programmation/comments/sample",
    "score": 1542,
    "created_utc": 1645500000,
    "comments": [
        {
            "body": "Apprenez les bases solides avant de vous lancer dans des frameworks. Les langages changent, les frameworks meurent, mais les concepts fondamentaux restent les mêmes.",
            "author": "DeveloppeurExperimente",
            "score": 328,
            "created_utc": 1645501000
        },
        {
            "body": "N'ayez pas peur de faire des erreurs, c'est comme ça qu'on apprend. La programmation, c'est 80% de débogage et 20% d'écriture de code.",
            "author": "BugHunter42",
            "score": 251,
            "created_utc": 1645502000
        },
        {
            "body": "Utilisez Git dès le début. Même pour vos petits projets personnels. Vous me remercierez plus tard quand vous ferez une erreur et que vous pourrez revenir en arrière facilement.",
            "author": "GitMaster",
            "score": 199,
            "created_utc": 1645503000
        },
        {
            "body": "Écrivez du code lisible. Le code que vous écrivez aujourd'hui, vous (ou quelqu'un d'autre) le lirez dans six mois. Utilisez des noms de variables et de fonctions clairs, commentez votre code quand c'est nécessaire.",
            "author": "CleanCoder",
            "score": 187,
            "created_utc": 1645504000
        },
        {
            "body": "Prenez le temps de comprendre les structures de données et les algorithmes. Ce sont des outils qui vous serviront quel que soit le langage ou le domaine dans lequel vous travaillez.",
            "author": "AlgoExpert",
            "score": 143,
            "created_utc": 1645505000
        }
    ]
}

def get_mock_posts(count=1):
    """Retourne une liste de posts fictifs pour les tests"""
    posts = []
    for i in range(count):
        # Créer une copie du post pour éviter les références partagées
        post_copy = mock_post.copy()
        post_copy["title"] = f"{post_copy['title']} - Version {i+1}"
        posts.append(post_copy)
    return posts
