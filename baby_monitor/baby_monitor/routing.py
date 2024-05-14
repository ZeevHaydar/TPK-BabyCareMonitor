from django.urls import path
from .consumers import VideoStreamConsumer

websocket_urlpatterns = [
    path('video_stream', VideoStreamConsumer.as_asgi()),
]