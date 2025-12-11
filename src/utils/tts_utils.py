"""
Text-to-Speech using Google TTS (better quality, requires internet).
Uses pygame for audio playback, with fallback to system audio players.
"""

import os
import platform
import subprocess
import tempfile
from typing import Optional
import warnings

from dotenv import load_dotenv

load_dotenv()

# Try to import gTTS
try:
    from gtts import gTTS

    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("Warning: gTTS not installed. Install with: pip install gtts")

# Try pygame as primary audio player
try:
    # Suppress pygame warnings and messages
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

    import pygame

    # Suppress pygame initialization messages
    pygame.mixer.pre_init()
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class TextToSpeech:
    """Text-to-Speech handler using Google TTS."""

    def __init__(self):
        self.enabled = GTTS_AVAILABLE
        self.use_pygame = PYGAME_AVAILABLE

        self.speed = float(os.getenv("TTS_SPEED", "1.4"))
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self):
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except:
            return False

    def _build_atempo_filters(self, speed: float) -> str:
        filters = []
        remaining = speed

        while remaining > 2.0:
            filters.append("atempo=2.0")
            remaining /= 2.0

        while remaining < 0.5:
            filters.append("atempo=0.5")
            remaining /= 0.5

        filters.append(f"atempo={remaining}")
        return ",".join(filters)

    def speak(self, text: str):
        if not self.enabled:
            return

        try:
            clean_text = self._clean_text(text)
            if not clean_text:
                return

            # Create temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_path = tmp_file.name

            # Generate the audio
            tts = gTTS(text=clean_text, lang="en", slow=False)
            tts.save(tmp_path)

            if self.speed != 1.0 and self.ffmpeg_available:
                fast_path = tmp_path.replace(".mp3", "_fast.mp3")
                filter_chain = self._build_atempo_filters(self.speed)

                subprocess.run(
                    [
                        "ffmpeg",
                        "-i",
                        tmp_path,
                        "-filter:a",
                        filter_chain,
                        "-y",
                        fast_path,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                os.replace(fast_path, tmp_path)

            try:
                if self.use_pygame:
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                else:
                    system = platform.system()
                    if system == "Darwin":
                        subprocess.run(["afplay", tmp_path], check=True)
                    elif system == "Linux":
                        for player in ["aplay", "paplay", "mpg123", "mpv"]:
                            try:
                                subprocess.run(
                                    [player, tmp_path],
                                    check=True,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                )
                                break
                            except:
                                continue
                        else:
                            print("No audio player found.")
                    elif system == "Windows":
                        subprocess.run(
                            ["start", "/B", tmp_path], shell=True, check=True
                        )

            except Exception as e:
                print(f"Error playing audio: {e}")

            try:
                os.unlink(tmp_path)
            except:
                pass

        except Exception as e:
            print(f"Error with Google TTS: {e}")

    def _clean_text(self, text: str) -> str:
        if "{" in text and "}" in text:
            import json

            try:
                json_start = text.find("{")
                json_end = text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = text[json_start:json_end].replace("'", '"')
                    data = json.loads(json_str)
                    return data.get("followup", "")
            except:
                pass

        text = text.replace("**", "").replace("*", "").replace("#", "")
        text = text.replace("`", "").replace("_", " ")
        text = (
            text.replace("$", "dollars ").replace("%", "percent ").replace("&", "and ")
        )
        text = text.replace("IRA", "I R A").replace("CD", "Certificate of Deposit")
        text = text.replace("ATM", "A T M").replace("FAQ", "Frequently Asked Question")
        return " ".join(text.split()).strip()

    def stop(self):
        pass


_tts_instance: Optional[TextToSpeech] = None


def get_tts() -> TextToSpeech:
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech()
    return _tts_instance


def speak_text(text: str):
    if os.getenv("TTS_ENABLED", "true").lower() == "true":
        get_tts().speak(text)
