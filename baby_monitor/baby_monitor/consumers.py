import json
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2
import pickle
import base64
import sounddevice as sd
import asyncio

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.cap = cv2.VideoCapture(0)
        asyncio.create_task(self.send_camera_frames())

    async def disconnect(self, close_code):
        self.cap.release()

    async def send_camera_frames(self):
        cap = cv2.VideoCapture(0)
        try:
             while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                _, encoded_frame = cv2.imencode('.jpg', frame)

                # Convert the encoded frame to base64
                base64_frame = base64.b64encode(encoded_frame).decode('utf-8')

                await self.send_json_frame(base64_frame)
                await asyncio.sleep(0.0166666) 
        except asyncio.CancelledError:
            cap.release()
        except Exception as e:
            print(f"Error in send_camera_frames: {e}")
            cap.release()
    async def send_json_frame(self, frame_data):
        await self.send(text_data=json.dumps({'video': frame_data}))


class AudioStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        asyncio.create_task(self.send_audio_frames())

    async def disconnect(self, close_code):
        pass

    async def send_audio_frames(self):
        sample_rate = 44100
        channels = 1
        block_size = 1024

        def audio_callback(indata, frames, time, status):
            audio_data = indata.tobytes()
            base64_data = base64.b64encode(audio_data).decode('utf-8')
            asyncio.run_coroutine_threadsafe(self.send_audio_data(base64_data), asyncio.get_event_loop())

        with sd.InputStream(samplerate=sample_rate, channels=channels, blocksize=block_size, callback=audio_callback):
            while True:
                await asyncio.sleep(0.1)

    async def send_audio_data(self, audio_data):
        await self.send(text_data=json.dumps({'audio': audio_data}))
