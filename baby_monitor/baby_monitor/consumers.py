import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2
import pickle
import base64
import numpy as np
import sounddevice as sd
import asyncio
from pvrecorder import PvRecorder

class VideoStreamConsumer(AsyncWebsocketConsumer):
    connected_clients = set()  # To keep track of all connected clients

    async def connect(self):
        await self.accept()
        self.connected_clients.add(self)

    async def disconnect(self, close_code):
        self.connected_clients.remove(self)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if 'video' in data:
            frame_data = data['video']
            # Relay the frame to all other clients
            await self.broadcast_video_frame(frame_data)

    async def broadcast_video_frame(self, frame_data):
        for client in self.connected_clients:
            if client != self:  # Do not send to self
                await client.send(text_data=json.dumps({'video': frame_data}))


class AudioStreamConsumer(AsyncWebsocketConsumer):
    connected_clients = set()  # To keep track of all connected clients

    async def connect(self):
        await self.accept()
        self.connected_clients.add(self)

    async def disconnect(self, close_code):
        self.connected_clients.remove(self)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if 'audio' in data:
            audio_data = data['audio']
            # Relay the audio to all other clients
            await self.broadcast_audio_frame(audio_data)

    async def broadcast_audio_frame(self, audio_data):
        for client in self.connected_clients:
            if client != self:  # Do not send to self
                await client.send(text_data=json.dumps({'audio': audio_data}))
