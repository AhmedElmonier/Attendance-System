import time
import logging
from src.audio.engine import AudioEngine

class CaptureLoop:
    def __init__(self, audio_engine: AudioEngine):
        self.audio = audio_engine
        self.face_in_frame_time = None
        self.GUIDANCE_DELAY_SEC = 3.0
        
    def process_frame(self, frame_has_face: bool, match_confidence: float = 0.0, is_stale_template: bool = False):
        if frame_has_face:
            if self.face_in_frame_time is None:
                self.face_in_frame_time = time.time()
                
            elapsed = time.time() - self.face_in_frame_time
            
            # FR-006: 98% confidence threshold logic for stale templates
            threshold = 0.98 if is_stale_template else 0.85
            
            if match_confidence >= threshold:
                logging.info(f"Match Successful (Conf: {match_confidence}, Stale: {is_stale_template})")
                
                if is_stale_template:
                    logging.warning("Event flagged: Stale Template used for matching.")
                    
                self.audio.play_success()
                self.reset_state()
                return True
            else:
                if elapsed > self.GUIDANCE_DELAY_SEC:
                    logging.info("Triggering Smart Audio Guidance (No match after 3s)")
                    self.audio.play_guidance()
                    self.face_in_frame_time = time.time() # Reset to avoid spamming audio
                    
        else:
            self.reset_state()
            
        return False
        
    def reset_state(self):
        self.face_in_frame_time = None
