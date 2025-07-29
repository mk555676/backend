import os
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
import firebase_admin
from firebase_admin import credentials, firestore
from django.http import JsonResponse
import logging
logger = logging.getLogger(__name__)
if not firebase_admin._apps:
    cred = credentials.Certificate("speaknorder_python_key_firebase.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
encoder = VoiceEncoder()

def process_audio(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return None
    
    try:
        wav = preprocess_wav(file_path)  
        embedding = encoder.embed_utterance(wav)  
        if isinstance(embedding, np.ndarray) and embedding.size > 0:
            return embedding  
        else:
            print("Error: Embedding is empty or invalid.")
            return None
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None




def save_embeddings_to_firebase(user_id, embeddings):
    db = firestore.client()
    user_ref = db.collection("VoiceId").document(user_id)
    embeddings_dict = {f"embedding_{i}": embeddings[i].tolist() for i in range(len(embeddings))}

    user_ref.set(embeddings_dict) 

    print(f"Saved embeddings for user: {user_id}")

def compare_embeddings(registered_embedding, incoming_embedding):
    try:
        # Calculate cosine similarity between the two embeddings
        cosine_similarity = np.dot(registered_embedding, incoming_embedding) / (np.linalg.norm(registered_embedding) * np.linalg.norm(incoming_embedding))
        # A threshold to decide if the voice matches
        threshold = 0.8  
        if cosine_similarity > threshold:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error comparing embeddings: {e}")
        return False

def get_registered_embedding(user_id):
    try:
        user_ref = db.collection("VoiceId").document(user_id)
        user_data = user_ref.get()
        if user_data.exists:
            embeddings = user_data.to_dict()
            # Convert the saved embeddings back to numpy arrays
            embeddings_list = [np.array(embedding) for embedding in embeddings.values()]
            return embeddings_list
        else:
            return None
    except Exception as e:
        print(f"Error fetching registered embeddings: {e}")
        return None
def check_enrollment_status(user_id):
    # Your existing logic for checking enrollment status
    try:
        # Check enrollment status logic
        status = 'enrolled'  # Just a placeholder for your logic
        return status
    except Exception as e:
        return {'error': str(e)}


def check_enrollment_status_endpoint(request):
    user_id = request.GET.get('user_id')  # Get user_id from the query parameters
    if not user_id:
        logger.error('user_id is missing from the request')
        return JsonResponse({'error': 'user_id is required'}, status=400)

    logger.info(f"Received request for user_id: {user_id}")
    
    enrollment_status = check_enrollment_status(user_id)
    if isinstance(enrollment_status, dict) and 'error' in enrollment_status:
        logger.error(f"Error checking enrollment status for user {user_id}: {enrollment_status['error']}")
        return JsonResponse(enrollment_status, status=500)
    
    return JsonResponse({'enrollment_status': enrollment_status})