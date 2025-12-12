"""
Voice input handler for speech-to-text functionality using OpenAI Whisper.
Includes audio management to prevent feedback loops with TTS.
"""

import os
import threading
import time
import tempfile
import wave
from typing import Optional, Callable
import warnings

from dotenv import load_dotenv

# Suppress Whisper warnings
warnings.filterwarnings(
    "ignore", message="FP16 is not supported on CPU; using FP32 instead"
)

load_dotenv()

# Try to import OpenAI Whisper
try:
    import whisper
    import torch

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print(
        "Warning: OpenAI Whisper not installed. Install with: pip install openai-whisper"
    )

# Try to import pyaudio for microphone access
try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: PyAudio not installed. Install with: pip install pyaudio")


class VoiceInputHandler:
    """Handles speech-to-text input with audio management using OpenAI Whisper."""

    def __init__(self):
        """Initialize voice input handler."""
        self.enabled = WHISPER_AVAILABLE and PYAUDIO_AVAILABLE
        self.is_listening = False
        self.is_muted = False  # For preventing feedback loops
        self.whisper_model = None

        if not self.enabled:
            return

        # Initialize Whisper model
        try:
            print("🎤 Loading Whisper model...")
            # Use base model for good balance of speed and accuracy
            self.whisper_model = whisper.load_model("base")
            print("✅ Whisper model loaded")
        except Exception as e:
            print(f"Warning: Could not load Whisper model: {e}")
            self.enabled = False
            return

        # Initialize PyAudio for microphone access
        try:
            self.audio = pyaudio.PyAudio()
            print("✅ Microphone initialized")
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
            self.enabled = False

    def mute_listening(self):
        """Mute voice input to prevent feedback loops during TTS."""
        self.is_muted = True

    def unmute_listening(self):
        """Unmute voice input after TTS is complete."""
        self.is_muted = False

    def listen_for_command(
        self, timeout: int = 5, phrase_time_limit: int = 10
    ) -> Optional[str]:
        """
        Listen for a single voice command using Whisper.

        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time for the entire phrase

        Returns:
            Recognized text or None if no speech detected
        """
        if not self.enabled or self.is_muted:
            return None

        try:
            print("🎤 Listening... (speak now)")

            # Record audio from microphone
            audio_data = self._record_audio(timeout, phrase_time_limit)
            if audio_data is None:
                return None

            return self._process_audio_with_whisper(audio_data)

        except Exception as e:
            print(f"❌ Voice input error: {e}")
            return None

    def _record_audio(self, timeout: int, phrase_time_limit: int) -> Optional[bytes]:
        """Record audio from microphone."""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000  # Whisper works best with 16kHz

        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []
        silent_chunks = 0
        max_silent_chunks = int(timeout * RATE / CHUNK)

        try:
            # Record until silence or timeout
            for _ in range(int(phrase_time_limit * RATE / CHUNK)):
                data = stream.read(CHUNK)
                frames.append(data)

                # Simple silence detection (can be improved)
                if max(data) < 500:  # Threshold for silence
                    silent_chunks += 1
                    if silent_chunks > max_silent_chunks:
                        break
                else:
                    silent_chunks = 0

        finally:
            stream.stop_stream()
            stream.close()

        if len(frames) < 10:  # Too short
            print("⏰ No speech detected within timeout")
            return None

        return b"".join(frames)

    def _process_audio_with_whisper(self, audio_data: bytes) -> Optional[str]:
        """
        Process audio data with Whisper.

        Args:
            audio_data: Raw audio bytes

        Returns:
            Recognized text or None if recognition failed
        """
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                # Write WAV header and data
                with wave.open(tmp_file.name, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(16000)
                    wav_file.writeframes(audio_data)

                # Use Whisper to transcribe
                result = self.whisper_model.transcribe(tmp_file.name)
                text = result["text"].strip()

                # Clean up temporary file
                os.unlink(tmp_file.name)

                if text:
                    print(f"🎯 Recognized: {text}")
                    return text
                else:
                    print("❓ Could not understand the audio")
                    return None

        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            return None

    def is_voice_enabled(self) -> bool:
        """Check if voice input is available and enabled."""
        return self.enabled and not self.is_muted

    def get_status(self) -> str:
        """Get current status of voice input system."""
        if not WHISPER_AVAILABLE:
            return "❌ OpenAI Whisper not installed"
        if not PYAUDIO_AVAILABLE:
            return "❌ PyAudio not installed"
        if not self.enabled:
            return "❌ Voice input disabled (initialization error)"
        if self.is_muted:
            return "🔇 Voice input muted (TTS active)"
        return "✅ Voice input ready"


# Singleton instance
_voice_handler_instance: Optional[VoiceInputHandler] = None


def get_voice_handler() -> VoiceInputHandler:
    """Get or create voice input handler instance."""
    global _voice_handler_instance
    if _voice_handler_instance is None:
        _voice_handler_instance = VoiceInputHandler()
    return _voice_handler_instance


def listen_for_voice_input(timeout: int = 5) -> Optional[str]:
    """
    Convenience function to listen for voice input.

    Args:
        timeout: Maximum time to wait for speech

    Returns:
        Recognized text or None
    """
    handler = get_voice_handler()
    return handler.listen_for_command(timeout=timeout)
