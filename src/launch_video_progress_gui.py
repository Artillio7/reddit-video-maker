import tkinter as tk
import threading
import os
import sys
from pathlib import Path

# Ajout du répertoire parent au chemin Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from video_progress_gui import VideoProgressGUI
from silent_video_creator import RedditSilentVideoCreator
import logging
from config import LOGGING_CONFIG

# Configuration du logger
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG.get("level", "INFO")),
    format=LOGGING_CONFIG.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

if LOGGING_CONFIG.get("log_to_file", False):
    file_handler = logging.FileHandler(LOGGING_CONFIG.get("log_file", "reddit_video_maker.log"))
    file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG.get("format")))
    logging.getLogger().addHandler(file_handler)

logger = logging.getLogger("LaunchVideoProgressGUI")

class EnhancedVideoProgressGUI(VideoProgressGUI):
    def __init__(self, root):
        super().__init__(root)
        
        # Paramètres pour la génération de vidéos
        self.subreddit = "askreddit"
        self.timeframe = "day"
        self.post_count = 1
        
        # Ajouter des champs de configuration
        config_frame = ttk.LabelFrame(self.progress_frame, text="Configuration")
        config_frame.grid(row=11, column=0, sticky="ew", padx=10, pady=10)
        
        # Subreddit
        ttk.Label(config_frame, text="Subreddit:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.subreddit_entry = ttk.Entry(config_frame, width=20)
        self.subreddit_entry.insert(0, self.subreddit)
        self.subreddit_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Timeframe
        ttk.Label(config_frame, text="Période:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.timeframe_combo = ttk.Combobox(config_frame, values=["hour", "day", "week", "month", "year", "all"])
        self.timeframe_combo.current(1)  # "day" par défaut
        self.timeframe_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Nombre de posts
        ttk.Label(config_frame, text="Nombre de posts:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.post_count_spinbox = ttk.Spinbox(config_frame, from_=1, to=5, width=5)
        self.post_count_spinbox.insert(0, "1")
        self.post_count_spinbox.grid(row=2, column=1, sticky="w", padx=5, pady=2)
    
    def update_silent_video_creator(self):
        # Récupérer les valeurs des champs de configuration
        self.subreddit = self.subreddit_entry.get().strip().lower()
        self.timeframe = self.timeframe_combo.get()
        
        try:
            self.post_count = int(self.post_count_spinbox.get())
        except ValueError:
            self.post_count = 1
        
        # Créer une instance de RedditSilentVideoCreator avec callbacks de progression et prévisualisation
        self.creator = RedditSilentVideoCreator(
            progress_callback=self.update_progress,
            preview_callback=self.update_preview
        )
    
    def process_videos(self):
        try:
            # Mettre à jour le créateur de vidéos avec les paramètres actuels
            self.update_silent_video_creator()
            
            # Lancer la création de contenu
            self.creator.create_content(
                subreddit=self.subreddit,
                timeframe=self.timeframe,
                post_count=self.post_count
            )
            
            # Réinitialiser l'interface après le traitement
            if self.processing:
                self.root.after(1000, self.reset_interface)
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement des vidéos: {e}")
            self.reset_interface()

def main():
    root = tk.Tk()
    app = EnhancedVideoProgressGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()