"""Configuration for the Reddit Video Maker"""
import os
from dotenv import load_dotenv
import logging

# Charger les variables d'environnement depuis .env si disponible
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Vérifier les identifiants Reddit
client_id = os.environ.get("REDDIT_CLIENT_ID")
client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
user_agent = os.environ.get("REDDIT_USER_AGENT")

if client_id == "your_client_id" or client_id is None:
    logger.warning("REDDIT_CLIENT_ID non configure dans le fichier .env")
    logger.warning("Veuillez suivre les instructions dans le fichier .env pour configurer vos identifiants Reddit")

if client_secret == "your_client_secret" or client_secret is None:
    logger.warning("REDDIT_CLIENT_SECRET non configure dans le fichier .env")

# Reddit API Configuration
REDDIT_CONFIG = {
    "client_id": client_id,
    "client_secret": client_secret,
    "user_agent": user_agent or "RedditVideoMaker by /u/your_reddit_username"
}

# Video Configuration
VIDEO_CONFIG = {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "background_color": (25, 25, 25),
    "text_color": (255, 255, 255),
    "font_size": 40,
    "max_duration": 60,  # Maximum video duration in seconds
    "title_duration": 5,  # Duration for title cards in seconds
    "comment_duration": 8,  # Duration for comment cards in seconds
    "transition_duration": 0.8,  # Duration of transitions in seconds
    "enable_zoom_effect": True,  # Enable zoom effects on images
    "video_codec": "libx264",
    "video_bitrate": "2500k",
}

# Audio Configuration
AUDIO_CONFIG = {
    "tts_language": "en",
    "background_music_volume": -15,  # Volume reduction in dB (ajuste pour meilleur equilibre)
    "voice_boost": 3,  # Boost de voix en dB
    "ducking_factor": 0.8,  # Reduction de volume de musique quand il y a de la voix (0-1)
    "audio_quality": "128k",
    "fade_duration": 1000,  # Fade duration in milliseconds
    "silence_between_segments": 0.8,  # Silence entre segments en secondes
    "audio_codec": "aac",
}

# Content Limits
CONTENT_LIMITS = {
    "max_title_length": 300,
    "max_comment_length": 500,
    "max_comments": 5,
    "min_comment_length": 50,
}

# Output Structure
OUTPUT_CONFIG = {
    "base_directory": "output",
    "subdirectories": {
        "title": "titre",
        "comments": "commentaires",
        "audio": "audio",
        "video": "video"
    },
    "copy_final_to_root": True,  # Copier la video finale dans le repertoire racine
    "keep_temp_files": True,  # Conserver les fichiers temporaires
    "unique_id_format": "{subreddit}_{title}_{timestamp}"  # Format pour les identifiants uniques
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_to_file": True,
    "log_file": "reddit_video_maker.log"
}
