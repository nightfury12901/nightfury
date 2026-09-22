"""
Speech-to-text: records a few seconds of audio after the wake word fires
and transcribes it with faster-whisper (runs fully offline on CPU).
"""
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

_model = None


def _get_model():
    global _model
    if _model is None:
        # "base" is a good speed/accuracy balance on CPU.
        # Bump to "small" or "medium" if you have a GPU and want more accuracy.
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def record_and_transcribe(samplerate=16000):
    print("Jarvis: listening...")
    import queue
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        q.put(indata.copy())

    audio_data = []
    # Tunable threshold for silence detection
    SILENCE_THRESHOLD = 0.02
    # 0.1 seconds per chunk
    chunk_duration = 0.1
    max_silence_chunks = int(1.5 / chunk_duration)
    silence_chunks = 0
    has_spoken = False
    
    with sd.InputStream(
        samplerate=samplerate,
        channels=1,
        dtype='float32',
        blocksize=int(samplerate * chunk_duration),
        callback=callback
    ):
        # Hard limit of 15 seconds so it doesn't get stuck forever
        max_chunks = int(15 / chunk_duration)
        for _ in range(max_chunks):
            chunk = q.get()
            audio_data.append(chunk)
            
            # Simple volume calculation
            volume = np.max(np.abs(chunk))
            
            if volume > SILENCE_THRESHOLD:
                has_spoken = True
                silence_chunks = 0
            else:
                if has_spoken:
                    silence_chunks += 1
                    
            # Stop if we detected speech and then silence for 1.5s
            if has_spoken and silence_chunks > max_silence_chunks:
                break

    audio = np.concatenate(audio_data)
    audio = np.squeeze(audio)

    model = _get_model()
    segments, _ = model.transcribe(audio, language="en", condition_on_previous_text=False)
    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip()
