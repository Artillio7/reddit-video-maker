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

from utils.redditScrape import scrapeComments
from utils.modern_captions import ModernCaptionMaker
from utils.modern_audio import ModernAudioMaker
from pathlib import Path
from config import AUDIO_CONFIG, CONTENT_LIMITS, OUTPUT_CONFIG, LOGGING_CONFIG

# Configuration du logger
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG.get("level", "INFO")),
    format=LOGGING_CONFIG.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

if LOGGING_CONFIG.get("log_to_file", False):
    file_handler = logging.FileHandler(LOGGING_CONFIG.get("log_file", "reddit_video_maker.log"))
    file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG.get("format")))
    logging.getLogger().addHandler(file_handler)

logger = logging.getLogger("RedditContentCreator")

class RedditContentCreator:
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir if output_dir else OUTPUT_CONFIG.get("base_directory", "output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.subdirs = OUTPUT_CONFIG.get("subdirectories", {
            "title": "titre",
            "comments": "commentaires",
            "audio": "audio"
        })
        
        self.caption_maker = ModernCaptionMaker()
        logger.info(f"RedditContentCreator initialisé avec répertoire de sortie: {self.output_dir}")
        
    def sanitize_filename(self, name):
        name = re.sub(r'[^\w\s-]', '_', name)
        name = re.sub(r'\s+', '-', name)
        return name[:50] if len(name) > 50 else name
        
    def create_content(self, subreddit="askreddit", timeframe="day", post_count=1):
        logger.info(f"Début du processus de création: subreddit={subreddit}, timeframe={timeframe}, post_count={post_count}")
        
        post_data = scrapeComments(subreddit, post_count, timeframe)
        if not post_data:
            logger.error("Aucun post trouvé")
            return
            
        for post_index, post in enumerate(post_data[:post_count]):
            logger.info(f"Traitement du post {post_index+1}/{min(post_count, len(post_data))}")
            
            author = str(post.author) if post.author else "[deleted]"
            sanitized_title = self.sanitize_filename(post.title)
            
            post_id_format = OUTPUT_CONFIG.get("unique_id_format", "{subreddit}_{title}_{timestamp}")
            post_id = post_id_format.format(
                subreddit=subreddit,
                title=sanitized_title,
                timestamp=int(time.time()),
                uuid=uuid.uuid4().hex[:8]
            )
            
            post_dir = self.output_dir / post_id
            title_dir = post_dir / self.subdirs["title"]
            comments_dir = post_dir / self.subdirs["comments"]
            audio_dir = post_dir / self.subdirs["audio"]
            
            for d in [title_dir, comments_dir, audio_dir]:
                d.mkdir(parents=True, exist_ok=True)
                
            with open(post_dir / "metadata.txt", "w", encoding="utf-8") as f:
                f.write(f"Titre: {post.title}\n")
                f.write(f"Auteur: {author}\n")
                f.write(f"Subreddit: r/{post.subreddit}\n")
                f.write(f"URL: {post.url}\n")
                f.write(f"Date: {time.ctime()}\n")
                f.write(f"ID: {post_id}\n")
            
            self.audio_maker = ModernAudioMaker(audio_dir)
            
            # 1. Créer les images (1 titre + 9 commentaires max)
            logger.info("Création des images...")
            title_image = self.caption_maker.create_title_card(
                post.title, 
                author, 
                f"r/{post.subreddit}"
            )
            title_image_path = title_dir / "title.png"
            title_image.save(title_image_path)
            
            with open(title_dir / "title.txt", "w", encoding="utf-8") as f:
                f.write(post.title)
            
            comments = []
            max_comments = 9  # Limité à 9 commentaires
            
            for i, comment in enumerate(post_data[post_index+1:]):
                if i >= max_comments:
                    break
                    
                comment_author = str(comment.author) if comment.author else "[deleted]"
                comment_text = comment.body
                
                min_length = CONTENT_LIMITS.get("min_comment_length", 50)
                if len(comment_text.strip()) < min_length:
                    continue
                
                comment_dir = comments_dir / f"comment_{i}"
                comment_dir.mkdir(exist_ok=True)
                
                with open(comment_dir / "text.txt", "w", encoding="utf-8") as f:
                    f.write(comment_text)
                
                img = self.caption_maker.create_comment_card(comment_text, comment_author, i)
                img_path = comment_dir / "capture.png"
                img.save(img_path)
                comments.append({"text": comment_text, "path": img_path, "dir": comment_dir})
            
            # 2. Créer l'audio
            logger.info("Création de l'audio...")
            
            title_audio_path = audio_dir / "title_audio.mp3"
            title_audio = self.audio_maker.create_audio_for_text(
                f"From {author} on Reddit: {post.title}", 
                title_audio_path
            )
            
            for i, comment in enumerate(comments):
                comment_audio_path = audio_dir / f"comment_{i}_audio.mp3"
                comment_audio = self.audio_maker.create_audio_for_text(
                    comment["text"],
                    comment_audio_path
                )
            
            logger.info(f"Contenu créé avec succès dans le dossier: {post_dir}")

if __name__ == "__main__":
    creator = RedditContentCreator()
    creator.create_content()
