"""
Speech-to-text: records audio and transcribes it instantly with Groq's whisper-large-v3.
"""
import numpy as np
import sounddevice as sd
import queue
import wave
import os
import tempfile
from groq import Groq
from config import GROQ_API_KEY

def record_and_transcribe(samplerate=16000):
    print("Jarvis: listening...")
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        q.put(indata.copy())

    audio_data = []
    # Tunable threshold for silence detection
    SILENCE_THRESHOLD = 0.02
    chunk_duration = 0.1
    max_silence_chunks = int(1.5 / chunk_duration)
    silence_chunks = 0
    has_spoken = False
    
    with sd.InputStream(
        samplerate=samplerate,
        channels=1,
        dtype='int16',  # Groq expects standard audio formats like int16 wav
        blocksize=int(samplerate * chunk_duration),
        callback=callback
    ):
        max_chunks = int(15 / chunk_duration)
        for _ in range(max_chunks):
            chunk = q.get()
            audio_data.append(chunk)
            
            # Simple volume calculation
            volume = np.max(np.abs(chunk)) / 32768.0
            
            if volume > SILENCE_THRESHOLD:
                has_spoken = True
                silence_chunks = 0
            else:
                if has_spoken:
                    silence_chunks += 1
                    
            if has_spoken and silence_chunks > max_silence_chunks:
                break

    audio = np.concatenate(audio_data)

    # Save to a temporary WAV file for Groq
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    with wave.open(temp_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())

    print("Jarvis: thinking...")
    try:
        client = Groq(api_key=GROQ_API_KEY)
        with open(temp_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_path, file.read()),
                model="whisper-large-v3",
                prompt="Transcribe english. Pay special attention to names and email addresses.",
            )
        text = transcription.text.strip()
    except Exception as e:
        print(f"STT Error: {e}")
        text = ""
    finally:
        try:
            os.remove(temp_path)
        except:
            pass

    return text

