import os
import logging
from pathlib import Path

import pygame


class AudioEngine:
    def __init__(self, asset_dir=None):
        if asset_dir is None:
            asset_dir = Path(__file__).resolve().parent / "assets" / "audio"
        self.asset_dir = Path(asset_dir)
        self.locale = "en"
        self._sound_cache: dict[tuple[str, str], pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init()
            self.initialized = True
        except OSError as e:
            logging.exception(f"Failed to init audio engine: {e}")
            self.initialized = False
        except RuntimeError as e:
            logging.exception(f"Failed to init audio engine: {e}")
            self.initialized = False

    def set_locale(self, locale: str):
        if locale in ["en", "ar"]:
            self.locale = locale

    def play_prompt(self, prompt_name: str):
        if not self.initialized:
            return

        cache_key = (self.locale, prompt_name)
        if cache_key in self._sound_cache:
            self._sound_cache[cache_key].play()
            return

        file_path = self.asset_dir / self.locale / f"{prompt_name}.wav"
        if file_path.exists():
            try:
                sound = pygame.mixer.Sound(str(file_path))
                self._sound_cache[cache_key] = sound
                sound.play()
            except (OSError, RuntimeError) as e:
                logging.error(f"Failed to play {file_path}: {e}")
        else:
            logging.warning(
                f"Audio file missing: {file_path} (Fallback to visual only)"
            )

    def play_success(self):
        self.play_prompt("success")

    def play_guidance(self):
        self.play_prompt("move_closer")
