"""Audio handling utilities for STT and TTS streaming."""

import io
from typing import AsyncGenerator, Optional
import assemblyai as aai
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

from logger.custom_logger import CustomLogger
from config import settings

_LOG = CustomLogger().get_logger(__name__)


class AudioHandler:
    """Handles speech-to-text and text-to-speech streaming."""

    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        
        # Initialize AssemblyAI for STT
        if settings.ASSEMBLYAI_API_KEY:
            aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
            self.stt_available = True
        else:
            self.stt_available = False
            self.log.warning("AssemblyAI API key not configured; STT disabled")
        
        # Initialize ElevenLabs for TTS
        if settings.ELEVENLABS_API_KEY:
            self.tts_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
            self.tts_available = True
        else:
            self.tts_available = False
            self.log.warning("ElevenLabs API key not configured; TTS disabled")

    async def transcribe_audio_stream(self, audio_data: bytes) -> str:
        """
        Convert audio bytes to text using AssemblyAI.
        
        Args:
            audio_data: Raw audio bytes (WAV, MP3, etc).
            
        Returns:
            Transcribed text.
            
        Raises:
            ValueError: If STT unavailable.
        """
        if not self.stt_available:
            raise ValueError("Speech-to-text not configured")
        
        try:
            # Create transcriber and submit audio
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_data)
            
            if transcript.status == aai.TranscriptStatus.error:
                error_msg = f"Transcription error: {transcript.error}"
                self.log.error(error_msg)
                raise ValueError(error_msg)
            
            self.log.info("Audio transcribed successfully", text_length=len(transcript.text))
            return transcript.text
        except Exception as e:
            self.log.error("Transcription failed", error=str(e))
            raise

    async def synthesize_speech_stream(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (default)
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio from text using ElevenLabs.
        
        Args:
            text: Text to synthesize.
            voice_id: ElevenLabs voice ID (default: Rachel).
            
        Yields:
            Audio chunks as bytes.
            
        Raises:
            ValueError: If TTS unavailable.
        """
        if not self.tts_available:
            raise ValueError("Text-to-speech not configured")
        
        try:
            # Generate speech with streaming
            response = self.tts_client.text_to_speech.convert_with_voice_model(
                text=text,
                voice_id=voice_id,
                model_id="eleven_turbo_v2",  # Fastest model for real-time
                voice_settings=None,
            )
            
            # Yield audio in chunks
            for chunk in response:
                if isinstance(chunk, bytes):
                    yield chunk
                elif isinstance(chunk, BinaryData):
                    yield chunk.body if hasattr(chunk, 'body') else bytes(chunk)
            
            self.log.info("Speech synthesized and streamed", text_length=len(text))
        except Exception as e:
            self.log.error("Speech synthesis failed", error=str(e))
            raise

    async def convert_audio_format(
        self,
        audio_data: bytes,
        from_format: str = "webm",
        to_format: str = "wav"
    ) -> bytes:
        """
        Convert audio from one format to another using pydub.
        
        Args:
            audio_data: Raw audio bytes.
            from_format: Source format (webm, mp3, wav, etc).
            to_format: Target format (wav, mp3, etc).
            
        Returns:
            Converted audio bytes.
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=from_format)
            
            # Convert to target format
            output = io.BytesIO()
            audio.export(output, format=to_format)
            output.seek(0)
            
            self.log.info(f"Audio converted from {from_format} to {to_format}")
            return output.read()
        except Exception as e:
            self.log.error(f"Audio conversion failed", error=str(e))
            raise

    def get_supported_voices(self) -> list:
        """
        Get list of available ElevenLabs voices.
        
        Returns:
            List of voice dicts with id, name, description.
        """
        if not self.tts_available:
            return []
        
        try:
            voices = self.tts_client.voices.get_all()
            return [
                {
                    "id": v.voice_id,
                    "name": v.name,
                    "preview_url": v.preview_url if hasattr(v, 'preview_url') else None
                }
                for v in voices.voices
            ]
        except Exception as e:
            self.log.error("Failed to fetch voices", error=str(e))
            return []
