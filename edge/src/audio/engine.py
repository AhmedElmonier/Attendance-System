import pygame
import os
import logging

class AudioEngine:
    def __init__(self, asset_dir="assets/audio"):
        self.asset_dir = asset_dir
        self.locale = "en"
        try:
            pygame.mixer.init()
            self.initialized = True
        except Exception as e:
            logging.error(f"Failed to init audio engine: {e}")
            self.initialized = False

    def set_locale(self, locale: str):
        if locale in ["en", "ar"]:
            self.locale = locale

    def play_prompt(self, prompt_name: str):
        if not self.initialized:
            return
        
        file_path = os.path.join(self.asset_dir, self.locale, f"{prompt_name}.wav")
        if os.path.exists(file_path):
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.play()
            except Exception as e:
                logging.error(f"Failed to play {file_path}: {e}")
        else:
            logging.warning(f"Audio file missing: {file_path} (Fallback to visual only)")

    def play_success(self):
        self.play_prompt("success")
        
    def play_guidance(self):
        self.play_prompt("move_closer")
