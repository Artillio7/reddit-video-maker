#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reddit Video Maker - Main Script
--------------------------------
Ce script principal coordonne le processus de creation de videos a partir de posts Reddit.
"""

import os
import sys
import logging
import time
import argparse
import random
from pathlib import Path
from datetime import datetime
import json
import shutil
import traceback
import unicodedata

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reddit_video_maker.log'))
    ]
)

# Importer les modules du projet
try:
    from utils.modern_audio import ModernAudioMaker, TTSGenerator
    from utils.modern_video import TikTokVideoMaker
    from utils.modern_captions import ModernCaptionMaker, CommentCardCreator
    from utils.redditScrape import RedditScraper
    import config
except ImportError as e:
    logging.error(f"Erreur d'importation: {e}")
    logging.error("Assurez-vous d'exécuter le script depuis le dossier src")
    sys.exit(1)

def sanitize_filename(filename):
    """
    Sanitize le nom de fichier en remplaçant les caractères interdits.
    
    Args:
        filename: Le nom de fichier à nettoyer
        
    Returns:
        Le nom de fichier nettoyé
    """
    # Caractères interdits dans les noms de fichiers Windows
    invalid_chars = '<>:"/\\|?*'
    
    # Remplacer les caractères interdits par des underscores
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limiter la longueur du nom de fichier
    if len(filename) > 100:
        filename = filename[:97] + '...'
    
    # Remplacer les espaces multiples par un seul espace
    while '  ' in filename:
        filename = filename.replace('  ', ' ')
    
    # Remplacer les espaces par des underscores
    filename = filename.replace(' ', '_')
    
    return filename

class RedditTikTokCreator:
    """Classe principale pour coordonner la création de vidéos TikTok à partir de Reddit."""
    
    def __init__(self, output_dir=None):
        """
        Initialise le créateur de vidéos TikTok.
        
        Args:
            output_dir: Répertoire de sortie pour les vidéos générées
        """
        # Initialiser les chemins
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        
        if output_dir is None:
            output_dir = os.path.join(self.base_dir, 'output')
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Créer un dossier temporaire s'il n'existe pas
        self.temp_dir = os.path.join(self.base_dir, 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialiser les ressources
        self.resources_dir = os.path.join(self.base_dir, 'resources')
        self.music_dir = os.path.join(self.resources_dir, 'music')
        self.fonts_dir = os.path.join(self.resources_dir, 'fonts')
        self.backgrounds_dir = os.path.join(self.resources_dir, 'backgrounds')
        self.icons_dir = os.path.join(self.resources_dir, 'icons')
        
        # Garder trace des posts déjà traités
        self.processed_posts_file = os.path.join(self.output_dir, 'processed_posts.json')
        
        # Initialiser les composants
        self.reddit_scraper = RedditScraper()
        self.tts_generator = TTSGenerator()
        
        logging.info(f"RedditTikTokCreator initialisé avec répertoire de sortie: {self.output_dir}")
    
    def create_video(self, subreddit="askreddit", timeframe="day", post_count=10, 
                    video_count=3, random_subreddit=False, allow_nsfw=False, sorting=None, comment_sort=None):
        """
        Crée une vidéo TikTok à partir de posts Reddit.
        
        Args:
            subreddit: Subreddit à utiliser (ignoré si random_subreddit=True)
            timeframe: Période (day, week, month, year, all)
            post_count: Nombre de posts à récupérer
            video_count: Nombre de vidéos à créer
            random_subreddit: Si True, sélectionne un subreddit aléatoire
            allow_nsfw: Si True, inclut les posts NSFW
            sorting: Méthode de tri ("hot", "new", "top", "rising", "controversial", None pour aléatoire)
            comment_sort: Méthode de tri des commentaires ("most_comments", "most_upvotes", None pour aléatoire)
            
        Returns:
            Liste des chemins des vidéos générées
        """
        start_time = time.time()
        logging.info(f"Début du processus de création vidéo")
        
        # Sélection de subreddit
        if random_subreddit:
            logging.info("Sélection d'un subreddit aléatoire")
            subreddit = self.reddit_scraper.get_random_subreddit()
        
        logging.info(f"Paramètres: subreddit={subreddit}, timeframe={timeframe}, post_count={post_count}, video_count={video_count}")
        
        # Récupérer les posts
        posts = self.reddit_scraper.get_reddit_posts(
            subreddit=subreddit,
            timeframe=timeframe,
            post_count=post_count,
            allow_nsfw=allow_nsfw,
            sorting=sorting,
            comment_sort=comment_sort
        )
        
        if not posts:
            logging.error("Aucun post n'a été récupéré")
            logging.error("Vérifiez vos identifiants Reddit dans le fichier .env")
            logging.error("Suivez les instructions dans le fichier .env pour obtenir vos identifiants")
            return []
        
        logging.info(f"{len(posts)} posts récupérés, création de {min(video_count, len(posts))} vidéos")
        
        videos_created = []
        
        # Limiter au nombre de vidéos demandées
        posts = posts[:min(len(posts), video_count)]
        
        # Initialiser les composants
        caption_maker = CommentCardCreator()
        audio_maker = ModernAudioMaker(
            output_dir=self.temp_dir, 
            background_music_dir=self.music_dir
        )
        
        # Traiter chaque post
        for i, post in enumerate(posts):
            try:
                logging.info(f"Traitement du post {i+1}/{len(posts)}: {post.get('title', '')[:50]}...")
                
                # Créer un nom de fichier sécurisé basé sur le titre du post
                safe_title = sanitize_filename(post.get('title', '')[:40])
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                post_id = f"{subreddit}_{safe_title}_{timestamp}"
                post_dir = os.path.join(self.output_dir, post_id)
                os.makedirs(post_dir, exist_ok=True)
                
                # Sous-dossiers pour organiser les fichiers
                audio_dir = os.path.join(post_dir, 'audio')
                images_dir = os.path.join(post_dir, 'images')
                video_dir = os.path.join(post_dir, 'video')
                
                os.makedirs(audio_dir, exist_ok=True)
                os.makedirs(images_dir, exist_ok=True)
                os.makedirs(video_dir, exist_ok=True)
                
                # Fichiers de sortie
                output_video = os.path.join(video_dir, f"{post_id}_video.mp4")  # Vidéo sans audio
                output_audio = os.path.join(audio_dir, f"{post_id}_audio.mp3")  # Audio combiné séparé
                
                # Initialiser le créateur de vidéos
                video_maker = TikTokVideoMaker(
                    output_path=output_video,
                    output_size=(config.VIDEO_CONFIG.get('width', 1080), config.VIDEO_CONFIG.get('height', 1920)),
                    fps=config.VIDEO_CONFIG.get('fps', 30)
                )
                
                # Créer les images
                logging.info("Création des images...")
                
                # Image du titre
                title_image = os.path.join(images_dir, "title.png")
                caption_maker.create_title_card(
                    title=post.get('title', ''),
                    subreddit=subreddit,
                    author=post.get('author', 'unknown'),
                    output_path=title_image
                )
                
                # Images des commentaires
                comment_images = []
                for j, comment in enumerate(post.get('comments', [])):
                    comment_image = os.path.join(images_dir, f"comment_{j}.png")
                    caption_maker.create_comment_card(
                        comment_text=comment.get('body', ''),
                        author=comment.get('author', 'unknown'),
                        upvotes=comment.get('score', 0),
                        output_path=comment_image,
                        media=comment.get('media', None)  # Passer les informations de médias
                    )
                    comment_images.append(comment_image)
                
                # Créer l'audio
                logging.info("Création de l'audio...")
                
                # Générer l'audio pour le titre
                title_audio = os.path.join(audio_dir, "title.mp3")
                self.tts_generator.generate_tts(
                    post.get('title', ''),
                    title_audio
                )
                
                # Générer l'audio pour chaque commentaire
                comment_audios = []
                for i, comment in enumerate(post.get('comments', [])[:5]):  # Limiter à 5 commentaires
                    comment_audio = os.path.join(audio_dir, f"comment_{i}.mp3")
                    self.tts_generator.generate_tts(
                        comment.get('body', ''),
                        comment_audio
                    )
                    comment_audios.append(comment_audio)
                
                # Combiner tous les fichiers audio
                all_audio_files = [title_audio] + comment_audios
                if not self.tts_generator.combine_audio_files(all_audio_files, output_audio):
                    logging.error("Erreur lors de la combinaison des fichiers audio")
                    continue
                
                # Ajouter les images à la vidéo
                video_maker.add_image(title_image, duration=5)
                for image in comment_images:
                    video_maker.add_image(image, duration=5)
                
                # Rendre la vidéo
                if not video_maker.render():
                    logging.error("Erreur lors du rendu de la vidéo")
                    continue
                
                # Ajouter l'audio à la vidéo
                if os.path.exists(output_audio) and os.path.getsize(output_audio) > 0:
                    logging.info(f"[VIDEO] Début de l'ajout d'audio")
                    final_video_path = os.path.join(video_dir, f"{post_id}_final.mp4")
                    
                    if video_maker.add_audio_to_video(output_video, output_audio, final_video_path):
                        videos_created.append({
                            'path': final_video_path,
                            'audio': output_audio,
                            'title': post.get('title', '')[:50]
                        })
                    else:
                        logging.error("Erreur lors de l'ajout de l'audio à la vidéo")
                        # En cas d'échec, essayer de conserver au moins la vidéo sans audio
                        if os.path.exists(output_video) and os.path.getsize(output_video) > 0:
                            videos_created.append({
                                'path': output_video,
                                'audio': None,
                                'title': post.get('title', '')[:50]
                            })
                else:
                    logging.error("Fichier audio manquant ou vide, impossible d'ajouter l'audio à la vidéo")
                    # Conserver la vidéo sans audio si elle existe
                    if os.path.exists(output_video) and os.path.getsize(output_video) > 0:
                        videos_created.append({
                            'path': output_video,
                            'audio': None,
                            'title': post.get('title', '')[:50]
                        })
                
            except Exception as e:
                logging.error(f"Erreur lors de la création de la vidéo pour le post: {e}")
                # Nettoyer les dossiers vides en cas d'erreur
                try:
                    # Supprimer le dossier de post si la création de la vidéo a échoué et qu'il est vide
                    if os.path.exists(post_dir):
                        has_content = False
                        for root, dirs, files in os.walk(post_dir):
                            if files:
                                has_content = True
                                break
                        
                        if not has_content:
                            shutil.rmtree(post_dir)
                            logging.info(f"Suppression du dossier vide après échec: {post_dir}")
                except Exception as cleanup_error:
                    logging.warning(f"Erreur lors du nettoyage après échec: {cleanup_error}")
        
        # Nettoyage des fichiers temporaires et des dossiers vides
        self._cleanup_temp_files()
        self._cleanup_empty_directories()
        
        # Afficher le résumé
        elapsed_time = time.time() - start_time
        logging.info(f"Processus terminé en {elapsed_time:.2f} secondes.")
        logging.info(f"Vidéos créées: {len(videos_created)}/{video_count}")
        
        return videos_created
    
    def _cleanup_temp_files(self):
        """Supprime les fichiers temporaires mais conserve les dossiers dans output."""
        try:
            # Nettoyer les fichiers temporaires dans le dossier temp uniquement
            temp_cleaned = self._clean_output_directory(self.temp_dir, remove_all=True)
            logging.info(f"Fichiers temporaires supprimés: {temp_cleaned[0]}")
            
            # Ne pas nettoyer les dossiers dans output
            # output_cleaned = self._clean_output_directory(self.output_dir, remove_all=True)
            # logging.info(f"Dossiers vides supprimés dans output: {output_cleaned[1]}")
        except Exception as e:
            logging.warning(f"Erreur lors du nettoyage des fichiers temporaires: {e}")
            
    def _cleanup_empty_directories(self):
        """Ne supprime plus les dossiers vides dans le répertoire de sortie."""
        # Désactivé pour conserver tous les dossiers dans output
        return
    
    def _sanitize_filename(self, filename):
        """
        Sanitize le nom de fichier (méthode de compatibilité, utilise la fonction globale).
        """
        return sanitize_filename(filename)
    
    def _clean_output_directory(self, directory, remove_all=False):
        """
        Nettoie le répertoire de sortie en supprimant les fichiers temporaires et les dossiers vides.
        
        Args:
            directory (str): Chemin du répertoire à nettoyer
            remove_all (bool): Si True, supprime tous les fichiers et sous-dossiers
        
        Returns:
            tuple: (nombre de fichiers supprimés, nombre de dossiers supprimés)
        """
        files_removed = 0
        dirs_removed = 0
        
        # Ne pas supprimer tout si nous sommes dans le dossier output (sauf si c'est un sous-dossier .temp)
        if directory == self.output_dir and remove_all:
            remove_all = False
        
        for root, dirs, files in os.walk(directory, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                if remove_all or file.startswith('.'):
                    try:
                        os.remove(file_path)
                        files_removed += 1
                    except Exception as e:
                        logging.warning(f"Erreur lors de la suppression du fichier {file_path}: {e}")
            
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if remove_all or dir.startswith('.'):
                    try:
                        os.rmdir(dir_path)
                        dirs_removed += 1
                    except Exception as e:
                        logging.warning(f"Erreur lors de la suppression du dossier {dir_path}: {e}")
        
        return files_removed, dirs_removed
    
    def combine_videos(self, video_paths, output_path):
        """Combine plusieurs vidéos en une seule"""
        import os
        import shutil
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        
        # Créer un répertoire temporaire pour les copies des vidéos
        temp_dir = os.path.join(self.output_dir, ".temp_combine")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Vérifier les chemins et copier les vidéos dans un emplacement sûr
        valid_paths = []
        copied_paths = []
        
        for i, path in enumerate(video_paths):
            if os.path.exists(path) and os.path.isfile(path):
                # Copier le fichier pour éviter les problèmes de suppression
                base_name = os.path.basename(path)
                safe_copy_path = os.path.join(temp_dir, f"video_{i}_{base_name}")
                try:
                    shutil.copy2(path, safe_copy_path)
                    valid_paths.append(safe_copy_path)
                    copied_paths.append(safe_copy_path)
                    logging.info(f"Copie de vidéo pour combinaison: {path} -> {safe_copy_path}")
                except Exception as e:
                    logging.error(f"Erreur lors de la copie de la vidéo {path}: {e}")
                    
                # Copier également le fichier à la racine du dossier output pour le conserver
                output_copy = os.path.join(self.output_dir, base_name)
                if not os.path.exists(output_copy):
                    try:
                        shutil.copy2(path, output_copy)
                        logging.info(f"Copie de sauvegarde: {path} -> {output_copy}")
                    except Exception as e:
                        logging.warning(f"Erreur lors de la copie de sauvegarde de {path}: {e}")
        
        if not valid_paths:
            logging.error("Aucune vidéo valide à combiner")
            return False
        
        try:
            logging.info(f"Combinaison de {len(valid_paths)} vidéos")
            video_clips = [VideoFileClip(p) for p in valid_paths]
            final_clip = concatenate_videoclips(video_clips)
            
            # Créer le répertoire de sortie si nécessaire
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Écrire la vidéo finale
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            # Fermer les clips pour libérer les ressources
            for clip in video_clips:
                clip.close()
            final_clip.close()
            
            # Nettoyage des fichiers temporaires
            for path in copied_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    logging.warning(f"Erreur lors de la suppression du fichier temporaire {path}: {e}")
            
            # Essayer de supprimer le dossier temporaire
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logging.warning(f"Erreur lors de la suppression du dossier temporaire {temp_dir}: {e}")
            
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la combinaison des vidéos: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return False


def main():
    try:
        import argparse
        
        # Parser les arguments de ligne de commande
        parser = argparse.ArgumentParser(description='Reddit Video Maker')
        
        parser.add_argument("--subreddit", type=str, default="askreddit",
                          help="Subreddit à utiliser (ignoré si --random-subreddit est spécifié)")
        
        parser.add_argument("--random-subreddit", action="store_true",
                          help="Sélectionne un subreddit aléatoire parmi la liste prédéfinie")
        
        parser.add_argument("--timeframe", type=str, default="day", choices=["hour", "day", "week", "month", "year", "all"],
                          help="Période à considérer pour les posts")
        
        parser.add_argument("--post-count", type=int, default=10,
                          help="Nombre de posts à récupérer")
        
        parser.add_argument("--video-count", type=int, default=3,
                          help="Nombre de vidéos à créer")
        
        parser.add_argument("--allow-nsfw", action="store_true",
                          help="Inclure les posts NSFW")
        
        parser.add_argument("--output-dir", type=str, default=None,
                          help="Répertoire de sortie pour les vidéos")
        
        parser.add_argument("--sorting", type=str, default=None, choices=["hot", "new", "top", "rising", "controversial"],
                          help="Méthode de tri des posts (aléatoire si non spécifiée)")
        
        parser.add_argument("--comment-sort", type=str, default=None, choices=["most_comments", "most_upvotes"],
                          help="Méthode de tri des commentaires (par défaut: most_upvotes)")
        
        # Ajout des nouveaux arguments tout en gardant la compatibilité avec les anciens
        parser.add_argument('--count', type=int, help='Alias pour --post-count')
        parser.add_argument('--sort', type=str, choices=['hot', 'new', 'top', 'rising'], 
                          help='Alias pour --sorting')
        parser.add_argument('--output', type=str, help='Alias pour --output-dir')
        parser.add_argument('--cleanup', action='store_true', 
                          help='Nettoyer les dossiers vides sans générer de vidéos')
        
        args = parser.parse_args()
        
        # Rétro-compatibilité
        if args.count and not args.post_count:
            args.post_count = args.count
        if args.sort and not args.sorting:
            args.sorting = args.sort
        if args.output and not args.output_dir:
            args.output_dir = args.output
        
        if args.cleanup:
            # Nettoyer les dossiers vides sans générer de vidéos
            creator = RedditTikTokCreator(output_dir=args.output_dir)
            empty_dirs_removed = creator._clean_output_directory(creator.output_dir, remove_all=True)
            temp_removed = creator._clean_output_directory(creator.temp_dir, remove_all=True)
            print(f"Nettoyage termine: {empty_dirs_removed[1]} dossiers vides et {temp_removed[0]} fichiers temporaires supprimes")
            return
        
        # Créer l'instance et générer les vidéos
        creator = RedditTikTokCreator(output_dir=args.output_dir)
        
        print(f"Recuperation des posts depuis r/{args.subreddit} (tri: {args.sorting or 'default'})...")
        videos = creator.create_video(
            subreddit=args.subreddit,
            timeframe=args.timeframe,
            post_count=args.post_count,
            video_count=args.video_count,
            random_subreddit=args.random_subreddit,
            allow_nsfw=args.allow_nsfw,
            sorting=args.sorting,
            comment_sort=args.comment_sort
        )
        
        # Affichage des résultats
        if videos:
            print("\nVideos generees avec succes:")
            for i, video in enumerate(videos):
                print(f"{i+1}. {os.path.basename(video['path'])}")
                print(f"   Audio: {os.path.basename(video['audio']) if video['audio'] else 'None'}")
                print(f"   Titre: {video['title'][:50]}...")
            
            print(f"\nTotal: {len(videos)} videos")
            print(f"Les videos ont ete sauvegardees dans: {creator.output_dir}")
            
            # Déboguer les chemins pour la combinaison
            print("\nDébug des chemins de vidéos:")
            
            # Vérifier les chemins et les corriger si nécessaire
            valid_videos = []
            for i, video in enumerate(videos):
                old_path = video['path']
                print(f"{i+1}. Path original: {old_path}")
                
                # Si le chemin original n'existe pas, essayons de trouver la vidéo dans le répertoire output
                if not os.path.exists(old_path):
                    # Extraire les parties importantes du chemin (dossier de sortie et nom de base)
                    base_name = os.path.basename(old_path)
                    dir_name = os.path.dirname(os.path.dirname(os.path.dirname(old_path)))  # Remonte de 3 niveaux (video/post_id/output)
                    
                    # Chercher la vidéo dans le répertoire racine
                    possible_path = os.path.join(dir_name, base_name)
                    if os.path.exists(possible_path):
                        video['path'] = possible_path
                        valid_videos.append(video)
                        print(f"   Path corrigé: {possible_path} (existe: Oui)")
                    else:
                        # Chercher tout fichier similaire
                        for root, _, files in os.walk(dir_name):
                            for file in files:
                                if file.endswith('.mp4') and file.startswith(os.path.splitext(base_name)[0].split('_')[0]):
                                    video['path'] = os.path.join(root, file)
                                    valid_videos.append(video)
                                    print(f"   Path trouvé: {video['path']} (existe: Oui)")
                                    break
                else:
                    valid_videos.append(video)
                    print(f"   Path existe déjà: {old_path}")
            
            # Mettre à jour la liste des vidéos
            videos = valid_videos
            for i, video in enumerate(videos):
                print(f"{i+1}. Path final: {video['path']}")
                print(f"   Existe: {os.path.exists(video['path'])}")
                if os.path.exists(video['path']):
                    print(f"   Taille: {os.path.getsize(video['path'])} octets")
            
            # Combinez les vidéos
            combined_video_path = os.path.join(creator.output_dir, "combined_video.mp4")
            # Utiliser le chemin 'path' complet depuis la liste des vidéos
            if videos and creator.combine_videos([video['path'] for video in videos], combined_video_path):
                print(f"\nVideo combinee creee avec succes: {combined_video_path}")
            else:
                print("\nErreur lors de la combinaison des videos.")
        else:
            print("Aucune video n'a ete generee. Consultez le fichier journal pour plus de details.")
    except Exception as e:
        logging.error(f"Erreur lors de l'execution: {e}")
        print(f"Une erreur est survenue: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
