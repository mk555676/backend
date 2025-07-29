from rest_framework import serializers
from .models import MenuItem, CustomUser
from django.core.files.uploadedfile import UploadedFile
import uuid
from .firebase_config import initialize_firebase
from .models import VoiceSample

# Initialize Firebase and get db and bucket

db, bucket = initialize_firebase()
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'category', 'price', 'image_url']

# class OrderSerializer(serializers.ModelSerializer):
#     items = MenuItemSerializer(many=True)

    # class Meta:
    #     model = Order
    #     fields = ['id', 'items', 'total_price', 'timestamp']


class ProfilePictureSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField()

    def validate_profile_picture(self, value):
        if not isinstance(value, UploadedFile):
            raise serializers.ValidationError("Invalid image file")
        return value

    def update_user_profile_picture(self, user, profile_picture):
        # Generate a unique file name using uuid
        file_name = f"profile_pictures/{uuid.uuid4().hex}.jpg"
        
        # Upload the image to Firebase Storage
        blob = bucket.blob(file_name)
        blob.upload_from_file(profile_picture, content_type='image/jpeg')
        
        # Get the public URL of the uploaded file
        image_url = blob.public_url
        
        # Update the user's profile picture URL in Firestore
        user.profile_picture_url = image_url
        user.save()
        return image_url




class VoiceSampleSerializer(serializers.ModelSerializer):

    class Meta:

        model = VoiceSample

        fields = ['unique_id', 'profile_data', 'audio_file']