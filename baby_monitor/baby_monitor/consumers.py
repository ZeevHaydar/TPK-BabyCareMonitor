import json
from channels.generic.websocket import AsyncWebsocketConsumers
import cv2

class VideoStreamConsumer(AsyncWebsocketConsumers):
    async def connect(self):
        await self.accept()

        # Open video capture device (replace 0 with the appropriate device index or video file path)
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to bytes
            _, buffer = cv2.imencode('.jpg', frame)
            jpeg_bytes = buffer.tobytes()

            # Send frame to client
            await self.send(jpeg_bytes, binary=True)

        # Release video capture device
        cap.release()

    async def disconnect(self, close_code):
        pass