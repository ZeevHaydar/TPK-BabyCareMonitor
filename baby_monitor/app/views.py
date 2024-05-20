# views.py
import json
import base64
import numpy as np
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import wave
import re
import tensorflow as tf
import tensorflow_io as tfio
import traceback
import os

dirname = os.path.dirname(__file__)
saved_model_path = os.path.join(dirname, './../baby_cry_detection_model')
model = tf.saved_model.load(saved_model_path)

def video_stream_view(request):
    return render(request, 'video_stream.html')


@csrf_exempt
def process_the_audio(request):
    """
    Memproses data audio yang dikirim melalui permintaan POST. Menangani data audio yang 
    dikodekan dalam base64 dan unggahan file WAV. Menggunakan model pembelajaran mesin untuk 
    membuat prediksi pada data audio tersebut.

    Args:
    \trequest (HttpRequest): The HTTP request object.\n
    \targumen JSON yang digunakan bisa berupa
    
    \t    header: "Content-Type: application/json"\n
    \t    body: 
    \t      ```json
                {"base64": "your_base64_encoded_wav_data_here [format Data URI]"}
    ```

    atau dengan file dengan mengirimnya method POST melalui form yang di dalamnya 
    terdapat id "wav" yang berisi file .wav dan memiliki enctype="multipart/form-data".\n

    Returns:
            JsonResponse: Sebuah JSON response yang mengandung hasil prediksi atau pesan error.
    """
    if request.method == 'POST':
        try:
            if 'wav' in request.FILES:
                try:
                    wav_file = request.FILES['wav']
                    print(wav_file.name)
                    if not wav_file.name.lower().endswith('.wav'):
                        return JsonResponse({"error": "Invalid file extension, only .wav files are supported"}, status=400)

                    # Decode the WAV file and resample to 16 kHz
                    # file_contents = tf.io.read_file(wav_file)
                    file_contents = wav_file.read()
                    wav = resample_wav_data(file_contents)

                    # Predict the audio using machine learning
                    prediction, audio_duration = predict_audio(wav)
                    
                    return JsonResponse({"prediction": prediction, "audio_duration": audio_duration})
                except wave.Error:
                    return JsonResponse({"error": "Invalid WAV file"}, status=400)
                except Exception as e:
                    traceback_str = traceback.format_exc()

                    # Return JsonResponse with error message and stack trace
                    return JsonResponse({"error": str(e), "traceback": traceback_str}, status=500)
            
            elif 'b64' in json.loads(request.body.decode('utf-8')):
                try:
                    data = json.loads(request.body)
                    base64_data = data['b64']

                    # Check if the base64 data is in Data URI format
                    if not re.match(r'data:audio/wav;base64,', base64_data):
                        return JsonResponse({"error": "Invalid base64 data, must be in Data URI format"}, status=400)

                    # Extract the base64 encoded part after the Data URI prefix
                    audio_data = base64.b64decode(base64_data.split(',')[1])
                    wav = resample_wav_data(audio_data)

                    # Predict the audio using machine learning
                    prediction, audio_duration = predict_audio(wav)
                    
                    return JsonResponse({"prediction": prediction, "audio_duration": audio_duration})
                except (json.JSONDecodeError, KeyError, base64.binascii.Error):
                    return JsonResponse({"error": "Invalid base64 data"}, status=400)
                except Exception as e:
                    traceback_str = traceback.format_exc()

                    # Return JsonResponse with error message and stack trace
                    return JsonResponse({"error": str(e), "traceback": traceback_str}, status=500)
        
            else:
                return JsonResponse({"error": "Invalid request, no audio data found"}, status=400)
        except Exception as e:
            # Get the stack trace as a string
            traceback_str = traceback.format_exc()

            # Return JsonResponse with error message and stack trace
            return JsonResponse({"error": str(e), "traceback": traceback_str}, status=500)
    
    return JsonResponse({"error": "Invalid HTTP method, only POST is allowed"}, status=405)

def predict_audio(waveform, sampling_rate=16000):
    """
    Prediksi audio menggunakan YamNET yang dilakukan transfer learning agar hanya mendeteksi 
    suara tangisan bayi. Fungsi akan menerima data waveform yang sudah diresample dengan 
    sampling rate 16000 Hz dan berbentuk 1-dimensional.
    """
    result_class = ['Yes', 'No']
    results = model(waveform)
    prediction = result_class[tf.math.argmax(results)]
    num_samples = tf.shape(waveform)[0]
    duration = tf.cast(num_samples, dtype=tf.float32) / tf.cast(sampling_rate, dtype=tf.float32)
    return prediction, float(duration.numpy())

@tf.function
def resample_wav_data(file_contents):
    """ Get audio data, convert it to a float tensor, resample to 16 kHz single-channel audio. """
    wav, sample_rate = tf.audio.decode_wav(
          file_contents,
          desired_channels=1)
    print(wav)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav