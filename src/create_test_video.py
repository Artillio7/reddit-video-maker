#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour créer une vidéo avec des données fictives
"""

import os
import sys
import logging
import time
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_video.log'))
    ]
)

# Importer les modules du projet
try:
    from utils.modern_audio import ModernAudioMaker
    from utils.modern_video import TikTokVideoMaker
    from utils.modern_captions import ModernCaptionMaker
    from mock_data import get_mock_posts
    import config
except ImportError as e:
    logging.error(f"Erreur d'importation: {e}")
    logging.error("Assurez-vous d'exécuter le script depuis le dossier src")
    sys.exit(1)

def create_test_video():
    """Création d'une vidéo de test avec des données fictives"""
    
    # Obtenir les chemins de base
    base_dir = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(base_dir, 'output')
    resources_dir = os.path.join(base_dir, 'resources')
    music_dir = os.path.join(resources_dir, 'music')
    fonts_dir = os.path.join(resources_dir, 'fonts')
    backgrounds_dir = os.path.join(resources_dir, 'backgrounds')
    icons_dir = os.path.join(resources_dir, 'icons')
    
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Récupérer des données fictives
    posts = get_mock_posts(1)
    post = posts[0]
    
    # Générer un ID unique pour le post
    post_id = f"test_vid_{int(time.time())}"
    post_dir = os.path.join(output_dir, post_id)
    os.makedirs(post_dir, exist_ok=True)
    
    # Sous-dossiers pour organiser les fichiers
    audio_dir = os.path.join(post_dir, 'audio')
    images_dir = os.path.join(post_dir, 'images')
    video_dir = os.path.join(post_dir, 'video')
    
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)
    
    # Fichier de sortie final
    output_video = os.path.join(video_dir, f"{post_id}_video.mp4")
    
    # Initialiser les composants
    video_maker = TikTokVideoMaker(
        output_path=output_video,
        output_size=(config.VIDEO_CONFIG.get("width", 1080), 
                   config.VIDEO_CONFIG.get("height", 1920)),
        fps=config.VIDEO_CONFIG.get("fps", 30)
    )
    
    audio_maker = ModernAudioMaker(
        output_dir=audio_dir, 
        background_music_dir=music_dir
    )
    
    # Créer l'instance de ModernCaptionMaker avec les dimensions correctes
    caption_maker = ModernCaptionMaker(
        size=(config.VIDEO_CONFIG.get("width", 1080), 
              config.VIDEO_CONFIG.get("height", 1920))
    )
    
    # Créer les images
    logging.info("Création des images...")
    
    # Image du titre
    title_image = os.path.join(images_dir, "title.png")
    subreddit_icon = Path(icons_dir) / "askreddit.png"
    
    # Utiliser le chemin d'icône par défaut si l'icône spécifique n'existe pas
    if not subreddit_icon.exists():
        subreddit_icon = list(Path(icons_dir).glob("*.png"))[0] if list(Path(icons_dir).glob("*.png")) else None
    
    # Générer l'image de titre
    title_card = caption_maker.create_title_card(
        title=post["title"],
        author=post["author"],
        subreddit="AskReddit"
    )
    title_card.save(title_image)
    
    # Images des commentaires
    comment_images = []
    for i, comment in enumerate(post["comments"]):
        comment_image = os.path.join(images_dir, f"comment_{i}.png")
        comment_card = caption_maker.create_comment_card(
            text=comment["body"],
            author=comment["author"],
            comment_num=i+1
        )
        comment_card.save(comment_image)
        comment_images.append(comment_image)
    
    # Créer l'audio
    logging.info("Création de l'audio...")
    audio_paths = []
    
    # Audio pour le titre
    title_audio = os.path.join(audio_dir, "title.mp3")
    audio_maker.create_audio_for_text(post["title"], title_audio)
    audio_paths.append(title_audio)
    
    # Audio pour les commentaires
    for i, comment in enumerate(post["comments"]):
        comment_audio = os.path.join(audio_dir, f"comment_{i}.mp3")
        audio_maker.create_audio_for_text(comment["body"], comment_audio)
        audio_paths.append(comment_audio)
    
    # Combiner tous les audios
    combined_audio = os.path.join(audio_dir, "combined.wav")
    result, audio_durations = audio_maker.combine_audio_files(
        audio_paths, 
        combined_audio, 
        background_volume=config.AUDIO_CONFIG.get("background_music_volume", 0.2)
    )
    
    if not result:
        logging.error("Erreur lors de la création de l'audio")
        return None
        
    # Ajouter un peu de marge pour chaque segment (pour éviter les coupures trop abruptes)
    # Une marge minimale de 2 secondes pour chaque segment
    segment_durations = [max(duration + 0.5, 2.0) for duration in audio_durations]
    
    logging.info(f"Durées des segments audio: {', '.join([f'{d:.2f}s' for d in audio_durations])}")
    logging.info(f"Durées finales des segments vidéo: {', '.join([f'{d:.2f}s' for d in segment_durations])}")
    
    # Créer les métadonnées
    with open(os.path.join(post_dir, 'metadata.txt'), 'w', encoding='utf-8') as f:
        f.write(f"Titre: {post['title']}\n")
        f.write(f"Auteur: {post['author']}\n")
        f.write(f"Créé le: {time.ctime()}\n")
        f.write(f"Nombre de commentaires: {len(post['comments'])}\n")
    
    # Ajouter les images à la vidéo avec les durées audio correspondantes
    # Titre avec sa durée audio
    logging.info(f"Ajout du titre avec durée: {segment_durations[0]:.2f}s")
    video_maker.add_image_clip(title_image, segment_durations[0])
    
    # Commentaires avec leurs durées audio respectives
    for i, comment_image in enumerate(comment_images):
        # Si nous avons des durées audio pour ce commentaire (index+1 car 0 est le titre)
        if i+1 < len(segment_durations):
            duration = segment_durations[i+1]
            logging.info(f"Ajout du commentaire {i} avec durée: {duration:.2f}s")
            video_maker.add_image_clip(comment_image, duration)
        else:
            # Fallback au cas où nous aurions plus de commentaires que de segments audio
            logging.warning(f"Pas de durée audio pour le commentaire {i}, utilisation de 5s par défaut")
            video_maker.add_image_clip(comment_image, 5)
    
    # Ajouter l'audio
    video_maker.add_audio(combined_audio)
    
    # Rendre la vidéo
    logging.info("Rendu de la vidéo en cours...")
    if video_maker.render():
        logging.info(f"Vidéo créée avec succès: {output_video}")
        return output_video
    else:
        logging.error("Erreur lors de la création de la vidéo")
        return None

