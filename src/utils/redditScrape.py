import praw
from praw.exceptions import PRAWException
from prawcore.exceptions import PrawcoreException, ResponseException
import sys
import os
import importlib.util
import logging
import random
from .media_extractor import MediaExtractor

# Approche plus robuste pour les imports
MODULE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if MODULE_PATH not in sys.path:
    sys.path.insert(0, MODULE_PATH)

# Import du module config
try:
    from config import REDDIT_CONFIG, CONTENT_LIMITS
except ImportError:
    # Fallback pour l'import si le chemin direct ne fonctionne pas
    config_path = os.path.join(MODULE_PATH, 'config.py')
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    REDDIT_CONFIG = config.REDDIT_CONFIG
    CONTENT_LIMITS = config.CONTENT_LIMITS
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedditScraper:
    def __init__(self):
        """Initialize Reddit API connection"""
        self.reddit = None
        self.media_extractor = MediaExtractor()  # Initialize MediaExtractor
        
        # Vérifier si les identifiants sont définis
        if not REDDIT_CONFIG.get("client_id") or not REDDIT_CONFIG.get("client_secret"):
            logger.error("Identifiants Reddit manquants. Veuillez configurer le fichier .env")
            logger.error("Suivez les instructions dans le fichier .env pour obtenir vos identifiants")
            return
            
        try:
            self.reddit = praw.Reddit(**REDDIT_CONFIG)
            # Tester la connexion
            username = self.reddit.user.me()
            if username:
                logger.info(f"Successfully connected to Reddit API as {username}")
            else:
                logger.info("Successfully connected to Reddit API (read-only mode)")
        except ResponseException as e:
            if e.response.status_code == 401:
                logger.error("Erreur d'authentification (401): Identifiants Reddit invalides")
                logger.error("Veuillez vérifier vos identifiants dans le fichier .env")
            else:
                logger.error(f"Erreur API Reddit: {e}")
        except Exception as e:
            logger.error(f"Failed to connect to Reddit API: {e}")

    def select_random_subreddit(self):
        """
        Sélectionne aléatoirement un subreddit populaire pour générer du contenu.
        
        Returns:
            str: Nom du subreddit sélectionné
        """
        # Liste de subreddits populaires qui ont généralement du contenu intéressant
        popular_subreddits = [
            "AskReddit", "todayilearned", "explainlikeimfive", "LifeProTips",
            "Showerthoughts", "mildlyinteresting", "interestingasfuck", "tifu",
            "TrueOffMyChest", "UnpopularOpinion", "AmItheAsshole", "confessions",
            "talesfromtechsupport", "MaliciousCompliance", "pettyrevenge", "ProRevenge",
            "IDontWorkHereLady", "TalesFromRetail", "ChoosingBeggars", "entitledparents",
            "relationship_advice", "TwoXChromosomes", "NoStupidQuestions", "whatisthisthing",
            "AskMen", "AskWomen", "askscience", "IAmA", "TrueAskReddit", "offmychest"
        ]
        
        # Sélectionner un subreddit aléatoire
        selected_subreddit = random.choice(popular_subreddits)
        logger.info(f"Subreddit aléatoire sélectionné: r/{selected_subreddit}")
        
        return selected_subreddit

    def get_reddit_posts(self, subreddit, timeframe="day", post_count=10, allow_nsfw=False, sorting=None, comment_sort=None):
        """
        Récupère des posts Reddit avec des options avancées.
        
        Args:
            subreddit (str): Nom du subreddit à scraper
            timeframe (str): Période (day, week, month, year, all)
            post_count (int): Nombre de posts à récupérer
            allow_nsfw (bool): Si True, inclut les posts NSFW
            sorting (str): Méthode de tri ("hot", "new", "top", "rising", "controversial", None pour aléatoire)
            comment_sort (str): Méthode de tri des commentaires ("most_comments", "most_upvotes", None pour défaut)
            
        Returns:
            list: Liste des posts Reddit
        """
        # Vérifier si l'API Reddit est disponible
        if self.reddit is None:
            logger.error("API Reddit non disponible. Impossible de récupérer les posts.")
            logger.error("Veuillez configurer vos identifiants Reddit dans le fichier .env")
            return []
            
        try:
            # Validation des paramètres
            if not isinstance(subreddit, str) or not subreddit:
                logger.error("Le nom du subreddit doit être une chaîne non vide")
                return []
                
            if not isinstance(post_count, int) or post_count < 1:
                logger.error("Le nombre de posts doit être un entier positif")
                post_count = 10
            
            # Convertir les timeframes en valeurs acceptées par PRAW
            valid_timeframes = {"hour": "hour", "day": "day", "week": "week", 
                               "month": "month", "year": "year", "all": "all"}
            if timeframe not in valid_timeframes:
                logger.warning(f"Timeframe invalide: {timeframe}, utilisation de 'day'")
                timeframe = "day"
                
            # Déterminer la méthode de tri
            valid_sorting = ["hot", "new", "top", "rising", "controversial"]
            if sorting is None or sorting not in valid_sorting:
                sorting = random.choice(valid_sorting)
                logger.info(f"Méthode de tri aléatoire sélectionnée: {sorting}")
            
            # Récupérer le subreddit
            logger.info(f"Récupération des posts de r/{subreddit} avec tri {sorting}...")
            sub = self.reddit.subreddit(subreddit)
            
            # Récupérer les posts selon la méthode de tri
            fetch_limit = min(post_count * 3, 100)  # Récupérer plus de posts pour filtrer
            
            if sorting == "hot":
                submissions = sub.hot(limit=fetch_limit)
            elif sorting == "new":
                submissions = sub.new(limit=fetch_limit)
            elif sorting == "top":
                submissions = sub.top(time_filter=timeframe, limit=fetch_limit)
            elif sorting == "rising":
                submissions = sub.rising(limit=fetch_limit)
            elif sorting == "controversial":
                submissions = sub.controversial(time_filter=timeframe, limit=fetch_limit)
            
            # Filtrer les posts
            filtered_posts = []
            all_posts = []
            for post in submissions:
                # Vérifier si le post est valide
                if post.over_18 and not allow_nsfw:  # Ignorer les posts NSFW si non autorisés
                    continue
                
                # Accepter tous les types de posts, pas seulement les self posts
                # Mais s'assurer qu'il y a du contenu à afficher
                if not post.title:
                    continue
                    
                # Vérifier si le post a suffisamment de commentaires
                post.comment_sort = 'best'
                post.comments.replace_more(limit=0)  # Ne pas charger les commentaires supplémentaires
                
                # Compter le nombre de commentaires pour le tri potentiel
                comment_count = len(post.comments)
                
                valid_comments = []
                for i, comment in enumerate(post.comments):
                    if hasattr(comment, 'body') and len(comment.body) >= CONTENT_LIMITS.get('min_comment_length', 50):
                        valid_comments.append(comment)
                        if len(valid_comments) >= CONTENT_LIMITS.get('max_comments', 5):
                            break
                
                if len(valid_comments) >= 3:  # Au moins 3 commentaires valides
                    post_data = {
                        'post': post,
                        'title': post.title,
                        'author': post.author.name if post.author else "[deleted]",
                        'score': post.score,
                        'url': f"https://www.reddit.com{post.permalink}",
                        'created_utc': post.created_utc,
                        'id': post.id,
                        'comment_count': comment_count,
                        'comments': [{
                            'body': comment.body,
                            'author': comment.author.name if comment.author else "[deleted]",
                            'score': comment.score,
                            'media': self.media_extractor.process_comment(
                                comment.body, 
                                comment.id if hasattr(comment, 'id') else f"comment_{i}_{j}",
                                post.id
                            )
                        } for j, comment in enumerate(valid_comments)]
                    }
                    all_posts.append(post_data)
                    
            # Appliquer le tri par nombre de commentaires si spécifié
            if comment_sort == "most_comments":
                logger.info("Tri des posts par nombre de commentaires")
                all_posts.sort(key=lambda x: x.get('comment_count', 0), reverse=True)
            
            # Prendre les N premiers posts après le tri
            filtered_posts = all_posts[:post_count]
            
            # Trier les commentaires par score, du plus haut au plus bas pour chaque post
            for post in filtered_posts:
                post['comments'].sort(key=lambda x: x.get('score', 0), reverse=True)
            
            logger.info(f"{len(filtered_posts)} posts récupérés de r/{subreddit}")
            
            # Log pour déboguer la structure du premier post si disponible
            if filtered_posts and len(filtered_posts) > 0:
                logger.info(f"Structure du premier post: {list(filtered_posts[0].keys())}")
                
            return filtered_posts
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des posts: {e}")
            return []

    def get_posts(self, sub, span="day", count=1):
        """Get posts from a subreddit with error handling
        
        Args:
            sub (str): Subreddit name
            span (str): Time span (day, week, month, year, all)
            count (int): Number of posts to fetch
        """
        try:
            subreddit = self.reddit.subreddit(sub)
            posts = []
            
            # S'assurer que count est un entier
            count = int(count) if isinstance(count, str) else count
            
            # Fetch posts more efficiently based on count
            fetch_limit = min(count * 10, 100)  # Increased multiplier to get more variety
            
            # Choose a random sorting method to increase variety
            sort_methods = ["top", "hot", "rising", "controversial"]
            sort_method = random.choice(sort_methods)
            
            logger.info(f"Using sorting method: {sort_method} with span: {span}")
            
            # Get posts using the selected sort method
            if sort_method == "top":
                submission_stream = subreddit.top(span, limit=fetch_limit)
            elif sort_method == "hot":
                submission_stream = subreddit.hot(limit=fetch_limit)
            elif sort_method == "rising":
                submission_stream = subreddit.rising(limit=fetch_limit)
            elif sort_method == "controversial":
                submission_stream = subreddit.controversial(span, limit=fetch_limit)
            
            # Track posts we've already processed using a simple file-based history
            history_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output", ".history")
            os.makedirs(history_dir, exist_ok=True)
            history_file = os.path.join(history_dir, f"{sub}_history.txt")
            
            # Load history
            processed_ids = set()
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        processed_ids = set(line.strip() for line in f)
                except Exception as e:
                    logger.warning(f"Could not read history file: {e}")
            
            # Find posts we haven't processed yet
            for submission in submission_stream:
                if submission.id not in processed_ids and self._is_valid_post(submission):
                    posts.append(submission)
                    
                    # Add to history
                    try:
                        with open(history_file, 'a', encoding='utf-8') as f:
                            f.write(f"{submission.id}\n")
                    except Exception as e:
                        logger.warning(f"Could not update history file: {e}")
                    
                    if len(posts) >= count:
                        break
            
            # If we can't find enough new posts, use the least recently used ones
            if len(posts) < count and len(processed_ids) > 0:
                logger.info(f"Not enough new posts found, reusing older posts")
                
                # If history is too long, trim it
                max_history = 1000
                if len(processed_ids) > max_history:
                    try:
                        # Get the oldest entries (first lines in the file)
                        with open(history_file, 'r', encoding='utf-8') as f:
                            all_ids = [line.strip() for line in f]
                        
                        # Keep only the most recent entries
                        with open(history_file, 'w', encoding='utf-8') as f:
                            for id in all_ids[-max_history:]:
                                f.write(f"{id}\n")
                        
                        # Update processed_ids
                        processed_ids = set(all_ids[-max_history:])
                    except Exception as e:
                        logger.warning(f"Could not trim history file: {e}")
                
                # Try to get more posts
                additional_needed = count - len(posts)
                for submission in subreddit.top(span, limit=fetch_limit * 2):
                    if self._is_valid_post(submission) and submission not in posts:
                        posts.append(submission)
                        if len(posts) >= count:
                            break
                
            if not posts:
                logger.warning(f"No valid posts found in r/{sub}")
                
            return posts
            
        except PRAWException as e:
            logger.error(f"PRAW error while getting posts: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while getting posts: {e}")
            raise

    def get_comments(self, submission):
        """Get comments from a submission with error handling"""
        try:
            submission.comment_sort = 'best'
            comments = []
            
            for comment in submission.comments:
                if self._is_valid_comment(comment):
                    comments.append(comment)
                    if len(comments) >= CONTENT_LIMITS['max_comments']:
                        break
                        
            return comments
            
        except PRAWException as e:
            logger.error(f"PRAW error while getting comments: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while getting comments: {e}")
            raise

    def scrape_content(self, subreddit, count=1, span="day", post_index=0):
        """Main method to scrape posts and comments
        
        Args:
            subreddit (str): Subreddit name to scrape
            count (int): Number of posts to fetch
            span (str): Time span for posts (day, week, month, year, all)
            post_index (int): Index of the post to use (default: 0, first post)
            
        Returns:
            list: List containing the post and its comments, or empty list if no posts found
        """
        try:
            # Validation des paramètres d'entrée
            if not isinstance(subreddit, str) or not subreddit:
                logger.error("Le nom du subreddit doit être une chaîne non vide")
                return []
                
            if not isinstance(count, int) or count < 1:
                logger.error("Le nombre de posts doit être un entier positif")
                count = 1
                
            valid_spans = ["hour", "day", "week", "month", "year", "all"]
            if span not in valid_spans:
                logger.error(f"La période doit être l'une des suivantes : {', '.join(valid_spans)}")
                span = "day"  # Valeur par défaut
                
            if not isinstance(post_index, int) or post_index < 0:
                logger.error("L'index du post doit être un entier positif ou nul")
                post_index = 0
            
            posts = self.get_posts(subreddit, span, count)
            if not posts:
                logger.warning(f"No valid posts found in r/{subreddit}")
                return []
            
            # Select post based on index, with fallback to first post
            post_index = min(post_index, len(posts) - 1)
                
            post = posts[post_index]
            logger.info(f"Selected post: {post.title}")
            
            comments = self.get_comments(post)
            
            if not comments:
                logger.warning(f"No valid comments found for post: {post.title}")
                
            # Always return a list containing the post and any comments found
            return [post] + (comments or [])
            
        except Exception as e:
            logger.error(f"Failed to scrape content: {e}")
            raise

    def _is_valid_post(self, submission):
        """Check if a post meets our criteria"""
        interesting_keywords = [
            "shocking", "unexpected", "incredible", "crazy", "amazing", 
            "unbelievable", "mind blowing", "surprising", "never", "ever",
            "today", "yesterday", "best", "worst", "most", "least", "problem",
            "solution", "advice", "help", "weird", "strange", "life", "hack",
            "secret", "revealed", "popular", "unpopular", "opinion", "fact",
            "story", "experience", "true", "real", "fake", "truth", "lie"
        ]
        
        has_interesting_keywords = any(keyword in submission.title.lower() for keyword in interesting_keywords)
        
        return (
            not submission.over_18 and  # No NSFW content
            "r/" not in submission.title and  # No meta references
            "reddit" not in submission.title.lower() and
            len(submission.title) <= CONTENT_LIMITS['max_title_length'] and
            (submission.score > 50 or has_interesting_keywords)  # Either popular or interesting
        )

    def _is_valid_comment(self, comment):
        """Check if a comment meets our criteria"""
        if isinstance(comment, praw.models.MoreComments):
            return False
            
        # Vérifier si le commentaire contient des URLs d'images ou de vidéos Reddit
        contains_media_url = False
        
        if hasattr(comment, 'body'):
            # Patterns pour les URLs d'images/vidéos courantes sur Reddit
            media_patterns = [
                "i.redd.it", "preview.redd.it", "v.redd.it",
                "i.imgur.com", "imgur.com/a/", "imgur.com/gallery/",
                ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".webm"
            ]
            
            # Accepter les commentaires avec des URLs d'images/vidéos
            if any(pattern in comment.body.lower() for pattern in media_patterns):
                contains_media_url = True
            
        return (
            hasattr(comment, 'body') and
            CONTENT_LIMITS['min_comment_length'] <= len(comment.body) <= CONTENT_LIMITS['max_comment_length'] and
            (contains_media_url or "http" not in comment.body) and  # Accepter uniquement les URLs de médias
            not comment.stickied  # No pinned comments
        )

    @staticmethod
    def get_author_name(author_obj):
        """Safely extract author name from author object
        
        Args:
            author_obj: PRAW author object, which may be None
            
        Returns:
            str: Author name or "[deleted]" if author is None or deleted
        """
        if author_obj is None:
            return "[deleted]"
            
        try:
            return author_obj.name
        except (AttributeError, PRAWException):
            return "[deleted]"

# For backwards compatibility
def scrapeComments(subreddit, count=1, span="day", post_index=0):
    """Legacy function for compatibility
    
    Args:
        subreddit (str): Subreddit name to scrape
        count (int): Number of posts to fetch
        span (str): Time span for posts (day, week, month, year, all)
        post_index (int): Index of the post to use (default: 0, first post)
        
    Returns:
        list: List containing the post and its comments, or empty list if no posts found
    """
    scraper = RedditScraper()
    return scraper.scrape_content(subreddit, count, span, post_index)

if __name__ == "__main__":
    scraper = RedditScraper()
    content = scraper.scrape_content("askreddit", 1, "day")
    if content:
        post = content[0]
        author_name = RedditScraper.get_author_name(post.author)
        print(f"Found post: {post.title}")
        print(f"Author: {author_name}")
        print(f"Number of comments: {len(content) - 1}")
        
        # Print first few comments if available
        for i, comment in enumerate(content[1:3], 1):
            comment_author = RedditScraper.get_author_name(comment.author)
            print(f"\nComment {i} by {comment_author}:")
            print(f"{comment.body[:100]}...")  # Show first 100 chars
