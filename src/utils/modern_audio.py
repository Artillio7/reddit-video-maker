import os
import random
import numpy as np
from gtts import gTTS
from pathlib import Path
import logging
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips

class TTSGenerator:
    def __init__(self, language='en', tld='com', temp_dir='temp'):
        self.language = language
        self.tld = tld
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        logging.info(f"TTSGenerator initialisé (langue={language}, tld={tld})")
    
    def generate_tts(self, text, output_path=None, slow=False):
        if not text or not text.strip():
            logging.warning("Texte vide, impossible de générer TTS")
            return None
            
        if len(text) > 5000:
            logging.warning(f"Texte trop long ({len(text)} caractères), tronqué à 5000 caractères")
            text = text[:5000] + "..."
            
        if output_path is None:
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            output_path = os.path.join(self.temp_dir, f"tts_{text_hash}.mp3")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            logging.info(f"Génération TTS pour '{text[:50]}...' ({len(text)} caractères)")
            tts = gTTS(text=text, lang=self.language, tld=self.tld, slow=slow)
            tts.save(output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logging.info(f"TTS généré avec succès: {output_path}")
                return output_path
            else:
                logging.error(f"Échec de génération TTS: fichier vide ou non créé ({output_path})")
                return None
        except Exception as e:
            logging.error(f"Erreur lors de la génération TTS: {str(e)}")
            return None

    def combine_audio_files(self, audio_files, output_path):
        """
        Combine plusieurs fichiers audio en un seul en utilisant moviepy.
        
        Args:
            audio_files: Liste des chemins vers les fichiers audio à combiner
            output_path: Chemin de sortie pour le fichier audio combiné
            
        Returns:
            bool: True si la combinaison a réussi, False sinon
        """
        try:
            # Charger tous les clips audio
            audio_clips = [AudioFileClip(f) for f in audio_files if os.path.exists(f)]
            
            if not audio_clips:
                logging.error("Aucun fichier audio valide à combiner")
                return False
                
            # Concaténer les clips
            final_clip = concatenate_audioclips(audio_clips)
            
            # Sauvegarder le résultat
            final_clip.write_audiofile(output_path)
            
            # Nettoyer
            final_clip.close()
            for clip in audio_clips:
                clip.close()
                
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors de la combinaison des fichiers audio: {str(e)}")
            return False

class ModernAudioMaker:
    def __init__(self, output_dir="output", background_music_dir=None):
        self.output_dir = output_dir
        if background_music_dir is None:
            self.background_music_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "music")
        else:
            self.background_music_dir = background_music_dir
    
    def create_audio_for_text(self, text, output_path):
        try:
            tts = gTTS(text=text, lang='fr')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            tts.save(output_path)
            return output_path
        except Exception as e:
            logging.error(f"Erreur lors de la création de l'audio: {str(e)}")
            return None

    def combine_audio_files(self, audio_files, output_path, background_volume=0.3):
        try:
            logging.info("[AUDIO] Début de la combinaison des fichiers audio")
            
            # Vérifier les fichiers
            valid_files = [f for f in audio_files if os.path.exists(f)]
            if not valid_files:
                logging.error("[AUDIO] Aucun fichier audio valide à combiner")
                return False, []
            
            # Créer le dossier de sortie
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Charger les clips audio
            clips = []
            durations = []
            for audio_file in valid_files:
                try:
                    clip = AudioFileClip(audio_file)
                    clips.append(clip)
                    durations.append(clip.duration)
                except Exception as e:
                    logging.error(f"[AUDIO] Erreur lors du chargement de {audio_file}: {e}")
            
            if not clips:
                logging.error("[AUDIO] Aucun clip audio chargé")
                return False, []
            
            # Combiner les clips
            final_audio = CompositeAudioClip(clips)
            final_audio.write_audiofile(output_path, fps=44100, logger=None)
            
            # Nettoyer
            final_audio.close()
            for clip in clips:
                clip.close()
            
            return True, durations
            
        except Exception as e:
            logging.error(f"[AUDIO] Erreur lors de la combinaison audio: {str(e)}")
            return False, []
