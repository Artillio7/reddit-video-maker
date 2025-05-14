import logging
from utils.redditScrape import RedditScraper
from utils.modern_audio import TTSGenerator, ModernAudioMaker

class AppController:
    """
    Contrôleur central orchestrant le scraping Reddit, la génération audio et l'assemblage vidéo.
    """
    def __init__(self, output_dir=None):
        self.output_dir = output_dir
        self.scraper = RedditScraper()
        self.tts = TTSGenerator()
        self.audio_maker = ModernAudioMaker()
        logging.info("AppController initialisé.")

    def run_full_pipeline(self, subreddit, timeframe, post_count, video_count, allow_nsfw, sorting, comment_sort):
        logging.info(f"[Controller] Scraping r/{subreddit}...")
        posts = self.scraper.get_reddit_posts(
            subreddit=subreddit,
            timeframe=timeframe,
            post_count=post_count,
            allow_nsfw=allow_nsfw,
            sorting=sorting,
            comment_sort=comment_sort
        )
        if not posts:
            logging.error("Aucun post Reddit récupéré. Arrêt du pipeline.")
            return []
        logging.info(f"[Controller] {len(posts)} posts récupérés. Lancement génération audio/vidéo...")
        # Appel à la logique de génération audio/vidéo (à intégrer selon ta structure)
        # Exemple :
        # videos = self.audio_maker.create_videos_from_posts(posts, self.output_dir)
        # return videos
        return posts  # Pour test initial : renvoyer les posts pour vérification
