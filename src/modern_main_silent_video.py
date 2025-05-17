import sys
import os
import time
import re
import uuid
import logging
from PIL import Image
import cv2
import numpy as np

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from utils.redditScrape import scrapeComments
from utils.modern_captions import ModernCaptionMaker
from pathlib import Path
from config import OUTPUT_CONFIG, LOGGING_CONFIG

# Logger configuration
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG.get("level", "INFO")),
    format=LOGGING_CONFIG.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

if LOGGING_CONFIG.get("log_to_file", False):
    file_handler = logging.FileHandler(LOGGING_CONFIG.get("log_file", "reddit_video_maker.log"))
    file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG.get("format")))
    logging.getLogger().addHandler(file_handler)

logger = logging.getLogger("RedditSilentVideoCreator")

class RedditSilentVideoCreator:
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir if output_dir else OUTPUT_CONFIG.get("base_directory", "output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.subdirs = {
            "title": "titre",
            "comments": "commentaires",
            "video": "video"
        }
        
        self.caption_maker = ModernCaptionMaker(
            title_border_color=(255, 0, 0),  # Red borders for title
            comment_border_color=(0, 0, 255)  # Blue borders for comments
        )
        logger.info(f"RedditSilentVideoCreator initialized with output directory: {self.output_dir}")
        
    def sanitize_filename(self, name):
        name = re.sub(r'[^\w\s-]', '_', name)
        name = re.sub(r'\s+', '-', name)
        return name[:50] if len(name) > 50 else name

    def create_silent_video(self, image_paths, output_path, duration_per_image=11):
        """Create a silent video from images with smooth transitions."""
        if not image_paths:
            logger.error("No images provided for video creation")
            return

        # Read first image to get dimensions
        img = cv2.imread(str(image_paths[0]))
        height, width = img.shape[:2]
        
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 30
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        for i, img_path in enumerate(image_paths):
            img = cv2.imread(str(img_path))
            
            # Calculate number of frames for this image
            frames_per_image = int(duration_per_image * fps)
            
            # Add static image frames
            for _ in range(frames_per_image):
                out.write(img)

            # Add fade transition if not the last image
            if i < len(image_paths) - 1:
                next_img = cv2.imread(str(image_paths[i + 1]))
                transition_frames = 15  # 0.5 seconds at 30fps
                
                for j in range(transition_frames):
                    alpha = j / transition_frames
                    blended = cv2.addWeighted(img, 1 - alpha, next_img, alpha, 0)
                    out.write(blended)

        out.release()
        
    def create_content(self, subreddit="askreddit", timeframe="day", post_count=1):
        logger.info(f"Starting content creation: subreddit={subreddit}, timeframe={timeframe}, post_count={post_count}")
        
        post_data = scrapeComments(subreddit, post_count, timeframe)
        if not post_data:
            logger.error("No posts found")
            return
            
        for post_index, post in enumerate(post_data[:post_count]):
            logger.info(f"Processing post {post_index+1}/{min(post_count, len(post_data))}")
            
            author = str(post.author) if post.author else "[deleted]"
            sanitized_title = self.sanitize_filename(post.title)
            
            post_id = f"{subreddit}_{sanitized_title}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            post_dir = self.output_dir / post_id
            title_dir = post_dir / self.subdirs["title"]
            comments_dir = post_dir / self.subdirs["comments"]
            video_dir = post_dir / self.subdirs["video"]
            
            for d in [title_dir, comments_dir, video_dir]:
                d.mkdir(parents=True, exist_ok=True)
                
            with open(post_dir / "metadata.txt", "w", encoding="utf-8") as f:
                f.write(f"Title: {post.title}\n")
                f.write(f"Author: {author}\n")
                f.write(f"Subreddit: r/{post.subreddit}\n")
                f.write(f"URL: {post.url}\n")
                f.write(f"Date: {time.ctime()}\n")
                f.write(f"ID: {post_id}\n")
            
            # 1. Create images (1 title + 10 comments)
            logger.info("Creating images...")
            title_image = self.caption_maker.create_title_card(
                post.title, 
                author, 
                f"r/{post.subreddit}",
                futuristic_style=True  # Enable futuristic style
            )
            title_image_path = title_dir / "title.png"
            title_image.save(title_image_path)
            
            with open(title_dir / "title.txt", "w", encoding="utf-8") as f:
                f.write(post.title)
            
            image_paths = [title_image_path]
            comments = []
            max_comments = 10  # Increased to 10 comments
            
            for i, comment in enumerate(post_data[post_index+1:]):
                if i >= max_comments:
                    break
                    
                comment_author = str(comment.author) if comment.author else "[deleted]"
                comment_text = comment.body
                
                comment_dir = comments_dir / f"comment_{i}"
                comment_dir.mkdir(exist_ok=True)
                
                with open(comment_dir / "text.txt", "w", encoding="utf-8") as f:
                    f.write(comment_text)
                
                img = self.caption_maker.create_comment_card(
                    comment_text,
                    comment_author,
                    i,
                    futuristic_style=True  # Enable futuristic style
                )
                img_path = comment_dir / "capture.png"
                img.save(img_path)
                image_paths.append(img_path)
                comments.append({"text": comment_text, "path": img_path, "dir": comment_dir})
            
            # 2. Create silent video
            logger.info("Creating silent video...")
            video_output_path = video_dir / "final_video_silent.mp4"
            self.create_silent_video(image_paths, video_output_path)
            
            logger.info(f"Content created successfully in directory: {post_dir}")

if __name__ == "__main__":
    creator = RedditSilentVideoCreator()
    creator.create_content()
