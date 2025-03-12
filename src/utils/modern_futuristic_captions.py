from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import textwrap
import logging
import os
import sys

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import VIDEO_CONFIG

logger = logging.getLogger("ModernFuturisticCaptionMaker")

class ModernFuturisticCaptionMaker:
    def __init__(self, size=None):
        """Initialize the futuristic caption maker"""
        # Use configuration size or default
        if size is None:
            width = VIDEO_CONFIG.get("width", 1080)
            height = VIDEO_CONFIG.get("height", 1920)
            self.size = (width, height)
        else:
            self.size = size
            
        self.width, self.height = self.size
        
        # Theme colors
        self.background_color = (25, 25, 25)  # Dark background
        self.text_color = (255, 255, 255)  # White text
        self.title_border_color = (255, 0, 0)  # Red borders for title
        self.comment_border_color = (0, 0, 255)  # Blue borders for comments
        
        # Font configuration
        self.base_font_size = VIDEO_CONFIG.get("font_size", 40)
        self.title_font_size = int(self.base_font_size * 1.2)
        self.comment_font_size = self.base_font_size
        self.meta_font_size = int(self.base_font_size * 0.8)
        
        # Find fonts
        self.font_path = str(Path(__file__).parent.parent.parent / "resources" / "fonts" / "helvetica.ttf")
        if not os.path.exists(self.font_path):
            logger.warning(f"Font {self.font_path} not found. Using default font.")
            self.font_path = "arial.ttf"
            
        logger.debug(f"ModernFuturisticCaptionMaker initialized with size={self.size}")

    def _add_futuristic_elements(self, image, draw, x, y, width, height, is_title=True):
        """Add futuristic design elements to the card"""
        border_color = self.title_border_color if is_title else self.comment_border_color
        
        # Draw angular corners
        corner_size = 30
        line_width = 3
        
        # Top left corner
        draw.line([(x, y + corner_size), (x, y), (x + corner_size, y)], 
                 fill=border_color, width=line_width)
        
        # Top right corner
        draw.line([(x + width - corner_size, y), (x + width, y), (x + width, y + corner_size)], 
                 fill=border_color, width=line_width)
        
        # Bottom left corner
        draw.line([(x, y + height - corner_size), (x, y + height), (x + corner_size, y + height)], 
                 fill=border_color, width=line_width)
        
        # Bottom right corner
        draw.line([(x + width - corner_size, y + height), (x + width, y + height), (x + width, y + height - corner_size)], 
                 fill=border_color, width=line_width)
        
        # Add tech lines
        line_spacing = 40
        short_line_length = 15
        
        # Side tech lines
        for i in range(2):
            y_pos = y + height//3 + (i * line_spacing)
            draw.line([(x - short_line_length, y_pos), (x, y_pos)], 
                     fill=border_color, width=2)
            draw.line([(x + width, y_pos), (x + width + short_line_length, y_pos)], 
                     fill=border_color, width=2)

    def create_title_card(self, title, author, subreddit):
        """Create a futuristic title card"""
        # Create base image
        image = Image.new('RGB', self.size, self.background_color)
        draw = ImageDraw.Draw(image)
        
        # Prepare fonts
        title_font = ImageFont.truetype(self.font_path, self.title_font_size)
        meta_font = ImageFont.truetype(self.font_path, self.meta_font_size)
        
        # Add r/ prefix if needed
        if not subreddit.startswith('r/'):
            subreddit = f'r/{subreddit}'
            
        # Calculate text dimensions
        title_lines = textwrap.wrap(title, width=30)
        title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] for line in title_lines)
        
        meta_text = f'Posted by u/{author} on {subreddit}'
        meta_height = draw.textbbox((0, 0), meta_text, font=meta_font)[3]
        
        # Card dimensions
        padding = 40
        card_width = int(self.width * 0.9)
        card_height = title_height + meta_height + padding * 3
        
        # Card position
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        # Draw card background with gradient
        card_bg = Image.new('RGBA', (card_width, card_height), (45, 45, 45, 230))
        image.paste(card_bg, (card_x, card_y), card_bg)
        
        # Add futuristic elements
        self._add_futuristic_elements(image, draw, card_x, card_y, card_width, card_height, is_title=True)
        
        # Draw title
        y = card_y + padding
        for line in title_lines:
            draw.text((card_x + padding, y), line, font=title_font, fill=self.text_color)
            y += draw.textbbox((0, 0), line, font=title_font)[3]
        
        # Draw metadata
        draw.text((card_x + padding, y + padding), meta_text, font=meta_font, fill=(200, 200, 200))
        
        return image

    def create_comment_card(self, text, author, comment_num):
        """Create a futuristic comment card"""
        # Create base image
        image = Image.new('RGB', self.size, self.background_color)
        draw = ImageDraw.Draw(image)
        
        # Prepare fonts
        comment_font = ImageFont.truetype(self.font_path, self.comment_font_size)
        meta_font = ImageFont.truetype(self.font_path, self.meta_font_size)
        
        # Calculate text dimensions
        text_lines = textwrap.wrap(text, width=35)
        text_height = sum(draw.textbbox((0, 0), line, font=comment_font)[3] for line in text_lines)
        
        meta_text = f'u/{author}'
        meta_height = draw.textbbox((0, 0), meta_text, font=meta_font)[3]
        
        # Card dimensions
        padding = 40
        card_width = int(self.width * 0.9)
        card_height = text_height + meta_height + padding * 3
        
        # Card position - adjust based on comment number
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        # Draw card background with gradient
        card_bg = Image.new('RGBA', (card_width, card_height), (45, 45, 45, 230))
        image.paste(card_bg, (card_x, card_y), card_bg)
        
        # Add futuristic elements
        self._add_futuristic_elements(image, draw, card_x, card_y, card_width, card_height, is_title=False)
        
        # Draw comment text
        y = card_y + padding
        for line in text_lines:
            draw.text((card_x + padding, y), line, font=comment_font, fill=self.text_color)
            y += draw.textbbox((0, 0), line, font=comment_font)[3]
        
        # Draw metadata
        draw.text((card_x + padding, y + padding), meta_text, font=meta_font, fill=(200, 200, 200))
        
        return image
