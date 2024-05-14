from django.urls import path
from . import views

urlpatterns = [
    path('video_stream/', views.video_stream_view, name='video_stream'),
]