import whisper
import os

# Load the Whisper model
model = whisper.load_model("small")  # Use the model of your choice

def transcribe_audio(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: The file at path '{file_path}' does not exist.")
        return None
    
    if not os.access(file_path, os.R_OK):
        print(f"Error: The file at path '{file_path}' is not readable.")
        return None

    try:
        result = model.transcribe(file_path)
        print(f"Transcription result: {result}")
        print(f"Transcription text: {result.get('text', 'No text found')}")
        return result.get('text', 'No text found')
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None
