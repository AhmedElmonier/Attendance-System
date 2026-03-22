import sys
import time
from src.audio.engine import AudioEngine

def simulate_audio_flow():
    print("Initializing Audio Engine...")
    engine = AudioEngine(asset_dir="assets/audio")
    
    # Simulate a successful match
    print("Simulating Successful Scan (English)...")
    engine.set_locale("en")
    engine.play_success()
    time.sleep(2)
    
    # Simulate a smart guidance trigger
    print("Simulating Smart Guidance (Arabic)...")
    engine.set_locale("ar")
    engine.play_guidance()
    time.sleep(2)
    
    print("Audio simulation complete. (Note: Ensure .wav files exist in assets/audio/[en|ar]/ for true playback)")

if __name__ == "__main__":
    simulate_audio_flow()
