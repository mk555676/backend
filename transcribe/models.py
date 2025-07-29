from django.db import models
from django.contrib.auth.models import AbstractUser
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# models.py
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=100)  # Category can be Pizza, Pasta, etc.

    def __str__(self):
        return self.name


    
class Cart(models.Model):
    items = models.ManyToManyField(MenuItem)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class CustomUser (AbstractUser ):
    # Other fields for your custom user
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Change this to a unique name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Change this to a unique name
        blank=True,
        help_text='Specific permissions for this user.'
    )
class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

class VoiceSample(models.Model):
    unique_id = models.CharField(max_length=100, unique=True)
    profile_data = models.JSONField()  # Store user profile data as JSON
    audio_file = models.FileField(upload_to='voice_samples/')  # Store audio files
    def __str__(self):
        return self.unique_id
    
class FirebaseUser(models.Model):
    email = models.EmailField(unique=True)
    uid = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.email

    class Meta:
        managed = False  # This prevents Django from creating a database table
        
class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name