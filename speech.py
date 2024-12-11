import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import requests
from datetime import datetime
from fastapi.staticfiles import StaticFiles

# Constants
CHUNK_SIZE = 1024
XI_API_KEY = "sk_33e873c1c17a0ce48a48ea46ca1bb4e1bc4a725c86ff2df6"  # Replace with your valid API key
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Replace with your valid voice ID
OUTPUT_FOLDER = "output"  # Folder to save audio files

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# FastAPI app instance
app = FastAPI()

app.mount("/static", StaticFiles(directory="output"), name="static")

class TTSRequest(BaseModel):
    text: str
    filename: str = None

# API endpoint for TTS
@app.post("/text-to-speech/")
async def text_to_speech(request: TTSRequest):
    text = request.text
    filename = request.filename or f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

    """
    Converts input text to speech and saves the audio file in the output folder.
    
    Args:
        text (str): Text to convert to speech.
        filename (str): Custom filename for the output (optional).
        
    Returns:
        JSON: Details of the generated audio file.
    """
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY,
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }
    
    try:
        # Request TTS API
        response = requests.post(tts_url, headers=headers, json=data, stream=True)
        if not response.ok:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        # Determine the output filename
        if not filename:
            filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        # Save the streamed audio to the output file
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        
        # return {
        #     "message": "Audio file created successfully.",
        #     "filename": filename,
        #     "path": output_path,
        # }
        return {
            "message": "Audio file created successfully.",
            "filename": filename,
            "url": f"https://your-hosted-service-url.com/static/{filename}",
        }


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

