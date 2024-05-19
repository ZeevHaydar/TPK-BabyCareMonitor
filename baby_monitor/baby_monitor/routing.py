from django.urls import re_path
from .consumers import VideoStreamConsumer, AudioStreamConsumer

websocket_urlpatterns = [
    re_path(r'ws/video_stream/$', VideoStreamConsumer.as_asgi()),
    re_path(r'ws/audio_stream/$', AudioStreamConsumer.as_asgi()),
]