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
    async def connect(self):
        await self.accept()
        self.cap = cv2.VideoCapture(0)
        self.send_camera_task = asyncio.create_task(self.send_camera_frames())

    async def disconnect(self, close_code):
        self.cap.release()
        self.send_camera_task.cancel()

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
        try:
            await self.accept()
            self.recorder = PvRecorder(device_index=-1, frame_length=512)
            
            self.recorder.start()
            # Mulai mengirimkan audio setiap 1 detik
            self.send_audio_task = asyncio.create_task(self.send_audio_frames())
        except Exception as e:
            print(e)

    async def disconnect(self, close_code):
        # Hentikan perekaman audio
        self.recorder.stop()
        self.send_audio_task.cancel()

    async def send_audio_frames(self):
        try:
            while True:
                audio = []
                start_time = time.time()
                # print("akan recording")
                
                while time.time() - start_time < 0.32:  # Capture audio for 1 real-time second
                    frame = await asyncio.to_thread(self.recorder.read)
                    audio.extend(frame)
                # print("finish record")
                print(audio[:32])

                audio = np.array(audio, dtype=np.int16)  # Assuming 16-bit PCM from PvRecorder
                audio = ((audio + 32768) // 256).astype(np.uint8) 
                # Convert audio to base64
                audio_data = base64.b64encode(bytes(audio)).decode('utf-8')

                # Send audio data to the client in JSON format
                await self.send(text_data=json.dumps({'audio': audio_data}))

        except asyncio.CancelledError:
            self.recorder.stop()
        except KeyboardInterrupt:
            self.recorder.stop()
        except Exception as e:
            print(f"Error in send_audio_frames: {e}")
