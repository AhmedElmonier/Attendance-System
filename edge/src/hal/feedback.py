import logging
from typing import Optional
import time

logger = logging.getLogger(__name__)


class FeedbackModule:
    MESSAGES = {
        "ar": {
            "welcome": "مرحباً بك في نظام الحضور",
            "identity_confirmed": "تم تأكيد الهوية",
            "identity_not_recognized": "لم يتم التعرف على الهوية، يرجى استخدام طريقة بديلة",
            "identity_partial": "تم التحقق جزئياً، بانتظار مراجعة المدير",
            "look_at_camera": "الرجاء النظر إلى الكاميرا",
            "turn_left": "الرجاء الدوران يساراً ←",
            "turn_right": "الرجاء الدوران يميناً →",
            "tilt_up": "الرجاء الإمالة للأعلى ↑",
            "tilt_down": "الرجاء الإمالة للأسفل ↓",
            "good_position": "موقف جيد ✓",
            "too_dark": "الإضاءة ضعيفة",
            "too_bright": "الإضاءة قوية جداً",
            "image_blurry": "الصورة غير واضحة",
            "enrollment_success": "تم التسجيل بنجاح",
            "enrollment_failed": "فشل التسجيل، يرجى المحاولة مرة أخرى",
            "sync_success": "تمت المزامنة بنجاح",
            "sync_failed": "فشلت المزامنة",
            "offline_mode": "وضع عدم الاتصال",
            "clock_in_recorded": "تم تسجيل الحضور",
            "clock_out_recorded": "تم تسجيل الانصراف",
        },
        "en": {
            "welcome": "Welcome to Attendance System",
            "identity_confirmed": "Identity Confirmed",
            "identity_not_recognized": "Identity Not Recognized, Please use alternative method",
            "identity_partial": "Identity Partially Verified, Manager Review Required",
            "look_at_camera": "Please look at the camera",
            "turn_left": "Turn left ←",
            "turn_right": "Turn right →",
            "tilt_up": "Tilt up ↑",
            "tilt_down": "Tilt down ↓",
            "good_position": "Good position ✓",
            "too_dark": "Lighting too dark",
            "too_bright": "Lighting too bright",
            "image_blurry": "Image is blurry",
            "enrollment_success": "Enrollment Successful",
            "enrollment_failed": "Enrollment Failed, Please try again",
            "sync_success": "Sync Successful",
            "sync_failed": "Sync Failed",
            "offline_mode": "Offline Mode",
            "clock_in_recorded": "Clock In Recorded",
            "clock_out_recorded": "Clock Out Recorded",
        },
    }

    STATUS_COLORS = {
        "green": (0, 255, 0),
        "red": (0, 0, 255),
        "yellow": (0, 255, 255),
        "white": (255, 255, 255),
        "blue": (255, 0, 0),
    }

    def __init__(self, language: str = "en", use_audio: bool = False):
        self.language = language if language in ["ar", "en"] else "en"
        self.use_audio = use_audio
        self._last_message = ""
        self._last_color = self.STATUS_COLORS["white"]

    def set_language(self, language: str) -> None:
        if language in ["ar", "en"]:
            self.language = language

    def get_message(self, key: str) -> str:
        return self.MESSAGES[self.language].get(key, self.MESSAGES["en"].get(key, key))

    def set_status(self, message_key: str, color: str = "white") -> None:
        self._last_message = self.get_message(message_key)
        self._last_color = self.STATUS_COLORS.get(color, self.STATUS_COLORS["white"])

        if self.use_audio:
            self._play_audio(message_key)

    def _play_audio(self, message_key: str) -> None:
        logger.info(f"[AUDIO] Would play: {message_key} ({self.language})")

    def get_feedback(self, message_key: str) -> tuple[str, tuple]:
        return self.get_message(message_key), self.STATUS_COLORS["white"]

    def get_zone_feedback(self, zone: str) -> tuple[str, tuple]:
        zone_messages = {
            "green": ("identity_confirmed", "green"),
            "gray": ("identity_partial", "yellow"),
            "red": ("identity_not_recognized", "red"),
        }
        msg_key, color = zone_messages.get(zone, ("identity_not_recognized", "red"))
        return self.get_message(msg_key), self.STATUS_COLORS[color]

    def get_pose_feedback(self, direction: str) -> tuple[str, tuple]:
        direction_messages = {
            "turn_left": "turn_left",
            "turn_right": "turn_right",
            "tilt_up": "tilt_up",
            "tilt_down": "tilt_down",
            "centered": "good_position",
        }
        msg_key = direction_messages.get(direction, "look_at_camera")
        return self.get_message(msg_key), self.STATUS_COLORS["white"]
