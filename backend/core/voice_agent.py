"""Voice agent for handling real-time voice chat interactions."""

from typing import Optional, AsyncGenerator
from datetime import datetime
from bson import ObjectId

from logger.custom_logger import CustomLogger
from config import settings
from core.safety_checker import SafetyChecker
from core.journal_analyzer import JournalAnalyzer
from core.coach import CoachAgent
from db.mongo import get_db
from db.repositories.message_repo import MessageRepository, Message, MessageType
from db.repositories.session_repository import SessionRepository
from db.repositories.user_repository import UserRepository
from utils.audio_handler import AudioHandler

_LOG = CustomLogger().get_logger(__name__)


class VoiceAgent:
    """
    Orchestrates real-time voice conversations by coordinating:
    1. Speech-to-text transcription
    2. Safety checking
    3. Sentiment analysis
    4. Coach response generation
    5. Text-to-speech streaming
    """

    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.log = CustomLogger().get_logger(__name__)
        
        # Initialize components
        self.audio_handler = AudioHandler()
        self.safety_checker = SafetyChecker()
        self.journal_analyzer = JournalAnalyzer()
        self.coach = CoachAgent()
        
        # Initialize repositories
        db = get_db()
        self.message_repo = MessageRepository(db)
        self.session_repo = SessionRepository(db)
        self.user_repo = UserRepository(db)

    async def process_voice_message(
        self,
        audio_data: bytes,
        audio_format: str = "webm"
    ) -> AsyncGenerator[bytes, None]:
        """
        Process voice input and stream audio response.
        
        Flow:
        1. Transcribe audio → text
        2. Check safety
        3. Extract sentiment
        4. Generate coach response
        5. Stream TTS audio back
        
        Args:
            audio_data: Raw audio bytes.
            audio_format: Audio format (webm, wav, mp3).
            
        Yields:
            Audio chunks for response streaming.
        """
        user_transcript = None
        safety_passed = False
        
        try:
            # Step 1: Transcribe audio
            self.log.info("Transcribing audio", user_id=self.user_id, session_id=self.session_id)
            user_transcript = await self.audio_handler.transcribe_audio_stream(audio_data)
            self.log.info("Audio transcribed", text=user_transcript[:100])
            
            # Step 2: Safety check
            self.log.info("Running safety check", user_id=self.user_id)
            safety_result = self.safety_checker.check_text(user_transcript)
            safety_passed = safety_result.is_safe
            
            if not safety_passed:
                self.log.warning(
                    "Safety check failed",
                    user_id=self.user_id,
                    violation_type=safety_result.violation_type
                )
                # Generate safety response
                response_text = self._generate_safety_response(safety_result.violation_type)
                async for chunk in self.audio_handler.synthesize_speech_stream(response_text):
                    yield chunk
                
                # Save interaction to database
                await self._save_message(user_transcript, "SAFETY_VIOLATION", sentiment="NEGATIVE")
                return
            
            # Step 3: Analyze sentiment and extract insights
            self.log.info("Analyzing sentiment", user_id=self.user_id)
            sentiment_result = self.journal_analyzer.analyze_sentiment(user_transcript)
            sentiment = sentiment_result.get("label", "NEUTRAL")
            
            # Step 4: Generate coach response
            self.log.info("Generating coach response", user_id=self.user_id)
            coach_response = await self.coach.generate_response(
                user_input=user_transcript,
                session_id=self.session_id,
                user_id=self.user_id,
                sentiment=sentiment
            )
            response_text = coach_response.get("response", "I'm here to support you.")
            
            # Step 5: Stream TTS audio
            self.log.info("Streaming TTS response", user_id=self.user_id)
            async for chunk in self.audio_handler.synthesize_speech_stream(response_text):
                yield chunk
            
            # Save conversation to database
            await self._save_message(
                user_transcript,
                response_text,
                sentiment=sentiment
            )
            
        except ValueError as e:
            self.log.error(f"Voice processing error: {str(e)}", user_id=self.user_id)
            # Stream fallback response
            fallback = "I'm experiencing a technical issue. Please try again or contact support."
            async for chunk in self.audio_handler.synthesize_speech_stream(fallback):
                yield chunk
        except Exception as e:
            self.log.error(
                "Unexpected error in voice processing",
                user_id=self.user_id,
                error=str(e)
            )
            # Stream error response
            error_response = "An unexpected error occurred. Please try again."
            try:
                async for chunk in self.audio_handler.synthesize_speech_stream(error_response):
                    yield chunk
            except:
                pass  # If TTS also fails, no response can be streamed

    def _generate_safety_response(self, violation_type: str) -> str:
        """Generate a response for safety violations."""
        responses = {
            "SELF_HARM": "I'm concerned about your safety. Please reach out to a crisis counselor immediately.",
            "CRISIS": "This sounds serious. Please contact a mental health professional or crisis line right away.",
            "HARMFUL_CONTENT": "I can't engage with that content. Let's refocus on your wellness.",
            "INAPPROPRIATE": "I need to keep our conversation appropriate and focused on your wellness."
        }
        return responses.get(violation_type, "I'm here to support your wellness journey.")

    async def _save_message(
        self,
        user_text: str,
        assistant_text: str,
        sentiment: str = "NEUTRAL"
    ) -> None:
        """Save user and assistant messages to database."""
        try:
            # User message
            user_msg = Message(
                session_id=ObjectId(self.session_id),
                user_id=ObjectId(self.user_id),
                content=user_text,
                message_type=MessageType.USER,
                is_voice=True,
                sentiment=sentiment,
                timestamp=datetime.utcnow()
            )
            await self.message_repo.create(user_msg)
            
            # Assistant message
            assistant_msg = Message(
                session_id=ObjectId(self.session_id),
                user_id=ObjectId(self.user_id),
                content=assistant_text,
                message_type=MessageType.ASSISTANT,
                is_voice=True,
                timestamp=datetime.utcnow()
            )
            await self.message_repo.create(assistant_msg)
            
            self.log.info("Messages saved", session_id=self.session_id)
        except Exception as e:
            self.log.error("Failed to save messages", error=str(e))

    async def get_voice_list(self) -> list:
        """Get available TTS voices."""
        return self.audio_handler.get_supported_voices()
