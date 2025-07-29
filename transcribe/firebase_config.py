# # firebase_setup.py
# import firebase_admin
# from firebase_admin import credentials, firestore, storage

# def initialize_firebase():
#     FIREBASE_CREDENTIALS = r'C:\backend\myproject\firebase.json'  # Update this path
#     cred = credentials.Certificate(FIREBASE_CREDENTIALS)
#     firebase_admin.initialize_app(cred, {
#         'storageBucket': 'speaknorder.appspot.com'  # Update with your bucket name
#     })

#     db = firestore.client()
#     bucket = storage.bucket()
#     return db, bucket



# firebase_setup.py
import firebase_admin
from firebase_admin import credentials, firestore, storage

def initialize_firebase():
    # Check if the default app is already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(r'C:\backend\myproject\firebase.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'speaknorder.appspot.com'
        })

    # Get Firestore and Storage references
    db = firestore.client()
    bucket = storage.bucket()
    return db, bucket