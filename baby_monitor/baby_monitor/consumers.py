import json
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2
import pickle
import base64
import asyncio

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Open video capture device (replace 0 with the appropriate device index or video file path)
        asyncio.create_task(self.send_camera_frames())

    async def disconnect(self, close_code):
        pass

    async def send_binary(self, data):
        await self.send(data)
    
    async def send_camera_frames(self):
        # Open video capture device (replace 0 with the appropriate device index or video file path)
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Show frame
            cv2.imshow('frame', frame)
            cv2.waitKey(1)  # Refresh window
            
            # Convert frame to bytes
            frame_data = pickle.dumps(frame)

            # Send frame to client
            await self.send_jpeg_frame(frame_data)

        # Release video capture device
        cap.release()

    async def send_jpeg_frame(self, frame_bytes):
        # Encode binary data as base64
        base64_data = base64.b64encode(frame_bytes).decode('utf-8')
        
        # Send base64 encoded data to the client
        await self.send(text_data=base64_data)