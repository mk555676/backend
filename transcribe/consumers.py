# VoiceOrderingConsumer.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .firebase_config import initialize_firebase
from io import BytesIO
import base64
import whisper
import soundfile as sf

# Firebase setup
db, bucket = initialize_firebase()

# Load Whisper model
model = whisper.load_model("base")

class VoiceOrderingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.transcription = ""  # Store the continuous transcription

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            audio_chunk_base64 = data.get("audio")

            # Decode base64 audio
            audio_data = base64.b64decode(audio_chunk_base64)
            audio_file = BytesIO(audio_data)

            # Read and save audio to WAV
            audio_wav, sample_rate = sf.read(audio_file)
            temp_audio_path = "temp_audio.wav"
            sf.write(temp_audio_path, audio_wav, sample_rate)

            # Transcribe with Whisper
            result = model.transcribe(temp_audio_path, language="en")
            transcription = result["text"]
            self.transcription += " " + transcription

            # Command handling
            if "menu" in self.transcription.lower():
                menu_doc = db.collection("menu").document("pizza").get()
                if menu_doc.exists:
                    menu = menu_doc.to_dict()
                    await self.send(json.dumps({"menu": menu}))
                else:
                    await self.send(json.dumps({"message": "Menu not found"}))
            else:
                await self.send(json.dumps({"partial_transcription": transcription}))

        except Exception as e:
            error_message = {"error": str(e)}
            await self.send(json.dumps(error_message))