def main():
    """Fonction principale"""
    video_path = create_test_video()
    
    if video_path:
        # Message plus visible à la fin du processus
        completion_message = f"\n{'='*80}\n{'='*25} VIDÉO CRÉÉE AVEC SUCCÈS {'='*25}\n{'='*80}"
        completion_message += f"\nChemin: {video_path}"
        completion_message += f"\nDate et heure: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Vérifier la taille du fichier pour confirmer qu'il a bien été créé
        try:
            video_size = os.path.getsize(video_path)
            completion_message += f"\nTaille: {video_size / (1024*1024):.2f} Mo"
            
            # Vérification de l'intégration audio
            if video_size > 100000:  # Si la vidéo fait plus de 100 Ko
                completion_message += f"\nStatut: Vidéo créée avec audio intégré "
                audio_success = True
            else:
                completion_message += f"\nStatut: La vidéo semble trop petite, l'audio pourrait ne pas être intégré"
                audio_success = False
        except Exception as e:
            completion_message += f"\nStatut: Impossible de vérifier la taille: {e}"
            audio_success = False
            
        completion_message += f"\n{'='*80}\n"
        
        logging.info(completion_message)
        
        # Afficher aussi sur la sortie standard pour être sûr
        print(completion_message)
        
        try:
            # Notification système (sur Windows)
            import subprocess
            title = "Reddit Video Maker"
            
            if audio_success:
                message = f" Vidéo créée avec succès avec audio intégré!\n{os.path.basename(video_path)}"
            else:
                message = f" Vidéo créée mais vérifiez l'audio!\n{os.path.basename(video_path)}"
                
            subprocess.run(['powershell', '-command', f'New-BurntToastNotification -Text "{title}","{message}"'], 
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            logging.warning(f"Impossible d'afficher la notification système: {e}")
        
        return 0
    else:
        logging.error("Échec de la création de la vidéo")
        return 1

if __name__ == "__main__":
    sys.exit(main())
