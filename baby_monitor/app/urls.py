from django.urls import path
from . import views

# API endpoints
urlapipatterns = [
    path('api/audio_prediction/', views.process_the_audio, name="audio_prediction"),
]

# Template endpoints
urltemplatepatterns = [
    path('video_stream/', views.video_stream_view, name='video_stream'),
]