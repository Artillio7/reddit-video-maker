from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import textwrap
import logging
import os
import sys

# Ajout du répertoire parent au chemin Python pour pouvoir importer config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import VIDEO_CONFIG

logger = logging.getLogger("ModernCaptionMaker")

class CommentCardCreator:
    """
    Classe pour créer des cartes de titre et commentaires dans un style moderne pour les vidéos TikTok.
    Supporte la génération de fichiers images.
    """
    
    def __init__(self, width=1080, height=1920):
        """
        Initialisation du créateur de cartes
        
        Args:
            width: Largeur des images (par défaut 1080px)
            height: Hauteur des images (par défaut 1920px)
        """
        self.width = width
        self.height = height
        self.size = (width, height)
        
        # Couleurs du thème
        self.background_color = (25, 25, 25)  # Fond sombre
        self.text_color = (255, 255, 255)     # Texte blanc
        self.accent_color = (255, 69, 0)      # Accent Reddit
        self.card_bg_color = (45, 45, 45, 230) # Fond des cartes
        
        # Polices
        self.font_path = self._find_font()
        self.title_font_size = 48
        self.body_font_size = 38
        self.meta_font_size = 30
        
        # Créer le dossier temporaire s'il n'existe pas
        os.makedirs("temp", exist_ok=True)
        
        logger.info(f"CommentCardCreator initialisé ({width}x{height})")
    
    def _find_font(self):
        """Trouve une police système ou utilise celle du projet."""
        # Chemins possibles pour les polices
        possible_paths = [
            Path(__file__).parent.parent.parent / "resources" / "fonts" / "helvetica.ttf",
            Path(__file__).parent.parent.parent / "resources" / "fonts" / "arial.ttf",
            Path(__file__).parent.parent.parent / "resources" / "fonts" / "roboto.ttf",
        ]
        
        # Chercher les polices
        for font_path in possible_paths:
            if os.path.exists(font_path):
                return str(font_path)
        
        # Sinon utiliser une police système
        logger.warning("Aucune police trouvée dans le projet, utilisation d'une police système")
        return "arial.ttf"
    
    def create_title_card(self, title, subreddit, author, output_path=None):
        """
        Crée une carte de titre pour le post Reddit.
        
        Args:
            title: Titre du post
            subreddit: Nom du subreddit (avec ou sans le préfixe r/)
            author: Auteur du post
            output_path: Chemin de sortie pour l'image
            
        Returns:
            Chemin de l'image créée
        """
        # Créer l'image
        image = Image.new('RGB', self.size, self.background_color)
        draw = ImageDraw.Draw(image)
        
        # Préparer les polices
        title_font = ImageFont.truetype(self.font_path, self.title_font_size)
        meta_font = ImageFont.truetype(self.font_path, self.meta_font_size)
        
        # Ajouter le préfixe r/ si nécessaire
        if not subreddit.startswith("r/"):
            subreddit = f"r/{subreddit}"
        
        # Wrapper le titre pour qu'il s'adapte à l'écran
        max_chars = int(self.width / (self.title_font_size * 0.5))
        wrapped_title = textwrap.fill(title, width=max_chars)
        
        # Créer un fond de carte
        card_padding = 40
        title_bbox = draw.textbbox((0, 0), wrapped_title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        
        meta_text = f"Posted by u/{author} on {subreddit}"
        meta_bbox = draw.textbbox((0, 0), meta_text, font=meta_font)
        meta_height = meta_bbox[3] - meta_bbox[1]
        
        # Dimensions de la carte
        card_width = min(self.width - 80, title_width + card_padding * 2)
        card_height = title_height + meta_height + card_padding * 3
        
        # Position de la carte
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2 - 100  # Légèrement plus haut que le centre
        
        # Dessiner la carte avec un effet d'ombre
        shadow_offset = 8
        shadow = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 100))
        image.paste(shadow, (card_x + shadow_offset, card_y + shadow_offset), shadow)
        
        card = Image.new('RGBA', (card_width, card_height), self.card_bg_color)
        image.paste(card, (card_x, card_y), card)
        
        # Dessiner une barre d'accent en haut de la carte
        accent_bar_height = 6
        accent_bar = Image.new('RGBA', (card_width, accent_bar_height), self.accent_color)
        image.paste(accent_bar, (card_x, card_y), accent_bar)
        
        # Dessiner le titre
        title_x = card_x + card_padding
        title_y = card_y + card_padding + accent_bar_height
        draw.text((title_x, title_y), wrapped_title, font=title_font, fill=self.text_color)
        
        # Dessiner les métadonnées
        meta_x = card_x + card_padding
        meta_y = title_y + title_height + card_padding
        draw.text((meta_x, meta_y), meta_text, font=meta_font, fill=(200, 200, 200))
        
        # Sauvegarder l'image si un chemin est spécifié
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)
            logger.info(f"Carte de titre créée: {output_path}")
            return output_path
        
        return image
    
    def create_comment_card(self, comment_text, author, upvotes=0, output_path=None, media=None):
        """
        Crée une carte de commentaire Reddit.
        
        Args:
            comment_text: Texte du commentaire
            author: Auteur du commentaire
            upvotes: Nombre de votes positifs
            output_path: Chemin de sortie pour l'image
            media: Dictionnaire contenant les chemins des fichiers médias {'image_files': [], 'video_files': []}
            
        Returns:
            Chemin de l'image créée
        """
        # Créer l'image
        image = Image.new('RGB', self.size, self.background_color)
        draw = ImageDraw.Draw(image)
        
        # Préparer les polices
        body_font = ImageFont.truetype(self.font_path, self.body_font_size)
        meta_font = ImageFont.truetype(self.font_path, self.meta_font_size)
        
        # Wrapper le texte du commentaire
        max_chars = int(self.width / (self.body_font_size * 0.6))
        wrapped_comment = textwrap.fill(comment_text, width=max_chars)
        
        # Calculer les dimensions du texte
        comment_bbox = draw.textbbox((0, 0), wrapped_comment, font=body_font)
        comment_width = comment_bbox[2] - comment_bbox[0]
        comment_height = comment_bbox[3] - comment_bbox[1]
        
        # Texte des métadonnées
        meta_text = f"u/{author} • {upvotes:,} points"
        meta_bbox = draw.textbbox((0, 0), meta_text, font=meta_font)
        meta_height = meta_bbox[3] - meta_bbox[1]
        
        # Dimensions de la carte
        card_padding = 40
        card_width = min(self.width - 80, comment_width + card_padding * 2)
        
        # Vérifier s'il y a des médias à inclure
        media_height = 0
        media_image = None
        
        if media and 'image_files' in media and media['image_files']:
            try:
                # Utiliser la première image trouvée
                media_path = media['image_files'][0]
                
                # Ouvrir l'image média
                media_img = Image.open(media_path)
                
                # Calculer les dimensions pour conserver le ratio d'aspect
                media_width = min(card_width - card_padding * 2, 800)  # Max width
                ratio = media_width / media_img.width
                media_height = int(media_img.height * ratio)
                
                # Redimensionner l'image média
                media_image = media_img.resize((media_width, media_height), Image.LANCZOS)
                
                # Ajouter une marge au-dessus du média
                media_height += card_padding
                
                logging.info(f"Image media integree: {media_path}")
            except Exception as e:
                logging.error(f"Erreur lors de l'integration de l'image media: {e}")
                media_height = 0
                media_image = None
        
        # Hauteur totale de la carte avec médias
        card_height = comment_height + meta_height + card_padding * 3 + media_height
        
        # Position de la carte
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        # Dessiner la carte avec un effet d'ombre
        shadow_offset = 8
        shadow = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 100))
        image.paste(shadow, (card_x + shadow_offset, card_y + shadow_offset), shadow)
        
        card = Image.new('RGBA', (card_width, card_height), self.card_bg_color)
        card_draw = ImageDraw.Draw(card)
        
        # Ajouter une bordure subtile
        card_draw.rectangle((0, 0, card_width-1, card_height-1), outline=(100, 100, 100, 128), width=1)
        
        image.paste(card, (card_x, card_y), card)
        
        # Dessiner les métadonnées en haut
        meta_x = card_padding
        meta_y = card_padding
        card_draw.text((meta_x, meta_y), meta_text, font=meta_font, fill=(180, 180, 180))
        
        # Ligne de séparation
        line_y = meta_y + meta_height + card_padding // 2
        card_draw.line([(card_padding, line_y), (card_width - card_padding, line_y)], 
                      fill=(100, 100, 100), width=1)
        
        # Position du texte du commentaire
        comment_x = card_padding
        comment_y = line_y + card_padding // 2
        
        # Ajouter l'image média si disponible
        if media_image:
            # Coller l'image média
            media_x = (card_width - media_image.width) // 2
            card.paste(media_image, (media_x, comment_y))
            
            # Décaler le texte du commentaire en dessous de l'image
            comment_y += media_height
        
        # Dessiner le texte du commentaire
        card_draw.text((comment_x, comment_y), wrapped_comment, font=body_font, fill=(255, 255, 255))
        
        # Ajouter le logo de vote positif
        upvote_size = 20
        upvote_x = len(f"u/{author} •") * (self.meta_font_size // 2) + meta_x + 10
        upvote_y = meta_y + (meta_height - upvote_size) // 2
        
        # Dessiner une flèche vers le haut simplifiée
        card_draw.polygon([(upvote_x + upvote_size//2, upvote_y), 
                         (upvote_x, upvote_y + upvote_size), 
                         (upvote_x + upvote_size, upvote_y + upvote_size)], 
                        fill=self.accent_color)
        
        # Ajouter l'image combinée à l'image principale
        image.paste(card, (card_x, card_y), card)
        
        # Sauvegarder l'image si un chemin est spécifié
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)
            logger.info(f"Carte de commentaire créée: {output_path}")
            return output_path
        
        return image

class ModernCaptionMaker:
    def __init__(self, size=None):
        """
        Initialisation du créateur de cartes de titre et commentaires
        
        Args:
            size: Taille personnalisée de l'image (width, height). Par défaut utilise la configuration
        """
        # Utiliser la taille de la configuration ou la valeur par défaut
        if size is None:
            width = VIDEO_CONFIG.get("width", 1080)
            height = VIDEO_CONFIG.get("height", 1920)
            self.size = (width, height)
        else:
            self.size = size
            
        self.width, self.height = self.size
        
        # Couleurs du thème à partir de la configuration
        self.background_color = VIDEO_CONFIG.get("background_color", (39, 41, 49))
        self.text_color = VIDEO_CONFIG.get("text_color", (255, 255, 255))
        self.accent_color = (0, 162, 255)  # Couleur d'accentuation pour les éléments visuels
        
        # Taille de police à partir de la configuration
        self.base_font_size = VIDEO_CONFIG.get("font_size", 40)
        
        # Trouver les polices dans le projet
        self.font_path = str(Path(__file__).parent.parent.parent / "resources" / "fonts" / "helvetica.ttf")
        if not os.path.exists(self.font_path):
            logger.warning(f"Police {self.font_path} non trouvée. Utilisation de la police par défaut.")
            # Utiliser une police par défaut disponible sur la plupart des systèmes
            self.font_path = "arial.ttf"
            
        logger.debug(f"ModernCaptionMaker initialisé avec taille={self.size}, police={self.font_path}")
        
    def create_title_card(self, title, author, subreddit):
        """
        Crée une image de titre moderne pour TikTok
        
        Args:
            title: Titre du post Reddit
            author: Auteur du post
            subreddit: Nom du subreddit (avec ou sans 'r/')
            
        Returns:
            Image PIL du titre formaté
        """
        # Création de l'image
        image = Image.new('RGB', self.size, self.background_color)
        draw = ImageDraw.Draw(image)
        
        # Configuration des polices
        title_font = ImageFont.truetype(self.font_path, int(self.base_font_size * 1.2))
        meta_font = ImageFont.truetype(self.font_path, int(self.base_font_size * 0.8))
        
        # Wrapper le texte (ajuster la largeur en fonction de la largeur de l'écran)
        wrap_width = int(30 * (self.width / 1080))  # Ajuster en fonction de la largeur
        wrapped_title = textwrap.fill(title, width=wrap_width)
        
        # Position du titre
        title_bbox = draw.textbbox((0, 0), wrapped_title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        title_x = (self.width - title_width) // 2
        title_y = (self.height - title_height) // 2 - 100
        
        # Créer un effet de "carte" avec ombre
        padding = 30
        shadow_offset = 8
        
        # Dessiner l'ombre de la carte
        shadow = Image.new('RGBA', (title_width + padding*2, title_height + padding*2), (0, 0, 0, 80))
        image.paste(shadow, (title_x - padding + shadow_offset, title_y - padding + shadow_offset), shadow)
        
        # Dessiner le fond de la carte
        title_bg = Image.new('RGBA', (title_width + padding*2, title_height + padding*2), (255, 255, 255, 40))
        image.paste(title_bg, (title_x - padding, title_y - padding), title_bg)
        
        # Dessiner une barre d'accentuation au-dessus du titre
        accent_bar = Image.new('RGBA', (title_width + padding*2, 5), self.accent_color)
        image.paste(accent_bar, (title_x - padding, title_y - padding - 5), accent_bar)
        
        # Dessiner le titre
        draw.text((title_x, title_y), wrapped_title, 
                 font=title_font, fill=self.text_color)
        
        # Dessiner les métadonnées
        if not subreddit.startswith("r/"):
            subreddit = f"r/{subreddit}"
            
        meta_text = f"Posted by {author} in {subreddit}"
        meta_bbox = draw.textbbox((0, 0), meta_text, font=meta_font)
        meta_width = meta_bbox[2] - meta_bbox[0]
        meta_x = (self.width - meta_width) // 2
        meta_y = title_y + title_height + 50
        
        # Effet de soulignement moderne
        line_y = meta_y + meta_bbox[3] - meta_bbox[1] + 5
        draw.line([(meta_x, line_y), (meta_x + meta_width, line_y)], 
                 fill=self.accent_color, width=3)
        
        draw.text((meta_x, meta_y), meta_text, 
                 font=meta_font, fill=self.text_color)
        
        # Ajouter un logo Reddit stylisé
        logo_size = 50
        logo_x = (self.width - logo_size) // 2
        logo_y = meta_y + meta_bbox[3] - meta_bbox[1] + 20
        
        # Dessiner un cercle pour le logo Reddit (simplifié)
        circle_bg = Image.new('RGBA', (logo_size, logo_size), (0, 0, 0, 0))
        circle_draw = ImageDraw.Draw(circle_bg)
        circle_draw.ellipse((0, 0, logo_size, logo_size), fill=(255, 69, 0, 200))
        image.paste(circle_bg, (logo_x, logo_y), circle_bg)
                  
        return image
        
    def create_comment_card(self, text, author, comment_num):
        """
        Crée une image de commentaire moderne
        
        Args:
            text: Texte du commentaire
            author: Auteur du commentaire
            comment_num: Numéro du commentaire (pour le positionnement séquentiel)
            
        Returns:
            Image PIL du commentaire formaté
        """
        # Création de l'image
        image = Image.new('RGB', self.size, self.background_color)
        draw = ImageDraw.Draw(image)
        
        # Configuration des polices
        comment_font = ImageFont.truetype(self.font_path, int(self.base_font_size * 0.9))
        author_font = ImageFont.truetype(self.font_path, int(self.base_font_size * 0.7))
        
        # Wrapper le texte du commentaire
        wrap_width = int(35 * (self.width / 1080))
        wrapped_text = textwrap.fill(text, width=wrap_width)
        
        # Position du commentaire (avec un léger décalage en fonction du numéro du commentaire)
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=comment_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Variation de position pour créer un effet de profondeur entre les commentaires
        offset_y = (comment_num % 3) * 20  # Varie légèrement la position Y
        text_x = (self.width - text_width) // 2
        text_y = (self.height - text_height) // 2 + offset_y
        
        # Effet de carte moderne avec ombre portée
        padding = 30
        card_width = text_width + padding * 2
        card_height = text_height + padding * 2 + 60  # Espace supplémentaire pour l'auteur
        
        # Ombre de la carte
        shadow_offset = 10
        shadow = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 60))
        image.paste(shadow, (
            (self.width - card_width) // 2 + shadow_offset, 
            text_y - padding + shadow_offset
        ), shadow)
        
        # Carte principale
        card = Image.new('RGBA', (card_width, card_height), (255, 255, 255, 30))
        card_draw = ImageDraw.Draw(card)
        
        # Ajouter un effet de dégradé subtil sur la carte
        for i in range(card_height):
            alpha = 30 + int(20 * (i / card_height))  # Variation d'alpha pour créer un dégradé
            line_color = (255, 255, 255, min(alpha, 50))
            card_draw.line([(0, i), (card_width, i)], fill=line_color, width=1)
        
        # Ajouter un effet de bordure
        card_draw.rectangle((0, 0, card_width-1, card_height-1), 
                          outline=self.accent_color, width=2)
        
        # Ajouter une indication de numéro de commentaire dans le coin
        indicator_size = 24
        card_draw.ellipse((card_width - indicator_size - 10, 10, 
                          card_width - 10, 10 + indicator_size), 
                         fill=self.accent_color)
        
        # Ajouter le numéro dans l'indicateur
        indicator_font = ImageFont.truetype(self.font_path, indicator_size - 10)
        indicator_text = str(comment_num + 1)
        indicator_bbox = card_draw.textbbox((0, 0), indicator_text, font=indicator_font)
        indicator_width = indicator_bbox[2] - indicator_bbox[0]
        indicator_height = indicator_bbox[3] - indicator_bbox[1]
        
        card_draw.text((
            card_width - 10 - indicator_size/2 - indicator_width/2,
            10 + indicator_size/2 - indicator_height/2
        ), indicator_text, font=indicator_font, fill=self.text_color)
        
        # Placer la carte sur l'image
        card_x = (self.width - card_width) // 2
        card_y = text_y - padding
        image.paste(card, (card_x, card_y), card)
        
        # Dessiner le texte du commentaire
        draw.text((text_x, text_y), wrapped_text, 
                 font=comment_font, fill=self.text_color)
        
        # Dessiner l'auteur avec un style plus moderne
        author_text = f"Comment by {author}"
        author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (self.width - author_width) // 2
        author_y = text_y + text_height + 20
        
        # Ajouter un petit badge d'auteur
        badge_padding = 10
        badge_width = author_width + badge_padding * 2
        badge_height = author_bbox[3] - author_bbox[1] + badge_padding * 2
        badge = Image.new('RGBA', (badge_width, badge_height), self.accent_color + (100,))
        
        badge_x = author_x - badge_padding
        badge_y = author_y - badge_padding
        image.paste(badge, (badge_x, badge_y), badge)
        
        draw.text((author_x, author_y), author_text, 
                 font=author_font, fill=self.text_color)
                 
        return image
