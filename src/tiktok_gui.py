#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TikTok Video GUI
--------------
Interface graphique pour créer des vidéos au format TikTok à partir d'images sélectionnées.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import random
import time
from datetime import datetime
import shutil
import threading

# Importer la classe TikTokVideoMaker depuis le module utils.modern_video
from .utils.modern_video import TikTokVideoMaker

# Vérifier si moviepy est installé
try:
    from moviepy.editor import *
except ImportError:
    print("Le module moviepy n'est pas installé. Installation en cours...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
    from moviepy.editor import *

# Vérifier si Pillow est installé
try:
    from PIL import Image, ImageTk
except ImportError:
    print("Le module Pillow n'est pas installé. Installation en cours...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageTk

# Compatibilité avec les différentes versions de Pillow
# ANTIALIAS est déprécié dans les nouvelles versions de Pillow et remplacé par LANCZOS
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

# La classe TikTokVideoMaker est maintenant importée depuis utils.modern_video

class TikTokGUI(tk.Tk):
    """Interface graphique pour créer des vidéos TikTok."""
    
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.title("Créateur de Vidéos TikTok")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Variables
        self.selected_images = []
        self.background_path = None
        self.background_type = None
        self.background_audio_path = None
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Créer l'interface
        self._create_widgets()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Initialiser la prévisualisation avec un format TikTok vide
        self.initialize_preview()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """Crée les widgets de l'interface."""
        # Frame principale
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour les boutons en haut
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Bouton pour sélectionner les images
        select_images_btn = ttk.Button(button_frame, text="Sélectionner des images", command=self.select_images)
        select_images_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour sélectionner un arrière-plan
        select_bg_btn = ttk.Button(button_frame, text="Sélectionner un arrière-plan", command=self.select_background)
        select_bg_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour sélectionner un audio d'arrière-plan
        select_audio_btn = ttk.Button(button_frame, text="Sélectionner un audio", command=self.select_background_audio)
        select_audio_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour générer la vidéo
        generate_btn = ttk.Button(button_frame, text="Générer la vidéo", command=self.generate_video)
        generate_btn.pack(side=tk.RIGHT, padx=5)
        
        # Frame pour la liste des images
        list_frame = ttk.LabelFrame(main_frame, text="Images sélectionnées")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox pour afficher les images sélectionnées avec sélection multiple
        self.image_listbox = tk.Listbox(list_frame, height=10, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set)
        self.image_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.image_listbox.yview)
        
        # Bind double-click pour prévisualiser l'image
        self.image_listbox.bind('<Double-1>', self.preview_image)
        
        # Bind pour le glisser-déposer
        self.image_listbox.bind('<ButtonPress-1>', self.on_drag_start)
        self.image_listbox.bind('<B1-Motion>', self.on_drag_motion)
        self.image_listbox.bind('<ButtonRelease-1>', self.on_drag_release)
        
        # Frame pour les boutons de manipulation de la liste
        list_button_frame = ttk.Frame(main_frame)
        list_button_frame.pack(fill=tk.X, pady=5)
        
        # Bouton pour supprimer les images sélectionnées
        delete_btn = ttk.Button(list_button_frame, text="Supprimer la sélection", command=self.delete_image)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour monter les images sélectionnées dans la liste
        up_btn = ttk.Button(list_button_frame, text="Monter la sélection", command=self.move_image_up)
        up_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour descendre les images sélectionnées dans la liste
        down_btn = ttk.Button(list_button_frame, text="Descendre la sélection", command=self.move_image_down)
        down_btn.pack(side=tk.LEFT, padx=5)
        
        # Label d'aide pour le glisser-déposer
        help_text = "Astuce: Utilisez Ctrl+clic pour sélectionner plusieurs images. \nVous pouvez aussi glisser-déposer les images pour les réorganiser."
        help_label = ttk.Label(list_button_frame, text=help_text, foreground="#555555")
        help_label.pack(side=tk.RIGHT, padx=5)
        
        # Frame pour la prévisualisation
        preview_frame = ttk.LabelFrame(main_frame, text="Prévisualisation")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Label pour afficher l'image prévisualisée
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame pour les options
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=10)
        
        # Option pour la durée de la vidéo
        ttk.Label(options_frame, text="Durée totale (secondes):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.duration_var = tk.StringVar(value="61")
        duration_entry = ttk.Entry(options_frame, textvariable=self.duration_var, width=10)
        duration_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Option pour le facteur de zoom
        ttk.Label(options_frame, text="Facteur de zoom (0.1-1.0):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.zoom_factor_var = tk.StringVar(value="0.8")
        zoom_entry = ttk.Entry(options_frame, textvariable=self.zoom_factor_var, width=10)
        zoom_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Option pour le répertoire de sortie
        ttk.Label(options_frame, text="Répertoire de sortie:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.output_dir_var = tk.StringVar(value=self.output_dir)
        output_dir_entry = ttk.Entry(options_frame, textvariable=self.output_dir_var, width=40)
        output_dir_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
        output_dir_btn = ttk.Button(options_frame, text="Parcourir", command=self.select_output_dir)
        output_dir_btn.grid(row=1, column=3, padx=5, pady=5)
        
        # Affichage des fichiers d'arrière-plan sélectionnés
        ttk.Label(options_frame, text="Arrière-plan:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.background_var = tk.StringVar(value="Aucun")
        ttk.Label(options_frame, textvariable=self.background_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
        
        ttk.Label(options_frame, text="Audio d'arrière-plan:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.background_audio_var = tk.StringVar(value="Aucun")
        ttk.Label(options_frame, textvariable=self.background_audio_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
        
        # Barre de statut
        self.status_var = tk.StringVar(value="Prêt")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def select_images(self):
        """Ouvre une boîte de dialogue pour sélectionner des images."""
        filetypes = [
            ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("Tous les fichiers", "*.*")
        ]
        filenames = filedialog.askopenfilenames(title="Sélectionner des images", filetypes=filetypes)
        
        if filenames:
            # Ajouter les nouvelles images à la liste
            for filename in filenames:
                if filename not in self.selected_images:
                    self.selected_images.append(filename)
                    self.image_listbox.insert(tk.END, os.path.basename(filename))
            
            self.status_var.set(f"{len(filenames)} image(s) ajoutée(s)")
            
            # Mettre à jour la prévisualisation avec la première image et l'arrière-plan
            if self.selected_images:
                self.preview_image(None, self.selected_images[0])
    
    def select_background(self):
        """Ouvre une boîte de dialogue pour sélectionner une image ou vidéo d'arrière-plan."""
        filetypes = [
            ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("Vidéos", "*.mp4 *.avi *.mov *.mkv"),
            ("Tous les fichiers", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Sélectionner un arrière-plan", filetypes=filetypes)
        
        if filename:
            self.background_path = filename
            # Déterminer le type d'arrière-plan en fonction de l'extension
            ext = os.path.splitext(filename)[1].lower()
            if ext in [".mp4", ".avi", ".mov", ".mkv"]:
                self.background_type = "video"
                self.status_var.set(f"Arrière-plan vidéo sélectionné: {os.path.basename(filename)}")
                self.background_var.set(f"{os.path.basename(filename)} (vidéo)")
            else:
                self.background_type = "image"
                self.status_var.set(f"Arrière-plan image sélectionné: {os.path.basename(filename)}")
                self.background_var.set(f"{os.path.basename(filename)} (image)")
            
            # Mettre à jour la prévisualisation avec l'arrière-plan et la première image si disponible
            if self.selected_images:
                self.preview_image(None, self.selected_images[0])
            else:
                # Prévisualiser uniquement l'arrière-plan si c'est une image
                if self.background_type == "image":
                    self.preview_image(None, filename)
    
    def select_background_audio(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier audio d'arrière-plan."""
        filetypes = [
            ("Fichiers audio", "*.mp3 *.wav *.ogg *.aac"),
            ("Tous les fichiers", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Sélectionner un audio d'arrière-plan", filetypes=filetypes)
        
        if filename:
            self.background_audio_path = filename
            self.status_var.set(f"Audio d'arrière-plan sélectionné: {os.path.basename(filename)}")
            self.background_audio_var.set(os.path.basename(filename))

    
    def select_output_dir(self):
        """Ouvre une boîte de dialogue pour sélectionner le répertoire de sortie."""
        directory = filedialog.askdirectory(title="Sélectionner le répertoire de sortie")
        
        if directory:
            self.output_dir = directory
            self.output_dir_var.set(directory)
    
    def initialize_preview(self):
        """Initialise la prévisualisation avec un format TikTok vide ou avec l'arrière-plan si disponible."""
        try:
            # Dimensions de prévisualisation (format TikTok en miniature)
            preview_width = 200
            preview_height = 356  # Ratio 9:16 comme TikTok
            
            # Créer une image de fond (noire ou avec l'arrière-plan)
            if self.background_path and self.background_type == "image" and os.path.exists(self.background_path):
                # Utiliser l'image d'arrière-plan
                bg_img = Image.open(self.background_path)
                # Redimensionner l'arrière-plan pour correspondre aux dimensions de prévisualisation
                bg_img = bg_img.resize((preview_width, preview_height), Image.LANCZOS)
                preview_img = bg_img.copy()
            else:
                # Créer un fond noir
                preview_img = Image.new('RGB', (preview_width, preview_height), (25, 25, 25))
            
            # Ajouter un texte explicatif sur l'image
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(preview_img)
            
            # Essayer de charger une police, sinon utiliser la police par défaut
            try:
                # Utiliser une police système si disponible
                font = ImageFont.truetype("arial.ttf", 14)
            except IOError:
                font = ImageFont.load_default()
            
            # Ajouter un texte explicatif
            text = "Format TikTok"
            text_width = draw.textlength(text, font=font)
            x = (preview_width - text_width) // 2
            draw.text((x, 20), text, fill="white", font=font)
            
            text2 = "9:16"
            text2_width = draw.textlength(text2, font=font)
            x2 = (preview_width - text2_width) // 2
            draw.text((x2, 40), text2, fill="white", font=font)
            
            # Convertir l'image pour tkinter
            tk_img = ImageTk.PhotoImage(preview_img)
            
            # Afficher l'image
            self.preview_label.configure(image=tk_img)
            self.preview_label.image = tk_img  # Garder une référence
            
            # Mettre à jour le statut
            self.status_var.set("Prêt à créer une vidéo TikTok")
                
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la prévisualisation: {e}")
    
    def preview_image(self, event, image_path=None):
        """Prévisualise l'image sélectionnée avec l'arrière-plan si disponible."""
        if image_path is None:
            # Obtenir les images sélectionnées dans la listbox
            selection = self.image_listbox.curselection()
            if not selection:
                # Si aucune image n'est sélectionnée mais qu'il y a des images dans la liste,
                # utiliser la première image
                if self.selected_images:
                    image_path = self.selected_images[0]
                else:
                    return
            else:
                # Si plusieurs images sont sélectionnées, utiliser la première sélectionnée
                # et afficher un message indiquant le nombre d'images sélectionnées
                if len(selection) > 1:
                    self.status_var.set(f"{len(selection)} images sélectionnées")
                index = selection[0]
                image_path = self.selected_images[index]
        
        try:
            # Dimensions de prévisualisation (format TikTok en miniature)
            preview_width = 200
            preview_height = 356  # Ratio 9:16 comme TikTok
            
            # Créer une image de fond (noire ou avec l'arrière-plan)
            if self.background_path and self.background_type == "image" and os.path.exists(self.background_path):
                # Utiliser l'image d'arrière-plan
                bg_img = Image.open(self.background_path)
                # Redimensionner l'arrière-plan pour correspondre aux dimensions de prévisualisation
                bg_img = bg_img.resize((preview_width, preview_height), Image.LANCZOS)
                preview_img = bg_img.copy()
            else:
                # Créer un fond noir
                preview_img = Image.new('RGB', (preview_width, preview_height), (25, 25, 25))
            
            # Ouvrir l'image à superposer
            img = Image.open(image_path)
            
            # Calculer les dimensions pour que l'image tienne dans la prévisualisation
            # tout en conservant son ratio
            img_width, img_height = img.size
            ratio = min(preview_width / img_width, preview_height / img_height) * 0.9  # 90% pour laisser une marge
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # Redimensionner l'image
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Calculer la position pour centrer l'image sur le fond
            x = (preview_width - new_width) // 2
            y = (preview_height - new_height) // 2
            
            # Coller l'image sur le fond
            preview_img.paste(img, (x, y))
            
            # Convertir l'image pour tkinter
            tk_img = ImageTk.PhotoImage(preview_img)
            
            # Afficher l'image
            self.preview_label.configure(image=tk_img)
            self.preview_label.image = tk_img  # Garder une référence
            
            # Mettre à jour le statut
            if image_path == self.background_path:
                self.status_var.set(f"Prévisualisation de l'arrière-plan: {os.path.basename(image_path)}")
            else:
                self.status_var.set(f"Prévisualisation de: {os.path.basename(image_path)}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de prévisualiser l'image: {e}")
    
    def delete_image(self):
        """Supprime les images sélectionnées de la liste."""
        selection = self.image_listbox.curselection()
        if not selection:
            return
        
        # Convertir en liste et trier en ordre décroissant pour éviter les problèmes d'index
        indices = sorted(list(selection), reverse=True)
        
        # Supprimer chaque image sélectionnée
        for index in indices:
            self.image_listbox.delete(index)
            del self.selected_images[index]
        
        count = len(indices)
        self.status_var.set(f"{count} image(s) supprimée(s)")
    
    def on_drag_start(self, event):
        """Commence l'opération de glisser-déposer."""
        # Identifier l'index de l'élément sous le curseur
        widget = event.widget
        index = widget.nearest(event.y)
        
        # Vérifier si l'élément est déjà sélectionné
        if index not in widget.curselection():
            # Si l'utilisateur n'a pas maintenu Ctrl ou Shift, désélectionner tout
            if not (event.state & 4) and not (event.state & 1):
                widget.selection_clear(0, tk.END)
            widget.selection_set(index)
        
        # Stocker l'index et la position y de départ
        self._drag_start_index = index
        self._drag_start_y = event.y
    
    def on_drag_motion(self, event):
        """Gère le mouvement pendant le glisser-déposer."""
        pass  # Nous pourrions ajouter un retour visuel ici si nécessaire
    
    def on_drag_release(self, event):
        """Termine l'opération de glisser-déposer."""
        if not hasattr(self, '_drag_start_index'):
            return
        
        widget = event.widget
        end_index = widget.nearest(event.y)
        
        # Si l'index de fin est différent de l'index de départ, déplacer l'élément
        if end_index != self._drag_start_index:
            # Obtenir tous les éléments sélectionnés
            selection = widget.curselection()
            
            # Si un seul élément est sélectionné, le déplacer
            if len(selection) == 1:
                self._move_items(selection, end_index)
            # Si plusieurs éléments sont sélectionnés, les déplacer ensemble
            elif len(selection) > 1 and self._drag_start_index in selection:
                self._move_items(selection, end_index)
        
        # Nettoyer les variables temporaires
        del self._drag_start_index
        del self._drag_start_y
    
    def _move_items(self, selection, end_index):
        """Déplace les éléments sélectionnés vers la position cible."""
        # Convertir en liste et trier
        indices = sorted(list(selection))
        
        # Déterminer si on déplace vers le haut ou vers le bas
        moving_up = end_index < indices[0]
        
        # Calculer la position cible pour chaque élément
        if moving_up:
            target_indices = list(range(end_index, end_index + len(indices)))
        else:
            # Ajuster l'index de fin pour tenir compte des suppressions
            adjusted_end = end_index - (len(indices) - 1) if end_index > indices[-1] else end_index
            target_indices = list(range(adjusted_end, adjusted_end + len(indices)))
        
        # Créer des copies temporaires des éléments à déplacer
        temp_items = [self.selected_images[i] for i in indices]
        temp_texts = [self.image_listbox.get(i) for i in indices]
        
        # Supprimer les éléments originaux (en ordre décroissant pour éviter les problèmes d'index)
        for i in sorted(indices, reverse=True):
            self.image_listbox.delete(i)
            del self.selected_images[i]
        
        # Insérer les éléments à leurs nouvelles positions
        for i, (item, text) in enumerate(zip(temp_items, temp_texts)):
            target_idx = target_indices[i]
            self.image_listbox.insert(target_idx, text)
            self.selected_images.insert(target_idx, item)
            self.image_listbox.selection_set(target_idx)
        
        self.status_var.set("Images réorganisées")
    
    def move_image_up(self):
        """Déplace les images sélectionnées vers le haut dans la liste."""
        selection = self.image_listbox.curselection()
        if not selection:
            return
            
        # Vérifier si la première image sélectionnée est déjà tout en haut
        if min(selection) == 0:
            return
            
        # Utiliser la méthode _move_items pour déplacer les éléments sélectionnés
        self._move_items(selection, min(selection) - 1)
    
    def move_image_down(self):
        """Déplace les images sélectionnées vers le bas dans la liste."""
        selection = self.image_listbox.curselection()
        if not selection:
            return
            
        # Vérifier si la dernière image sélectionnée est déjà tout en bas
        if max(selection) == len(self.selected_images) - 1:
            return
            
        # Utiliser la méthode _move_items pour déplacer les éléments sélectionnés
        self._move_items(selection, max(selection) + 2)
    
    def generate_video(self):
        """Génère la vidéo à partir des images sélectionnées."""
        if not self.selected_images:
            messagebox.showerror("Erreur", "Aucune image sélectionnée.")
            return
        
        try:
            # Obtenir la durée totale
            total_duration = int(self.duration_var.get())
            if total_duration <= 0:
                messagebox.showerror("Erreur", "La durée doit être supérieure à 0.")
                return
        except ValueError:
            messagebox.showerror("Erreur", "La durée doit être un nombre entier.")
            return
        
        # Créer un thread pour générer la vidéo
        threading.Thread(target=self._generate_video_thread, args=(total_duration,)).start()
    
    def _generate_video_thread(self, total_duration):
        """Thread pour générer la vidéo sans bloquer l'interface."""
        self.status_var.set("Génération de la vidéo en cours...")
        
        # Créer un nom de fichier unique pour la vidéo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"tiktok_video_{timestamp}.mp4"
        video_path = os.path.join(self.output_dir, video_filename)
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialiser le créateur de vidéos avec les dimensions TikTok
        video_maker = TikTokVideoMaker(
            output_path=video_path,
            output_size=(1080, 1920),  # Format TikTok vertical
            fps=30
        )
        
        # Note: Le facteur de zoom est maintenant géré automatiquement dans la classe TikTokVideoMaker
        # pour optimiser l'affichage des images dans le format vertical de TikTok
        
        # Configurer l'arrière-plan si sélectionné
        if self.background_path and os.path.exists(self.background_path):
            video_maker.set_background(self.background_path, self.background_type)
        
        # Configurer l'audio d'arrière-plan si sélectionné
        audio_duration = total_duration  # Valeur par défaut si pas d'audio
        if self.background_audio_path and os.path.exists(self.background_audio_path):
            video_maker.set_background_audio(self.background_audio_path)
            
            # Obtenir la durée de l'audio pour synchroniser les images
            try:
                audio_clip = AudioFileClip(self.background_audio_path)
                audio_duration = audio_clip.duration
                audio_clip.close()
                self.status_var.set(f"Durée de l'audio détectée: {audio_duration:.2f} secondes")
            except Exception as e:
                self.status_var.set(f"Impossible de déterminer la durée de l'audio: {str(e)}")
                # Continuer avec la durée définie par l'utilisateur
        
        # Calculer la durée de chaque image en fonction du nombre d'images et de la durée de l'audio
        image_count = len(self.selected_images)
        duration_per_image = audio_duration / image_count
        
        # Ajouter chaque image à la vidéo avec une durée égale
        for img_path in self.selected_images:
            # Ajouter l'image à la vidéo avec la durée calculée
            video_maker.add_image(img_path, duration_per_image)
        
        # Rendre la vidéo
        if video_maker.render():
            self.status_var.set(f"Vidéo générée avec succès: {video_filename}")
            
            # Demander à l'utilisateur s'il veut ouvrir le dossier de sortie
            if messagebox.askyesno("Succès", f"La vidéo a été générée avec succès.\n\nVoulez-vous ouvrir le dossier de sortie?"):
                os.startfile(self.output_dir)
        else:
            self.status_var.set("Erreur lors de la génération de la vidéo.")
            messagebox.showerror("Erreur", "Une erreur s'est produite lors de la génération de la vidéo.")

def main():
    app = TikTokGUI()
    app.mainloop()

if __name__ == "__main__":
    main()