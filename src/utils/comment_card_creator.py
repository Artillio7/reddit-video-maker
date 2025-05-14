import os

class CommentCardCreator:
    def __init__(self, output_directory):
        self.output_directory = output_directory
        os.makedirs(self.output_directory, exist_ok=True)

    def create_card(self, comment_data):
        """
        Crée une "carte" texte à partir des données du commentaire.
        Args:
            comment_data (dict): Doit contenir au minimum les clés 'author', 'body', 'id'.
        Returns:
            str: Chemin du fichier généré
        """
        caption = f"Commentaire de {comment_data.get('author', 'unknown')}: {comment_data.get('body', '')}"
        output_path = os.path.join(self.output_directory, f"comment_{comment_data.get('id', 'unknown')}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(caption)
        return output_path
