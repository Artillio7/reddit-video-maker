import moviepy
from moviepy.editor import VideoClip, ImageClip, ColorClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, CompositeAudioClip, concatenate_audioclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import random
import logging
import os
import sys
import time
import tempfile
import soundfile as sf
import traceback
import unicodedata

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TikTokVideoMaker')

class TikTokVideoMaker:
    """Classe pour créer des vidéos TikTok avec des clips d'images et de l'audio"""
    
    def __init__(self, output_size=(1080, 1920), fps=30, output_path='output.mp4', video_codec='libx264', video_bitrate='5000k'):
        """
        Initialise le créateur de vidéos.
        
        Args:
            output_size: Taille de sortie de la vidéo (width, height)
            fps: Images par seconde
            output_path: Chemin de sortie pour la vidéo
            video_codec: Codec vidéo
            video_bitrate: Débit vidéo
        """
        # Corriger le type d'output_size si nécessaire
        if isinstance(output_size, int):
            # Si on a reçu deux entiers séparés (width, height)
            self.width, self.height = output_size, fps
            fps = 30  # Valeur par défaut
        else:
            # Sinon c'est un tuple (width, height)
            self.width, self.height = output_size
            
        self.output_size = (self.width, self.height)
        self.fps = fps
        self.images = []
        self.background_color = (0, 0, 0)
        self.output_path = output_path
        self.video_codec = video_codec
        self.video_bitrate = video_bitrate
        self.duration = 0
        
        logger.info(f"TikTokVideoMaker initialisé avec taille={self.output_size}, fps={fps}")
        
    def create_background(self, color=None, duration=60):
        """
        Crée un arrière-plan de couleur unie.
        
        Args:
            color: Couleur d'arrière-plan RGB
            duration: Durée en secondes
            
        Returns:
            Clip d'arrière-plan
        """
        if color is None:
            color = self.background_color
            
        try:
            background = ColorClip(self.output_size, color=color, duration=duration)
            return background
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'arrière-plan: {e}")
            # Solution de secours, créer une image noire
            black_img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            return ImageClip(black_img, duration=duration)
            
    def add_text_clip(self, text, duration=5, position='center', font_size=40):
        """
        Ajoute un clip de texte à la vidéo.
        
        Args:
            text: Texte à afficher
            duration: Durée d'affichage en secondes
            position: Position du texte ('center', 'top', etc.)
            font_size: Taille de la police
            
        Returns:
            Clip de texte
        """
        logger.info(f"Ajout de texte: '{text[:30]}...' ({duration}s)")
        
        # Pour le texte, nous allons créer une image avec PIL puis la convertir en clip
        try:
            # Créer une image vide avec un fond transparent
            img = Image.new('RGBA', self.output_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Essayer de charger la police Arial ou utiliser une police par défaut
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            
            # Calculer les dimensions du texte et le centrer
            text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
            
            # Positionner le texte
            if position == 'center':
                x = (self.width - text_width) // 2
                y = (self.height - text_height) // 2
            elif position == 'top':
                x = (self.width - text_width) // 2
                y = 100
            elif position == 'bottom':
                x = (self.width - text_width) // 2
                y = self.height - text_height - 100
            else:
                x = (self.width - text_width) // 2
                y = (self.height - text_height) // 2
            
            # Dessiner le texte
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            
            # Convertir en ImageClip
            txt_clip = ImageClip(np.array(img))
            txt_clip = txt_clip.set_duration(duration)
            
            self.images.append({'path': txt_clip, 'duration': duration})
            self.duration += duration
            return txt_clip
        except Exception as e:
            logger.error(f"Erreur lors de la création du texte: {e}")
            return None
        
    def add_image(self, image_path, duration=5):
        """
        Ajoute une image à la vidéo.
        
        Args:
            image_path: Chemin vers l'image
            duration: Durée d'affichage en secondes
        """
        try:
            logging.info(f"Ajout d'image: {image_path} ({duration}s)")
            
            # Créer le clip d'image
            image_clip = ImageClip(image_path)
            
            # Définir la durée
            image_clip = image_clip.set_duration(duration)
            
            # Redimensionner l'image si nécessaire
            if image_clip.size != self.output_size:
                image_clip = image_clip.resize(self.output_size)
            
            # Ajouter le clip à la liste
            self.images.append({'path': image_clip, 'duration': duration})
            self.duration += duration
            
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de l'image: {str(e)}")
            return False

    def add_audio(self, audio_files):
        """
        Ajoute l'audio à la vidéo finale.
        
        Args:
            audio_files: Liste des chemins vers les fichiers audio à ajouter
            
        Returns:
            bool: True si l'ajout a réussi, False sinon
        """
        try:
            import time
            start_time = time.time()
            logging.info("[VIDEO] Début de l'ajout d'audio")
            
            # Définir un timeout (en secondes)
            TIMEOUT = 60  # 60 secondes max pour le traitement audio
            
            # Vérifier que les fichiers audio existent
            valid_files = [f for f in audio_files if os.path.exists(f) and os.path.getsize(f) > 0]
            if not valid_files:
                logging.error("[VIDEO] Aucun fichier audio valide trouvé")
                self._save_silent_video()
                return True
                
            # Si nous avons déjà un rendu vidéo, utiliser add_audio_to_video
            if os.path.exists(self.output_path) and os.path.getsize(self.output_path) > 0:
                temp_audio_path = os.path.join(os.path.dirname(self.output_path), "temp_combined_audio.mp3")
                
                # Combiner les audios si nécessaire
                if len(valid_files) > 1:
                    # Charger les clips audio
                    try:
                        logging.info("[VIDEO] Combinaison des fichiers audio")
                        audio_clips = [AudioFileClip(f) for f in valid_files]
                        combined_audio = concatenate_audioclips(audio_clips)
                        combined_audio.write_audiofile(temp_audio_path, logger=None)
                        
                        # Fermer les clips audio
                        for clip in audio_clips:
                            clip.close()
                        combined_audio.close()
                        
                        return self.add_audio_to_video(self.output_path, temp_audio_path)
                    except Exception as e:
                        logging.error(f"[VIDEO] Erreur lors de la combinaison des audios: {str(e)}")
                        self._save_silent_video()
                        return True
                else:
                    # Un seul fichier audio, pas besoin de combiner
                    return self.add_audio_to_video(self.output_path, valid_files[0])
            
            # Charger les clips audio
            try:
                logging.info("[VIDEO] Chargement des fichiers audio")
                audio_clips = [AudioFileClip(f) for f in valid_files]
            except Exception as e:
                logging.error(f"[VIDEO] Erreur lors du chargement des audios: {str(e)}")
                self._save_silent_video()
                return True
            
            # Vérifier le timeout
            if time.time() - start_time > TIMEOUT:
                logging.warning(f"[VIDEO] Timeout dépassé ({TIMEOUT}s) pendant le chargement de l'audio")
                self._save_silent_video()
                return True
            
            # Créer le clip audio final
            final_audio = concatenate_audioclips(audio_clips)
            
            # Créer le clip vidéo final
            final_clip = self.get_final_video()
            
            # Ajouter l'audio à la vidéo
            final_clip = final_clip.set_audio(final_audio)
            
            # Sauvegarder la vidéo finale
            logging.info("[VIDEO] Sauvegarde de la vidéo avec audio...")
            final_clip.write_videofile(
                self.output_path,
                fps=self.fps,
                codec=self.video_codec,
                bitrate=self.video_bitrate,
                audio_codec='aac',
                audio_bitrate='192k',
                threads=4,
                logger=None
            )
            
            # Nettoyer
            final_clip.close()
            final_audio.close()
            for clip in audio_clips:
                clip.close()
                
            logging.info("[VIDEO] Vidéo avec audio créée avec succès")
            return True
            
        except Exception as e:
            logging.error(f"[VIDEO] Erreur lors de l'ajout de l'audio: {str(e)}")
            error_details = traceback.format_exc()
            logging.debug(f"[VIDEO] Détails de l'erreur: {error_details}")
            self._save_silent_video()
            return True

    def _save_silent_video(self):
        """Sauvegarde la vidéo sans audio en cas d'erreur"""
        try:
            logging.info("[VIDEO] Sauvegarde de la vidéo sans audio...")
            final_video = self.get_final_video()
            
            final_video.write_videofile(
                self.output_path,
                fps=self.fps,
                codec=self.video_codec,
                bitrate=self.video_bitrate,
                audio=False,
                logger=None
            )
            
            final_video.close()
            logging.info(f"[VIDEO] Vidéo sans audio créée avec succès: {self.output_path}")
            return True
        except Exception as e:
            logging.error(f"[VIDEO] Erreur lors de la sauvegarde de la vidéo sans audio: {str(e)}")
            return False

    def get_final_video(self):
        """Renvoie la vidéo finale en concaténant tous les clips"""
        try:
            # Concaténer tous les clips vidéo
            image_clips = [img_data['path'] for img_data in self.images]
            final_video = concatenate_videoclips(image_clips, method="compose")
            return final_video
        except Exception as e:
            logging.error(f"[VIDEO] Erreur lors de la création de la vidéo finale: {str(e)}")
            return None

    def clean_resources(self):
        """Nettoie toutes les ressources pour éviter les fuites de mémoire."""
        try:
            # Fermer tous les clips vidéo
            for img_data in self.images:
                if img_data['path'] and hasattr(img_data['path'], 'close'):
                    try:
                        img_data['path'].close()
                    except Exception as e:
                        logging.warning(f"Erreur lors de la fermeture d'un clip: {e}")
            
            # Vider la liste des clips
            self.images = []
            
            # Forcer le garbage collector pour libérer la mémoire
            import gc
            gc.collect()
            
            logging.info("Ressources nettoyées avec succès")
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage des ressources: {e}")
            return False

    def render(self):
        """
        Crée une vidéo à partir des images ajoutées.
        
        Returns:
            bool: True si le rendu a réussi, False sinon
        """
        if not self.images:
            logging.error("[VIDEO] Aucune image fournie pour la vidéo")
            return False
            
        # Assurer que le répertoire de sortie existe
        output_dir = os.path.dirname(self.output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            start_render_time = time.time()
            logging.info(f"[VIDEO] Rendu de {len(self.images)} images...")
            
            # Créer une liste de clips d'images
            image_clips = []
            for img_data in self.images:
                img_path = img_data['path']
                duration = img_data['duration']
                image_clips.append(img_path.set_duration(duration))
            
            # Concaténer les clips d'images
            final_clip = concatenate_videoclips(image_clips, method="compose")
            
            # Sauvegarder la vidéo
            final_clip.write_videofile(
                self.output_path,
                fps=self.fps,
                codec=self.video_codec,
                bitrate=self.video_bitrate,
                audio=False,
                threads=4,
                logger=None
            )
            
            # Fermer tous les clips
            final_clip.close()
            for clip in image_clips:
                clip.close()
            
            render_time = time.time() - start_render_time
            logging.info(f"[VIDEO] Rendu terminé en {render_time:.2f} secondes")
            
            # Vérifier que la vidéo a bien été créée
            if not os.path.exists(self.output_path) or os.path.getsize(self.output_path) < 1024:
                logging.error(f"[VIDEO] La vidéo n'a pas été créée correctement ou est vide: {self.output_path}")
                return False
                
            logging.info(f"[VIDEO] Vidéo créée avec succès: {self.output_path}")
            return True
            
        except Exception as e:
            logging.error(f"[VIDEO] Erreur lors du rendu de la vidéo: {str(e)}")
            traceback.print_exc()
            return False

    def add_audio_to_video(self, video_path, audio_path, output_path=None):
        """
        Ajoute un fichier audio à un fichier vidéo existant.
        
        Args:
            video_path: Chemin vers le fichier vidéo
            audio_path: Chemin vers le fichier audio
            output_path: Chemin de sortie (si None, utilise le même que video_path)
            
        Returns:
            bool: True si la combinaison a réussi, False sinon
        """
        if not os.path.exists(video_path):
            logging.error(f"[VIDEO] Le fichier vidéo n'existe pas: {video_path}")
            return False
            
        if not os.path.exists(audio_path):
            logging.error(f"[VIDEO] Le fichier audio n'existe pas: {audio_path}")
            return False
            
        # Si aucun chemin de sortie n'est spécifié, utiliser le même que la vidéo d'entrée
        if output_path is None:
            output_path = video_path
            
        # Créer un fichier temporaire pour la sortie
        tmp_output = f"{output_path}.tmp.mp4"
        
        try:
            logging.info("[VIDEO] Début de l'ajout d'audio")
            
            # Charger les fichiers vidéo et audio
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            # Vérifier si la durée de l'audio est suffisante
            if audio_clip.duration < video_clip.duration:
                logging.warning(f"[VIDEO] L'audio ({audio_clip.duration:.2f}s) est plus court que la vidéo ({video_clip.duration:.2f}s)")
            
            # Ajouter l'audio à la vidéo
            video_with_audio = video_clip.set_audio(audio_clip)
            
            # Sauvegarder la vidéo avec audio
            logging.info("[VIDEO] Sauvegarde de la vidéo avec audio...")
            video_with_audio.write_videofile(
                tmp_output,
                codec=self.video_codec,
                bitrate=self.video_bitrate,
                audio_codec='aac',
                audio_bitrate='192k',
                threads=4,
                logger=None
            )
            
            # Fermer les clips
            video_clip.close()
            audio_clip.close()
            video_with_audio.close()
            
            # Remplacer le fichier original par le fichier temporaire
            if os.path.exists(tmp_output):
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(tmp_output, output_path)
                logging.info("[VIDEO] Vidéo avec audio créée avec succès")
                return True
            else:
                logging.error("[VIDEO] Échec de la création de la vidéo avec audio")
                return False
                
        except Exception as e:
            logging.error(f"[VIDEO] Erreur lors de l'ajout de l'audio à la vidéo: {str(e)}")
            error_details = traceback.format_exc()
            logging.debug(f"[VIDEO] Détails de l'erreur: {error_details}")
            
            # En cas d'erreur, supprimer le fichier temporaire s'il existe
            if os.path.exists(tmp_output):
                try:
                    os.remove(tmp_output)
                except:
                    pass
                    
            return False

    def _create_temp_video(self, images, duration_per_image=5.0, loop=False, fps=30, output_path=None):
        """
        Crée une vidéo temporaire à partir d'une liste d'images.
        
        Args:
            images (list): Liste des chemins d'images à utiliser
            duration_per_image (float): Durée de chaque image en secondes
            loop (bool): Si True, la vidéo sera en boucle
            fps (int): Images par seconde
            output_path (str): Chemin de sortie pour la vidéo (si None, un chemin temporaire sera utilisé)
            
        Returns:
            str: Chemin vers la vidéo créée
        """
        if not images:
            logging.error("[VIDEO] Aucune image fournie pour la vidéo")
            return None
            
        # Assurer que le répertoire de sortie existe
        if output_path:
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
        else:
            # Créer un fichier temporaire
            output_path = os.path.join(self.temp_dir, f"temp_video_{int(time.time())}.mp4")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self.output_path = output_path
        
        try:
            start_render_time = time.time()
            logging.info(f"[VIDEO] Rendu de {len(images)} images...")
            
            # Créer une liste de clips d'images
            image_clips = [ImageClip(img).set_duration(duration_per_image) for img in images]
            
            # Concaténer les clips d'images
            final_clip = concatenate_videoclips(image_clips, method="compose")
            
            # Sauvegarder la vidéo
            final_clip.write_videofile(
                output_path,
                fps=fps,
                codec=self.video_codec,
                bitrate=self.video_bitrate,
                audio=False,
                logger=None
            )
            
            final_clip.close()
            
            logging.info(f"[VIDEO] Vidéo temporaire créée avec succès: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"[VIDEO] Erreur lors de la création de la vidéo temporaire: {str(e)}")
            return None
