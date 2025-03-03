import os
import re
import logging
import requests
from urllib.parse import urlparse
from pathlib import Path

class MediaExtractor:
    """
    Classe pour extraire et télécharger les médias (images, vidéos) des commentaires Reddit.
    """
    
    def __init__(self, output_dir=None):
        """
        Initialise l'extracteur de médias.
        
        Args:
            output_dir: Répertoire de sortie pour les médias téléchargés
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), "output")
        
        # Patterns pour différents types de médias
        self.image_patterns = [
            r'https?://(?:i\.redd\.it|preview\.redd\.it)/\S+',
            r'https?://(?:i\.imgur\.com)/\S+',
            r'https?://\S+\.(?:jpg|jpeg|png|gif|webp)(?:\?\S+)?'
        ]
        
        self.video_patterns = [
            r'https?://(?:v\.redd\.it)/\S+',
            r'https?://\S+\.(?:mp4|webm)(?:\?\S+)?'
        ]
        
        logging.info(f"MediaExtractor initialisé avec répertoire de sortie: {self.output_dir}")
    
    def extract_media_urls(self, text):
        """
        Extrait les URLs d'images et de vidéos d'un texte.
        
        Args:
            text: Texte contenant potentiellement des URLs
            
        Returns:
            dict: Dictionnaire contenant les URLs d'images et de vidéos trouvées
        """
        if not text:
            return {"images": [], "videos": []}
            
        # Extraire toutes les URLs du texte
        url_pattern = r'https?://\S+'
        all_urls = re.findall(url_pattern, text)
        
        # Filtrer les images et vidéos
        image_urls = []
        video_urls = []
        
        for url in all_urls:
            # Vérifier si c'est une image
            if any(re.match(pattern, url) for pattern in self.image_patterns):
                image_urls.append(url)
            # Vérifier si c'est une vidéo
            elif any(re.match(pattern, url) for pattern in self.video_patterns):
                video_urls.append(url)
        
        return {
            "images": image_urls,
            "videos": video_urls
        }
    
    def download_media(self, url, output_dir, prefix=None):
        """
        Télécharge un média à partir d'une URL.
        
        Args:
            url: URL du média à télécharger
            output_dir: Répertoire de sortie
            prefix: Préfixe pour le nom du fichier (optionnel)
            
        Returns:
            str: Chemin du fichier téléchargé ou None en cas d'échec
        """
        try:
            # Créer le répertoire de sortie s'il n'existe pas
            os.makedirs(output_dir, exist_ok=True)
            
            # Extraire le nom de fichier de l'URL
            parsed_url = urlparse(url)
            original_filename = os.path.basename(parsed_url.path)
            
            # Déterminer l'extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm']
            found_ext = None
            
            for ext in valid_extensions:
                if original_filename.lower().endswith(ext):
                    found_ext = ext
                    break
            
            if not found_ext:
                if any(pattern in url for pattern in ["i.redd.it", "preview.redd.it"]):
                    found_ext = ".jpg"
                elif "v.redd.it" in url:
                    found_ext = ".mp4"
                else:
                    found_ext = ".jpg"  # Par défaut
            
            # Créer un nom de fichier unique
            if prefix:
                filename = f"{prefix}{found_ext}"
            else:
                # Utiliser un horodatage si pas de préfixe
                import time
                timestamp = int(time.time())
                filename = f"media_{timestamp}{found_ext}"
            
            # Chemin complet du fichier de sortie
            output_path = os.path.join(output_dir, filename)
            
            # Télécharger le fichier
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            logging.info(f"Media telecharge: {url} -> {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Erreur lors du telechargement de {url}: {e}")
            return None
    
    def process_comment(self, comment_text, comment_id, post_id, output_dir=None):
        """
        Traite un commentaire pour extraire les médias qui y sont liés.
        
        Args:
            comment_text: Texte du commentaire
            comment_id: Identifiant du commentaire
            post_id: Identifiant du post parent (pour l'organisation des fichiers)
            output_dir: Répertoire de sortie (facultatif)
            
        Returns:
            dict: Dictionnaire contenant les fichiers médias extraits
        """
        # Structure de retour
        result = {
            "image_files": [],
            "video_files": []
        }
        
        # Extraire les URLs des médias
        media_urls = self.extract_media_urls(comment_text)
        
        # Si aucun média n'est trouvé, retourner un résultat vide sans créer de dossiers
        if not media_urls["images"] and not media_urls["videos"]:
            return result
            
        # Vérifier si nous avons des URLs valides avant de créer des dossiers
        has_valid_media = False
        
        # Valider les URLs d'images
        valid_image_urls = []
        for url in media_urls["images"]:
            if self.is_valid_url(url):
                valid_image_urls.append(url)
                has_valid_media = True
        
        # Valider les URLs de vidéos
        valid_video_urls = []
        for url in media_urls["videos"]:
            if self.is_valid_url(url):
                valid_video_urls.append(url)
                has_valid_media = True
        
        # Si aucun média valide n'est trouvé, ne pas créer de dossier
        if not has_valid_media:
            logging.info(f"Aucun média valide trouvé dans le commentaire")
            return result
            
        # Créer la structure de dossiers pour ce post/commentaire seulement si des médias sont détectés
        if output_dir is None:
            # Suivre la structure existante du projet
            post_dir = os.path.join(self.output_dir, post_id)
            images_dir = os.path.join(post_dir, "images", "comments_media")
            videos_dir = os.path.join(post_dir, "video", "comments_media")
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(videos_dir, exist_ok=True)
        else:
            images_dir = output_dir
            videos_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
        
        # Télécharger les images
        for i, url in enumerate(valid_image_urls):
            img_path = self.download_media(url, images_dir, f"{comment_id}_img_{i}")
            if img_path:
                result["image_files"].append(img_path)
        
        # Télécharger les vidéos
        for i, url in enumerate(valid_video_urls):
            video_path = self.download_media(url, videos_dir, f"{comment_id}_vid_{i}")
            if video_path:
                result["video_files"].append(video_path)
        
        return result

    def is_valid_url(self, url):
        """
        Vérifie si une URL est valide et accessible.
        
        Args:
            url (str): URL à vérifier
            
        Returns:
            bool: True si l'URL est valide, False sinon
        """
        if not url:
            return False
            
        try:
            # Vérifier si l'URL a un format valide
            parsed = urlparse(url)
            if not parsed.netloc or not parsed.scheme:
                return False
                
            # Vérifier les extensions d'images courantes
            if parsed.path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                return True
                
            # Vérifier les extensions de vidéos courantes
            if parsed.path.lower().endswith(('.mp4', '.webm', '.avi', '.mov', '.mkv')):
                return True
                
            # Vérifier les domaines d'hébergement courants
            image_hosts = ['i.imgur.com', 'imgur.com', 'i.redd.it', 'preview.redd.it', 
                          'upload.wikimedia.org', 'pbs.twimg.com', 'i.pinimg.com']
            video_hosts = ['v.redd.it', 'youtu.be', 'youtube.com', 'gfycat.com', 'streamable.com']
            
            if parsed.netloc in image_hosts or parsed.netloc in video_hosts:
                return True
                
            # Par défaut, considérer l'URL comme invalide
            return False
                
        except Exception:
            return False
