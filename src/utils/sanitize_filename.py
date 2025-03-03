"""
Module pour la sanitisation des noms de fichiers.
"""

import re
import logging

def sanitize_filename(filename):
    """
    Sanitize le nom de fichier en remplaçant les caractères interdits.
    
    Args:
        filename: Le nom de fichier à nettoyer
        
    Returns:
        Le nom de fichier nettoyé
    """
    if not filename:
        return "untitled"
        
    # Caractères interdits dans les noms de fichiers Windows
    invalid_chars = r'[<>:"/\\|?*]'
    
    # Remplacer les caractères interdits par des underscores
    cleaned = re.sub(invalid_chars, "_", filename)
    
    # Remplacer les espaces multiples par un seul espace
    cleaned = re.sub(r'\s+', " ", cleaned)
    
    # Remplacer les underscores multiples par un seul underscore
    cleaned = re.sub(r'_+', "_", cleaned)
    
    # Enlever les espaces et underscores en début et fin
    cleaned = cleaned.strip(" _")
    
    # Remplacer les espaces par des underscores
    cleaned = cleaned.replace(" ", "_")
    
    # Limiter la longueur du nom de fichier
    if len(cleaned) > 100:
        cleaned = cleaned[:97] + "..."
    
    # Si le nom de fichier est vide après nettoyage, utiliser un nom par défaut
    if not cleaned:
        cleaned = "untitled"
    
    return cleaned
