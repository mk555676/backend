from django.urls import path
from .consumers import VoiceOrderingConsumer

websocket_urlpatterns = [
    path("ws/voice-ordering/", VoiceOrderingConsumer.as_asgi()),
]
