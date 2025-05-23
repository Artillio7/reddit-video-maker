import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import logging
from config import GUI_CONFIG

logger = logging.getLogger(__name__)

class VideoProgressGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry(f"{GUI_CONFIG['window_width']}x{GUI_CONFIG['window_height']}")
        
        # Variables de contrôle
        self.processing = False
        self.current_preview = None
        
        # Frame principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Frame de progression
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Progression")
        self.progress_frame.pack(fill='x', padx=5, pady=5)
        
        # Barre de progression
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', padx=5, pady=5)
        
        # Label de statut
        self.status_var = tk.StringVar(value="Prêt")
        self.status_label = ttk.Label(
            self.progress_frame,
            textvariable=self.status_var
        )
        self.status_label.pack(padx=5, pady=5)
        
        # Frame de prévisualisation
        self.preview_frame = ttk.LabelFrame(self.main_frame, text="Prévisualisation")
        self.preview_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Zone de prévisualisation
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Boutons de contrôle
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_button = ttk.Button(
            self.control_frame,
            text="Démarrer",
            command=self.start_processing
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(
            self.control_frame,
            text="Arrêter",
            command=self.stop_processing,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
    
    def update_progress(self, progress, status):
        """Met à jour la barre de progression et le statut"""
        self.progress_var.set(progress * 100)
        self.status_var.set(status)
        self.root.update_idletasks()
    
    def update_preview(self, image):
        """Met à jour l'aperçu avec une nouvelle image"""
        if image is not None:
            # Redimensionner l'image pour l'aperçu
            preview_width = GUI_CONFIG['preview_width']
            preview_height = GUI_CONFIG['preview_height']
            
            # Calculer les dimensions pour conserver le ratio
            ratio = min(preview_width / image.width, preview_height / image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            # Redimensionner l'image
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convertir en PhotoImage
            photo = ImageTk.PhotoImage(resized_image)
            
            # Mettre à jour le label
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo  # Garder une référence
            self.current_preview = photo
    
    def start_processing(self):
        """Démarre le traitement des vidéos"""
        if not self.processing:
            self.processing = True
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            self.process_videos()
    
    def stop_processing(self):
        """Arrête le traitement des vidéos"""
        if self.processing:
            self.processing = False
            self.reset_interface()
    
    def reset_interface(self):
        """Réinitialise l'interface"""
        self.processing = False
        self.progress_var.set(0)
        self.status_var.set("Prêt")
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        if self.current_preview:
            self.preview_label.configure(image='')
            self.current_preview = None
    
    def process_videos(self):
        """Méthode à surcharger dans les classes enfants"""
        raise NotImplementedError("Cette méthode doit être implémentée dans une classe enfant")