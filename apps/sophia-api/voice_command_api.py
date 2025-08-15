#!/usr/bin/env python3
"""
SOPHIA Voice Command API - Production-Grade Streaming Pipeline
Handles speech-to-text, command execution, and text-to-speech streaming
"""

import os
import json
import asyncio
import logging
import tempfile
import time
from typing import Optional, Dict, Any, AsyncGenerator
from pathlib import Path
import io
import base64

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import aiofiles

# Import SOPHIA components
import sys
sys.path.append('/home/ubuntu/sophia-intel')
from integrations.elevenlabs_client import ElevenLabsStreamingClient, SOPHIAVoicePersona
from mcp_servers.ai_router import AIRouter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceCommandProcessor:
    """Processes voice commands through the complete pipeline"""
    
    def __init__(self):
        # Initialize components
        self.voice_client = ElevenLabsStreamingClient()
        self.persona = SOPHIAVoicePersona()
        self.ai_router = AIRouter()
        
        # OpenAI client for Whisper (speech-to-text)
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        
        logger.info("Voice command processor initialized")
    
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "webm") -> str:
        """
        Transcribe audio to text using OpenAI Whisper
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (webm, mp3, wav, etc.)
            
        Returns:
            Transcribed text
        """
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using OpenAI Whisper
                with open(temp_file_path, "rb") as audio_file:
                    transcript = await self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"  # English for SOPHIA
                    )
                
                transcribed_text = transcript.text.strip()
                logger.info(f"Transcribed audio: {transcribed_text[:100]}...")
                
                return transcribed_text
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    async def execute_command(self, command_text: str) -> Dict[str, Any]:
        """
        Execute command through SOPHIA's AI router
        
        Args:
            command_text: Transcribed command text
            
        Returns:
            Command execution result
        """
        try:
            # Route command through AI router
            result = await self.ai_router.route_request({
                "message": command_text,
                "type": "voice_command",
                "context": "mobile_voice_interface"
            })
            
            logger.info(f"Command executed: {command_text[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return {
                "response": f"I encountered an issue processing your request: {str(e)}",
                "error": True,
                "context": "error"
            }
    
    async def stream_voice_response(
        self, 
        response_text: str, 
        context: str = "general"
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream text-to-speech response
        
        Args:
            response_text: Text to convert to speech
            context: Context for persona enhancement
            
        Yields:
            Audio chunks as bytes
        """
        try:
            async for audio_chunk in self.voice_client.stream_text_to_speech(response_text, context):
                yield audio_chunk
                
        except Exception as e:
            logger.error(f"Voice response streaming failed: {str(e)}")
            # Yield error message as audio
            error_text = "I'm having trouble with my voice right now, but I'm still here to help you."
            async for audio_chunk in self.voice_client.stream_text_to_speech(error_text, "error"):
                yield audio_chunk

# Initialize FastAPI app
app = FastAPI(
    title="SOPHIA Voice Command API",
    description="Production-grade voice command interface for SOPHIA Intel",
    version="2.0.0"
)

# Configure CORS for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile PWA
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize voice processor
voice_processor = VoiceCommandProcessor()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "sophia-voice-api",
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": time.time(),
        "voice_enabled": True,
        "persona": "Smart Asian American Female"
    }

@app.get("/voice/info")
async def get_voice_info():
    """Get voice configuration information"""
    try:
        voice_info = voice_processor.voice_client.get_voice_info()
        return {
            "status": "success",
            "voice_info": voice_info,
            "capabilities": [
                "speech_to_text",
                "command_execution", 
                "text_to_speech_streaming",
                "persona_enhancement"
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get voice info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/transcribe")
async def transcribe_audio_endpoint(audio: UploadFile = File(...)):
    """
    Transcribe uploaded audio to text
    
    Args:
        audio: Audio file upload
        
    Returns:
        Transcription result
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Determine audio format from filename
        audio_format = "webm"  # Default
        if audio.filename:
            audio_format = audio.filename.split(".")[-1].lower()
        
        # Transcribe audio
        transcribed_text = await voice_processor.transcribe_audio(audio_data, audio_format)
        
        return {
            "status": "success",
            "transcription": transcribed_text,
            "audio_format": audio_format,
            "audio_size": len(audio_data)
        }
        
    except Exception as e:
        logger.error(f"Transcription endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/command")
async def execute_voice_command(audio: UploadFile = File(...)):
    """
    Complete voice command pipeline: audio -> text -> execution -> response
    
    Args:
        audio: Audio file with voice command
        
    Returns:
        Streaming audio response
    """
    try:
        # Step 1: Transcribe audio to text
        audio_data = await audio.read()
        audio_format = "webm"
        if audio.filename:
            audio_format = audio.filename.split(".")[-1].lower()
        
        transcribed_text = await voice_processor.transcribe_audio(audio_data, audio_format)
        
        if not transcribed_text.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio")
        
        # Step 2: Execute command
        command_result = await voice_processor.execute_command(transcribed_text)
        
        # Step 3: Determine response context
        context = command_result.get("context", "general")
        if command_result.get("error"):
            context = "error"
        elif "greeting" in transcribed_text.lower() or "hello" in transcribed_text.lower():
            context = "greeting"
        elif "thank" in transcribed_text.lower():
            context = "completion"
        
        # Step 4: Stream voice response
        response_text = command_result.get("response", "I'm processing your request.")
        
        async def generate_audio_stream():
            """Generate streaming audio response"""
            try:
                async for audio_chunk in voice_processor.stream_voice_response(response_text, context):
                    # Encode audio chunk as base64 for streaming
                    chunk_data = {
                        "type": "audio",
                        "data": base64.b64encode(audio_chunk).decode('utf-8'),
                        "timestamp": time.time()
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Send completion signal
                completion_data = {
                    "type": "complete",
                    "transcription": transcribed_text,
                    "response_text": response_text,
                    "context": context,
                    "timestamp": time.time()
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "error": str(e),
                    "timestamp": time.time()
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_audio_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Voice command endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/speak")
async def text_to_speech_endpoint(request: Request):
    """
    Convert text to speech with streaming response
    
    Body:
        {
            "text": "Text to speak",
            "context": "general|greeting|confirmation|error"
        }
    """
    try:
        body = await request.json()
        text = body.get("text", "")
        context = body.get("context", "general")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        async def generate_speech_stream():
            """Generate streaming speech response"""
            try:
                async for audio_chunk in voice_processor.stream_voice_response(text, context):
                    # Stream raw audio bytes
                    yield audio_chunk
                    
            except Exception as e:
                logger.error(f"Speech generation failed: {str(e)}")
                # Return silence on error
                yield b''
        
        return StreamingResponse(
            generate_speech_stream(),
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "no-cache",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Text-to-speech endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voice/test")
async def test_voice_pipeline():
    """Test the complete voice pipeline"""
    try:
        # Test voice synthesis
        test_text = "Hello! I'm SOPHIA, your intelligent AI assistant. This is a test of my voice capabilities."
        
        # Generate test audio
        audio_chunks = []
        async for chunk in voice_processor.stream_voice_response(test_text, "greeting"):
            audio_chunks.append(chunk)
        
        total_audio = b''.join(audio_chunks)
        
        return {
            "status": "success",
            "test_text": test_text,
            "audio_generated": len(total_audio) > 0,
            "audio_size": len(total_audio),
            "chunks_count": len(audio_chunks),
            "voice_info": voice_processor.voice_client.get_voice_info()
        }
        
    except Exception as e:
        logger.error(f"Voice pipeline test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Run the voice API server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )

