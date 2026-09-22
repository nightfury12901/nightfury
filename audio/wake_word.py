"""
Wake word detection using openWakeWord.
Listens continuously on the default microphone and calls on_wake() each time
the configured wake word is heard.
"""
import numpy as np
import openwakeword
from openwakeword.model import Model
import sounddevice as sd

from config import WAKE_WORD

# Download models on first run if needed
openwakeword.utils.download_models()

def listen_for_wake_word(on_wake, stop_event):
    print(f"Jarvis: initializing wake word model for '{WAKE_WORD}'...")
    
    try:
        owwModel = Model(wakeword_models=[WAKE_WORD], inference_framework="onnx")
    except Exception as e:
        print(f"Error initializing openWakeWord: {e}")
        return

    # openWakeWord typically expects 16kHz audio, 16-bit PCM (which we provide via sounddevice)
    FORMAT = "int16"
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280

    audio_buffer = np.zeros(CHUNK, dtype=np.int16)

    def _callback(indata, frames, time_info, status):
        # We ignore input overflow statuses because when Jarvis is thinking/talking,
        # the buffer naturally fills up.
        audio_chunk = np.frombuffer(indata, dtype=np.int16)
        
        # Feed the audio to openWakeWord
        prediction = owwModel.predict(audio_chunk)
        
        # Check if the score is above the threshold
        # prediction is a dict: {'hey_jarvis': 0.123}
        for mdl in owwModel.prediction_buffer.keys():
            # You can tune this threshold between 0.0 and 1.0
            if prediction[mdl] > 0.5:
                # To prevent multiple consecutive triggers, we can reset or just call it
                owwModel.reset()
                on_wake()

    with sd.InputStream(
        samplerate=RATE,
        blocksize=CHUNK,
        dtype=FORMAT,
        channels=CHANNELS,
        callback=_callback,
    ):
        print(f"Jarvis: listening for wake word '{WAKE_WORD}'...")
        while not stop_event.is_set():
            sd.sleep(100)

