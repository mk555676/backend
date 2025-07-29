from django.contrib import admin
from django.utils.timezone import make_aware
import datetime
from firebase_admin import auth
from .models import FirebaseUser

class FirebaseUserAdmin(admin.ModelAdmin):
    list_display = ("email", "uid", "created_at")  # Columns in admin panel

    def get_queryset(self, request):
        """
        Override the queryset to fetch users dynamically from Firebase.
        """
        users = auth.list_users().iterate_all()
        firebase_users = []
        
        for user in users:
            user_data = FirebaseUser(
                email=user.email,
                uid=user.uid,
                created_at=make_aware(datetime.datetime.utcfromtimestamp(user.user_metadata.creation_timestamp / 1000))
            )
            firebase_users.append(user_data)

        return firebase_users  # Returns a list instead of a QuerySet

admin.site.register(FirebaseUser, FirebaseUserAdmin)
