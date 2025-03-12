import os
import asyncio
import random
from pathlib import Path
import logging
from edge_tts import Communicate
from typing import Optional, List, Dict

class EnhancedTTSVoice:
    # Voix optimisées pour TikTok en anglais
    TIKTOK_VOICES = {
        'en_US_AriaNeural': {
            'voice': 'en-US-AriaNeural',
            'style': 'cheerful',
            'pitch': '+2Hz',
            'rate': '+15%'
        },
        'en_US_JennyNeural': {
            'voice': 'en-US-JennyNeural',
            'style': 'friendly',
            'pitch': '+1Hz',
            'rate': '+10%'
        },
        'en_US_GuyNeural': {
            'voice': 'en-US-GuyNeural',
            'style': 'enthusiastic',
            'pitch': '-1Hz',
            'rate': '+12%'
        }
    }

    def __init__(self, temp_dir: str = 'temp', voice_preset: str = 'en_US_AriaNeural'):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.voice_preset = self.TIKTOK_VOICES.get(voice_preset, self.TIKTOK_VOICES['en_US_AriaNeural'])
        self.logger = logging.getLogger(__name__)

    def _create_dynamic_ssml(self, text: str) -> str:
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        ssml_parts = []
        for i, sentence in enumerate(sentences):
            style = random.choice(['cheerful', 'friendly', 'enthusiastic']) if i % 2 == 0 else ''
            
            pitch_variation = random.uniform(-0.5, 0.5)
            rate_variation = random.uniform(-5, 5)
            
            pitch = f"{pitch_variation:+.1f}Hz"
            rate = f"{rate_variation:+.1f}%"
            
            if style:
                ssml_parts.append(
                    f'<prosody pitch="{pitch}" rate="{rate}">'
                    f'<mstts:express-as style="{style}">{sentence}.</mstts:express-as>'
                    f'</prosody>'
                )
            else:
                ssml_parts.append(
                    f'<prosody pitch="{pitch}" rate="{rate}">{sentence}.</prosody>'
                )

        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
               xmlns:mstts="http://www.w3.org/2001/mstts">
            {' '.join(ssml_parts)}
        </speak>
        """
        return ssml

    async def generate_tts_async(self, text: str, output_path: Optional[str] = None) -> str:
        if not text.strip():
            self.logger.warning("Texte vide, impossible de générer TTS")
            return None

        if output_path is None:
            output_path = self.temp_dir / f"tts_{hash(text)}.mp3"
        
        try:
            ssml = self._create_dynamic_ssml(text)
            communicate = Communicate(ssml, self.voice_preset['voice'])
            await communicate.save(str(output_path))
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération TTS: {str(e)}")
            return None

    def generate_tts(self, text: str, output_path: Optional[str] = None) -> str:
        return asyncio.run(self.generate_tts_async(text, output_path))

class EnhancedAudioMaker:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tts_generator = EnhancedTTSVoice()
        self.logger = logging.getLogger(__name__)

    def create_tiktok_audio(
        self,
        texts: List[str],
        output_file: str,
    ) -> bool:
        try:
            audio_paths = []
            for text in texts:
                audio_path = self.tts_generator.generate_tts(text)
                if audio_path:
                    audio_paths.append(audio_path)

            if audio_paths:
                # Utiliser le premier fichier audio comme base
                import shutil
                shutil.copy2(audio_paths[0], output_file)
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la création audio: {str(e)}")
            return False
