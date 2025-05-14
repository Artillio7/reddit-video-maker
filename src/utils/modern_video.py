
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modern Video Maker
-----------------
Module pour créer des vidéos TikTok avec des images correctement dimensionnées.
"""

import os
import sys
import logging
from pathlib import Path

# Vérifier si moviepy est installé
try:
    from moviepy.editor import *
except ImportError:
    print("Le module moviepy n'est pas installé. Installation en cours...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
    from moviepy.editor import *

# Vérifier si Pillow est installé
try:
    from PIL import Image, ImageTk
except ImportError:
    print("Le module Pillow n'est pas installé. Installation en cours...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

# Compatibilité avec les différentes versions de Pillow
# ANTIALIAS est déprécié dans les nouvelles versions de Pillow et remplacé par LANCZOS
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

class TikTokVideoMaker:
    """Classe pour créer des vidéos au format TikTok à partir d'images."""
    
    def __init__(self, output_path, output_size=(1080, 1920), fps=30):
        """
        Initialise le créateur de vidéos TikTok.
        
        Args:
            output_path: Chemin de sortie pour la vidéo générée
            output_size: Taille de la vidéo (largeur, hauteur)
            fps: Images par seconde
        """
        self.output_path = output_path
        self.output_size = output_size
        self.fps = fps
        self.clips = []
        self.background_color = (25, 25, 25)  # Couleur de fond (RGB)
        self.background_path = None  # Chemin vers l'image ou vidéo d'arrière-plan
        self.background_audio_path = None  # Chemin vers l'audio d'arrière-plan
        self.background_type = None  # Type d'arrière-plan: 'image', 'video' ou None
        self.total_duration = 0
        
    def set_background(self, background_path, type='image'):
        """
        Définit l'arrière-plan de la vidéo.
        
        Args:
            background_path: Chemin vers l'image ou la vidéo d'arrière-plan
            type: Type d'arrière-plan ('image' ou 'video')
        """
        if not os.path.exists(background_path):
            logging.error(f"Le fichier d'arrière-plan {background_path} n'existe pas.")
            return False
            
        self.background_path = background_path
        self.background_type = type
        return True
    
    def set_background_audio(self, audio_path):
        """
        Définit l'audio d'arrière-plan de la vidéo.
        
        Args:
            audio_path: Chemin vers le fichier audio d'arrière-plan
        """
        if not os.path.exists(audio_path):
            logging.error(f"Le fichier audio {audio_path} n'existe pas.")
            return False
            
        self.background_audio_path = audio_path
        return True
    
    def set_zoom_factor(self, zoom_factor):
        """
        Cette méthode est conservée pour la compatibilité avec le code existant,
        mais n'a plus d'effet car les images sont maintenant positionnées sans zoom.
        
        Args:
            zoom_factor: Facteur de zoom (ignoré dans cette version)
        """
        logging.info("La fonction set_zoom_factor est désactivée dans cette version. Les images sont positionnées sans zoom.")
        
    def add_image(self, image_path, duration=5):
        """
        Ajoute une image à la vidéo en la redimensionnant correctement pour le format TikTok,
        en s'assurant qu'elle est bien proportionnée et visible dans l'écran vertical.
        
        Args:
            image_path: Chemin vers l'image
            duration: Durée d'affichage de l'image en secondes
        """
        if not os.path.exists(image_path):
            logging.error(f"L'image {image_path} n'existe pas.")
            return False
        
        try:
            # Charger l'image avec moviepy
            img_clip = ImageClip(image_path).set_duration(duration)
            
            # Obtenir les dimensions originales de l'image
            img_width, img_height = img_clip.size
            video_width, video_height = self.output_size
            
            logging.debug(f"Dimensions originales de l'image: {img_width}x{img_height}")
            
            # Calculer le ratio d'aspect de l'image et de la vidéo
            img_ratio = img_width / img_height
            video_ratio = video_width / video_height
            
            # Déterminer la meilleure façon de redimensionner l'image pour le format TikTok
            # Pour le format vertical de TikTok, nous voulons que l'image soit bien visible
            # mais pas trop grande pour éviter qu'elle ne soit coupée
            
            # Limiter la largeur maximale à 80% de la largeur de la vidéo
            max_width = int(video_width * 0.8)  # 80% de la largeur de la vidéo
            
            # Limiter la hauteur maximale à 60% de la hauteur de la vidéo
            # pour laisser de l'espace en haut et en bas
            max_height = int(video_height * 0.6)  # 60% de la hauteur de la vidéo
            
            # Calculer les nouvelles dimensions en respectant le ratio d'aspect original
            if img_ratio > video_ratio:  # Image plus large que haute par rapport à la vidéo
                # Limiter par la largeur
                new_width = min(img_width, max_width)
                new_height = int(new_width / img_ratio)
                
                # Vérifier si la hauteur ne dépasse pas la limite
                if new_height > max_height:
                    new_height = max_height
                    new_width = int(new_height * img_ratio)
            else:  # Image plus haute que large par rapport à la vidéo
                # Limiter par la hauteur
                new_height = min(img_height, max_height)
                new_width = int(new_height * img_ratio)
                
                # Vérifier si la largeur ne dépasse pas la limite
                if new_width > max_width:
                    new_width = max_width
                    new_height = int(new_width / img_ratio)
            
            # Redimensionner l'image avec les nouvelles dimensions
            img_clip = img_clip.resize((new_width, new_height))
            logging.debug(f"Image redimensionnée: {new_width}x{new_height}")
            
            # Centrer l'image (position 'center' gère automatiquement le centrage horizontal et vertical)
            img_clip = img_clip.set_position('center')
            
            logging.debug(f"Image positionnée: {os.path.basename(image_path)} - Dimensions finales: {new_width}x{new_height}")
            
            # Créer le fond
            if self.background_path and self.background_type == 'image':
                # Utiliser une image comme arrière-plan
                try:
                    bg_img = ImageClip(self.background_path).set_duration(duration)
                    # Redimensionner l'arrière-plan pour couvrir toute la vidéo
                    bg_img = bg_img.resize(self.output_size)
                    bg_clip = bg_img
                except Exception as e:
                    logging.error(f"Erreur avec l'image d'arrière-plan: {e}. Utilisation de la couleur par défaut.")
                    bg_clip = ColorClip(self.output_size, color=self.background_color).set_duration(duration)
            elif self.background_path and self.background_type == 'video':
                # Utiliser une vidéo comme arrière-plan
                try:
                    bg_video = VideoFileClip(self.background_path)
                    # Extraire un segment de la vidéo de la durée nécessaire (en boucle si nécessaire)
                    if bg_video.duration < duration:
                        # Répéter la vidéo si elle est trop courte
                        n_loops = int(duration / bg_video.duration) + 1
                        bg_video = bg_video.loop(n=n_loops)
                    bg_video = bg_video.subclip(0, duration)
                    # Redimensionner la vidéo pour couvrir toute la vidéo
                    bg_video = bg_video.resize(self.output_size)
                    bg_clip = bg_video
                except Exception as e:
                    logging.error(f"Erreur avec la vidéo d'arrière-plan: {e}. Utilisation de la couleur par défaut.")
                    bg_clip = ColorClip(self.output_size, color=self.background_color).set_duration(duration)
            else:
                # Utiliser une couleur unie comme arrière-plan
                bg_clip = ColorClip(self.output_size, color=self.background_color).set_duration(duration)
            
            # Superposer l'image sur le fond
            final_clip = CompositeVideoClip([bg_clip, img_clip])
            
            # Ajouter le clip à la liste
            self.clips.append(final_clip)
            self.total_duration += duration
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de l'image: {e}")
            return False
    
    def add_audio_to_video(self, video_path, audio_path, output_path):
        """
        Ajoute un fichier audio à une vidéo.
        
        Args:
            video_path: Chemin vers la vidéo
            audio_path: Chemin vers le fichier audio
            output_path: Chemin de sortie pour la vidéo avec audio
        
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            # Charger la vidéo et l'audio
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Ajuster la durée de l'audio à celle de la vidéo si nécessaire
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            
            # Ajouter l'audio à la vidéo
            final_video = video.set_audio(audio)
            
            # Enregistrer la vidéo finale
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=self.fps)
            
            # Fermer les clips
            video.close()
            audio.close()
            final_video.close()
            
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de l'audio à la vidéo: {e}")
            return False
    
    def render(self):
        """
        Rend la vidéo finale avec toutes les images ajoutées.
        
        Returns:
            bool: True si le rendu a réussi, False sinon
        """
        if not self.clips:
            logging.error("Aucune image n'a été ajoutée à la vidéo.")
            return False
        
        try:
            # Concaténer tous les clips pour créer une séquence d'images
            final_clip = concatenate_videoclips(self.clips)
            
            # Ajouter l'audio d'arrière-plan si spécifié
            if self.background_audio_path and os.path.exists(self.background_audio_path):
                try:
                    bg_audio = AudioFileClip(self.background_audio_path)
                    
                    # Ajuster la durée de l'audio à celle de la vidéo
                    if bg_audio.duration < final_clip.duration:
                        # Répéter l'audio si nécessaire pour couvrir toute la durée
                        n_loops = int(final_clip.duration / bg_audio.duration) + 1
                        bg_audio = concatenate_audioclips([bg_audio] * n_loops)
                    
                    # Couper l'audio à la durée exacte de la vidéo
                    bg_audio = bg_audio.subclip(0, final_clip.duration)
                    
                    # Réduire le volume de l'audio d'arrière-plan
                    bg_audio = bg_audio.volumex(0.3)  # Ajuster le volume à 30%
                    
                    # Ajouter l'audio à la vidéo
                    final_clip = final_clip.set_audio(bg_audio)
                except Exception as e:
                    logging.error(f"Erreur lors de l'ajout de l'audio d'arrière-plan: {e}")
            
            # Enregistrer la vidéo
            has_audio = self.background_audio_path is not None
            final_clip.write_videofile(self.output_path, codec='libx264', fps=self.fps, audio=has_audio)
            
            # Fermer le clip final
            final_clip.close()
            
            # Fermer tous les clips
            for clip in self.clips:
                clip.close()
            
            return True
        except Exception as e:
            logging.error(f"Erreur lors du rendu de la vidéo: {e}")
            return False
    
    def create_slideshow(self, image_paths, total_duration=61):
        """
        Crée un diaporama à partir d'une liste d'images avec une durée totale spécifiée.
        Les images sont redimensionnées pour être entièrement visibles et centrées.
        
        Args:
            image_paths: Liste des chemins vers les images
            total_duration: Durée totale de la vidéo en secondes (par défaut 61s)
            
        Returns:
            bool: True si la création a réussi, False sinon
        """
        if not image_paths:
            logging.error("Aucune image fournie pour le diaporama.")
            return False
            
        # Calculer la durée de chaque image pour atteindre la durée totale
        image_count = len(image_paths)
        duration_per_image = total_duration / image_count
        
        logging.info(f"Création d'un diaporama avec {image_count} images")
        
        # Ajouter chaque image à la vidéo
        for i, image_path in enumerate(image_paths):
            # Ajouter l'image au diaporama
            if not self.add_image(image_path, duration=duration_per_image):
                logging.error(f"Échec de l'ajout de l'image {image_path}")
                return False
        
        # Rendre la vidéo
        return self.render()