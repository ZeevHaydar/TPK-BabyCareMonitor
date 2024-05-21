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
import logging

logger = logging.getLogger(__name__)
class VideoStreamConsumer(AsyncWebsocketConsumer):
    connected_clients = set()  # To keep track of all connected clients

    async def connect(self):
        await self.accept()
        self.connected_clients.add(self)
        logger.info(f"Client connected: {self}")

    async def disconnect(self, close_code):
        if self in self.connected_clients:
            self.connected_clients.remove(self)
            logger.info(f"Client disconnected: {self}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        if 'video' in data:
            frame_data = data['video']
            # Relay the frame to all other clients
            await self.broadcast_video_frame(frame_data)

    async def broadcast_video_frame(self, frame_data):
        disconnected_clients = set()
        for client in self.connected_clients:
            if client != self:  # Do not send to self
                try:
                    await client.send(text_data=json.dumps({'video': frame_data}))
                except Exception as e:
                    logger.error(f"Error sending to client {client}: {e}")
                    disconnected_clients.add(client)
        
        # Remove disconnected clients from the set
        for client in disconnected_clients:
            self.connected_clients.remove(client)
            logger.info(f"Removed disconnected client: {client}")



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
