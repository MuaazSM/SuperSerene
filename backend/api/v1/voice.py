"""WebSocket endpoint for real-time voice chat."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.exceptions import WebSocketException
import json
from typing import Optional

from logger.custom_logger import CustomLogger
from api.deps import get_current_user
from core.voice_agent import VoiceAgent
from db.mongo import get_db
from db.repositories.session_repository import SessionRepository
from exception.custom_exception import DocumentPortalException

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["voice"])


class VoiceConnectionManager:
    """Manages WebSocket connections for voice chat."""
    
    def __init__(self):
        self.active_connections: dict = {}
        self.log = CustomLogger().get_logger(__name__)
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Register new WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.log.info(f"Voice connection established", session_id=session_id)
    
    async def disconnect(self, session_id: str):
        """Unregister WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            self.log.info(f"Voice connection closed", session_id=session_id)
    
    async def send_audio_chunk(self, session_id: str, data: bytes):
        """Send audio chunk to client."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_bytes(data)
            except Exception as e:
                self.log.error(f"Failed to send audio chunk", error=str(e))
    
    async def send_json(self, session_id: str, data: dict):
        """Send JSON message to client."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(data)
            except Exception as e:
                self.log.error(f"Failed to send message", error=str(e))


manager = VoiceConnectionManager()


@router.websocket("/voice/{session_id}")
async def voice_chat_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time voice chat.
    
    Message Format (Client → Server):
    - Binary frames: Raw audio data (WebM, WAV, etc)
    - JSON: Control messages {"type": "start|stop|config", ...}
    
    Response Format (Server → Client):
    - Binary frames: Audio response (WAV format)
    - JSON: Status/transcript {"type": "status|transcript", ...}
    
    Example client flow:
    1. Connect to ws://host/ws/voice/{session_id}
    2. Send audio chunks (binary frames) as user speaks
    3. Receive transcript updates (JSON) and audio response (binary)
    4. Send control messages to stop recording/stop playback
    """
    
    log = CustomLogger().get_logger(__name__)
    
    try:
        # Validate session exists and user has access
        db = get_db()
        session_repo = SessionRepository(db)
        session = await session_repo.get(session_id)
        
        if not session:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        user_id = str(session.get("user_id"))
        
        # Accept connection
        await manager.connect(session_id, websocket)
        await manager.send_json(session_id, {
            "type": "connection_established",
            "session_id": session_id
        })
        
        # Initialize voice agent
        voice_agent = VoiceAgent(user_id, session_id)
        
        # Track buffered audio data
        audio_buffer = bytearray()
        silence_threshold = 0.5  # seconds
        
        log.info(f"Voice session started", session_id=session_id, user_id=user_id)
        
        while True:
            try:
                # Receive data from client
                data = await websocket.receive()
                
                # Handle binary audio data
                if "bytes" in data:
                    audio_bytes = data["bytes"]
                    audio_buffer.extend(audio_bytes)
                    
                    # Optionally: implement silence detection
                    # to auto-submit audio when user pauses
                    
                    log.debug(f"Audio chunk received", size=len(audio_bytes), buffer_size=len(audio_buffer))
                
                # Handle JSON control messages
                elif "text" in data:
                    try:
                        message = json.loads(data["text"])
                        msg_type = message.get("type")
                        
                        if msg_type == "submit":
                            # User submitted audio for processing
                            if len(audio_buffer) > 0:
                                await manager.send_json(session_id, {
                                    "type": "processing",
                                    "status": "transcribing"
                                })
                                
                                # Process voice message and stream response
                                try:
                                    audio_format = message.get("format", "webm")
                                    response_chunks = []
                                    
                                    async for audio_chunk in voice_agent.process_voice_message(
                                        bytes(audio_buffer),
                                        audio_format=audio_format
                                    ):
                                        response_chunks.append(audio_chunk)
                                        await manager.send_audio_chunk(session_id, audio_chunk)
                                    
                                    await manager.send_json(session_id, {
                                        "type": "response_complete",
                                        "chunks_sent": len(response_chunks)
                                    })
                                    
                                    # Clear buffer after successful processing
                                    audio_buffer.clear()
                                    
                                except Exception as e:
                                    log.error(f"Voice processing error", error=str(e))
                                    await manager.send_json(session_id, {
                                        "type": "error",
                                        "message": "Failed to process voice message"
                                    })
                        
                        elif msg_type == "cancel":
                            # User cancelled current input
                            audio_buffer.clear()
                            await manager.send_json(session_id, {
                                "type": "cancelled"
                            })
                        
                        elif msg_type == "get_voices":
                            # Request available voices
                            voices = await voice_agent.get_voice_list()
                            await manager.send_json(session_id, {
                                "type": "voices",
                                "voices": voices
                            })
                        
                        else:
                            log.warning(f"Unknown message type", type=msg_type)
                    
                    except json.JSONDecodeError:
                        log.error("Invalid JSON received")
                        await manager.send_json(session_id, {
                            "type": "error",
                            "message": "Invalid message format"
                        })
            
            except WebSocketDisconnect:
                log.info(f"Client disconnected", session_id=session_id)
                await manager.disconnect(session_id)
                break
            
            except Exception as e:
                log.error(f"WebSocket error", error=str(e))
                await manager.disconnect(session_id)
                break
    
    except Exception as e:
        log.error(f"Voice websocket initialization failed", error=str(e))
        await manager.disconnect(session_id)


@router.post("/voice/voices")
async def get_available_voices(current_user: dict = Depends(get_current_user)):
    """Get list of available TTS voices."""
    try:
        # Create temporary agent to get voices
        voice_agent = VoiceAgent(str(current_user.get("_id")), "temp")
        voices = await voice_agent.get_voice_list()
        return {"voices": voices}
    except Exception as e:
        _LOG.error(f"Failed to fetch voices", error=str(e))
        return {"voices": [], "error": str(e)}


@router.get("/voice/status/{session_id}")
async def get_voice_session_status(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status of voice session."""
    try:
        db = get_db()
        session_repo = SessionRepository(db)
        session = await session_repo.get(session_id)
        
        if not session:
            raise NotFoundError("Session not found")
        
        user_id = str(session.get("user_id"))
        if user_id != str(current_user.get("_id")):
            raise UnauthorizedError("Not authorized to access this session")
        
        return {
            "session_id": session_id,
            "active": session_id in manager.active_connections,
            "messages": session.get("message_count", 0)
        }
    except Exception as e:
        _LOG.error(f"Failed to get session status", error=str(e))
        raise
