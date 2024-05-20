# views.py
import json
import base64
import numpy as np
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import wave

def video_stream_view(request):
    return render(request, 'video_stream.html')



@csrf_exempt
def process_the_audio(request):
    """
    Memproses data audio yang dikirim melalui permintaan POST. Menangani data audio yang 
    dikodekan dalam base64 dan unggahan file WAV. Menggunakan model pembelajaran mesin untuk 
    membuat prediksi pada data audio tersebut.

    Args:
        request (HttpRequest): The HTTP request object.\n
        argumen JSON yang digunakan bisa berupa
        
            header: "Content-Type: application/json"\n
            body: 
            ```json
            {
                "base64": "your_base64_encoded_wav_data_here"
            }
            ```\n
        atau dengan file dengan mengirimnya method POST melalui form yang di dalamnya terdapat id "wav" yang berisi file .wav

    Returns:
        JsonResponse: Sebuah JSON response yang mengandung hasil prediksi atau pesan error.
    """
    if request.method == 'POST':
        if 'base64' in request.POST:
            try:
                data = json.loads(request.body)
                audio_data = base64.b64decode(data['base64'])
                audio_sequence = np.frombuffer(audio_data, dtype=np.int16)  # Assuming 16-bit PCM
                
                with wave.open(BytesIO(audio_data), 'rb') as wav:
                    audio_sequence = np.frombuffer(wav.readframes(wav.getnframes()), dtype=np.int16)
                
                # Predict the audio using machine learning
                prediction = predict_audio(audio_sequence)
                
                return JsonResponse({"prediction": prediction})
            except (json.JSONDecodeError, KeyError, base64.binascii.Error):
                return JsonResponse({"error": "Invalid base64 data"}, status=400)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        
        elif 'wav' in request.FILES:
            # Handle WAV file upload
            try:
                wav_file = request.FILES['wav']
                if not wav_file.name.lower().endswith('.wav'):
                    return JsonResponse({"error": "Invalid file extension, only .wav files are supported"}, status=400)

                with wave.open(BytesIO(wav_file.read()), 'rb') as wav:
                    audio_sequence = np.frombuffer(wav.readframes(wav.getnframes()), dtype=np.int16)
                
                # Predict the audio using machine learning
                prediction = predict_audio(audio_sequence)
                
                return JsonResponse({"prediction": prediction})
            except wave.Error:
                return JsonResponse({"error": "Invalid WAV file"}, status=400)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        
        else:
            return JsonResponse({"error": "Invalid request, no audio data found"}, status=400)
    
    return JsonResponse({"error": "Invalid HTTP method, only POST is allowed"}, status=405)

def predict_audio(audio_sequence):
    # Implement your ML model prediction here
    # This is a placeholder for your actual prediction logic
    # For demonstration, let's return a dummy prediction
    return "This is a dummy prediction"