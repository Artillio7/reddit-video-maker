import sys
import os
import time
import re
import uuid
import logging

# Ajout du répertoire parent au chemin Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from askreddit.utils.redditScrape import scrapeComments
from askreddit.utils.modern_video import TikTokVideoMaker
from askreddit.utils.modern_captions import ModernCaptionMaker
from askreddit.utils.modern_audio import ModernAudioMaker
from pathlib import Path
import shutil
from askreddit.config import VIDEO_CONFIG, AUDIO_CONFIG, CONTENT_LIMITS, OUTPUT_CONFIG, LOGGING_CONFIG

# Configuration du logger
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG.get("level", "INFO")),
    format=LOGGING_CONFIG.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

if LOGGING_CONFIG.get("log_to_file", False):
    file_handler = logging.FileHandler(LOGGING_CONFIG.get("log_file", "reddit_video_maker.log"))
    file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG.get("format")))
    logging.getLogger().addHandler(file_handler)

logger = logging.getLogger("RedditTikTokCreator")

class RedditTikTokCreator:
    def __init__(self, output_dir=None):
        """Initialisation du créateur de vidéos Reddit TikTok
        
        Args:
            output_dir: Répertoire de sortie personnalisé (utilise la config par défaut si None)
        """
        # Utiliser la configuration ou la valeur par défaut
        self.output_dir = Path(output_dir if output_dir else OUTPUT_CONFIG.get("base_directory", "output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Définir les sous-répertoires à partir de la configuration
        self.subdirs = OUTPUT_CONFIG.get("subdirectories", {
            "title": "titre",
            "comments": "commentaires",
            "audio": "audio",
            "video": "video"
        })
        
        # Initialiser les composants
        self.caption_maker = ModernCaptionMaker()
        self.video_maker = None  # Sera initialisé pour chaque vidéo
        
        logger.info(f"RedditTikTokCreator initialisé avec répertoire de sortie: {self.output_dir}")
        
    def sanitize_filename(self, name):
        """Nettoie une chaîne pour en faire un nom de fichier valide"""
        # Remplacer les caractères non-alphanumériques par des underscores
        name = re.sub(r'[^\w\s-]', '_', name)
        # Remplacer les espaces par des tirets
        name = re.sub(r'\s+', '-', name)
        # Limiter la longueur
        return name[:50] if len(name) > 50 else name
        
    def create_video(self, subreddit="askreddit", timeframe="day", post_count=1):
        """Crée une vidéo TikTok à partir d'un post Reddit"""
        logger.info(f"Début du processus de création vidéo: subreddit={subreddit}, timeframe={timeframe}, post_count={post_count}")
        
        # Récupérer le post et les commentaires
        post_data = scrapeComments(subreddit, post_count, timeframe)
        if not post_data:
            logger.error("Aucun post trouvé")
            return
            
        # Traiter chaque post
        for post_index, post in enumerate(post_data[:post_count]):
            logger.info(f"Traitement du post {post_index+1}/{min(post_count, len(post_data))}")
            
            # Créer un identifiant unique pour ce post
            author = str(post.author) if post.author else "[deleted]"
            sanitized_title = self.sanitize_filename(post.title)
            
            # Utiliser le format d'ID unique de la configuration
            post_id_format = OUTPUT_CONFIG.get("unique_id_format", "{subreddit}_{title}_{timestamp}")
            post_id = post_id_format.format(
                subreddit=subreddit,
                title=sanitized_title,
                timestamp=int(time.time()),
                uuid=uuid.uuid4().hex[:8]
            )
            
            # Créer la structure de dossiers pour ce post
            post_dir = self.output_dir / post_id
            title_dir = post_dir / self.subdirs["title"]
            comments_dir = post_dir / self.subdirs["comments"]
            audio_dir = post_dir / self.subdirs["audio"]
            video_dir = post_dir / self.subdirs["video"]
            
            # Créer les dossiers nécessaires
            for d in [title_dir, comments_dir, audio_dir, video_dir]:
                d.mkdir(parents=True, exist_ok=True)
                
            # Sauvegarder les métadonnées du post
            with open(post_dir / "metadata.txt", "w", encoding="utf-8") as f:
                f.write(f"Titre: {post.title}\n")
                f.write(f"Auteur: {author}\n")
                f.write(f"Subreddit: r/{post.subreddit}\n")
                f.write(f"URL: {post.url}\n")
                f.write(f"Date: {time.ctime()}\n")
                f.write(f"ID: {post_id}\n")
            
            # Initialiser les composants pour ce post
            self.audio_maker = ModernAudioMaker(audio_dir)
            self.video_maker = TikTokVideoMaker(
                output_size=(VIDEO_CONFIG.get("width", 1080), VIDEO_CONFIG.get("height", 1920))
            )
            
            # 1. Créer les images
            logger.info("Création des images...")
            title_image = self.caption_maker.create_title_card(
                post.title, 
                author, 
                f"r/{post.subreddit}"
            )
            title_image_path = title_dir / "title.png"
            title_image.save(title_image_path)
            
            # Sauvegarder le texte du titre
            with open(title_dir / "title.txt", "w", encoding="utf-8") as f:
                f.write(post.title)
            
            comments = []
            comment_images = []
            
            # Limiter le nombre de commentaires selon la configuration
            max_comments = CONTENT_LIMITS.get("max_comments", 5)
            
            # Traiter les commentaires
            for i, comment in enumerate(post_data[post_index+1:]):
                if i >= max_comments:
                    break
                    
                comment_author = str(comment.author) if comment.author else "[deleted]"
                comment_text = comment.body
                
                # Vérifier la longueur minimale du commentaire
                min_length = CONTENT_LIMITS.get("min_comment_length", 50)
                if len(comment_text.strip()) < min_length:
                    continue
                
                # Créer un dossier pour ce commentaire
                comment_dir = comments_dir / f"comment_{i}"
                comment_dir.mkdir(exist_ok=True)
                
                # Sauvegarder le texte du commentaire
                with open(comment_dir / "text.txt", "w", encoding="utf-8") as f:
                    f.write(comment_text)
                
                # Diviser les commentaires longs selon la configuration
                max_length = CONTENT_LIMITS.get("max_comment_length", 500)
                if len(comment_text) > max_length:
                    chunks = [comment_text[i:i+max_length] for i in range(0, len(comment_text), max_length)]
                    for j, chunk in enumerate(chunks):
                        img = self.caption_maker.create_comment_card(chunk, comment_author, i)
                        img_path = comment_dir / f"part_{j}.png"
                        img.save(img_path)
                        comment_images.append(img_path)
                        comments.append({"text": chunk, "path": img_path, "dir": comment_dir})
                else:
                    img = self.caption_maker.create_comment_card(comment_text, comment_author, i)
                    img_path = comment_dir / "capture.png"
                    img.save(img_path)
                    comment_images.append(img_path)
                    comments.append({"text": comment_text, "path": img_path, "dir": comment_dir})
            
            # 2. Créer l'audio
            logger.info("Création de l'audio...")
            
            # Préparer les chemins audio
            audio_dir = post_dir / self.subdirs["audio"]
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            # Générer l'audio du titre
            title_audio_path = audio_dir / "title_audio.mp3"
            title_audio = self.audio_maker.create_audio_for_text(
                f"From {author} on Reddit: {post.title}", 
                title_audio_path
            )
            
            # Générer l'audio pour chaque commentaire
            comment_audios = []
            for i, comment in enumerate(comments):
                comment_audio_path = audio_dir / f"comment_{i}_audio.mp3"
                comment_audio = self.audio_maker.create_audio_for_text(
                    comment["text"],
                    comment_audio_path
                )
                if comment_audio:
                    comment_audios.append(comment_audio)
            
            # Combiner tous les audios avec la musique de fond
            final_audio_path = audio_dir / "combined_audio_with_music.wav"
            final_audio = self.audio_maker.combine_audio_files(
                [title_audio] + comment_audios,
                final_audio_path,
                background_volume=0.3
            )
            
            if not final_audio:
                logger.error("Erreur lors de la création de l'audio")
                continue
            
            # 3. Créer la vidéo
            logger.info("Assemblage de la vidéo...")
            
            # Ajouter le titre avec durée de configuration
            title_duration = VIDEO_CONFIG.get("title_duration", 5)
            self.video_maker.add_image_clip(str(title_image_path), title_duration)
            
            # Ajouter les commentaires avec durée de configuration
            comment_duration = VIDEO_CONFIG.get("comment_duration", 8)
            for image_path in comment_images:
                self.video_maker.add_image_clip(str(image_path), comment_duration)
                
            # Ajouter l'audio
            self.video_maker.add_audio(final_audio)
            
            # Rendre la vidéo finale
            output_path = video_dir / f"{sanitized_title}_video.mp4"
            logger.info(f"Rendu de la vidéo vers {output_path}...")
            
            render_success = self.video_maker.render(
                str(output_path),
                fps=VIDEO_CONFIG.get("fps", 30)
            )
            
            if not render_success:
                logger.error(f"Erreur lors du rendu de la vidéo: {output_path}")
                continue
                
            # Copier la vidéo finale vers le répertoire principal pour un accès facile
            if OUTPUT_CONFIG.get("copy_final_to_root", True):
                final_copy_path = self.output_dir / f"{sanitized_title}_video.mp4"
                shutil.copy(str(output_path), str(final_copy_path))
                logger.info(f"Copie de la vidéo créée dans: {final_copy_path}")
            
            logger.info(f"Vidéo créée avec succès: {output_path}")
            
            # Nettoyage des fichiers temporaires si configuré
            if not OUTPUT_CONFIG.get("keep_temp_files", True):
                logger.info("Nettoyage des fichiers temporaires...")
                # Garder uniquement la vidéo finale et les métadonnées
                for path in audio_dir.glob("*"):
                    if path.name != "final_audio.wav":
                        path.unlink()
            
        return True

if __name__ == "__main__":
    creator = RedditTikTokCreator()
    creator.create_video()
