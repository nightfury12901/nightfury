"""
Jarvis entry point.
Phase 1: wake word -> record -> transcribe -> speak back.
"""
import sys
import threading

from tray import start_tray_thread
from audio.wake_word import listen_for_wake_word
from audio.stt import record_and_transcribe
from audio.tts import speak
from brain.core import process_command

_stop_event = threading.Event()


def on_exit():
    print("Jarvis: shutting down.")
    _stop_event.set()
    sys.exit(0)


def on_wake():
    speak("Yes?")
    text = record_and_transcribe()
    if text:
        print(f"Jarvis heard: {text}")
        response = process_command(text)
        if response:
            speak(response)
    else:
        speak("I did not catch that.")


def assistant_loop():
    listen_for_wake_word(on_wake, _stop_event)


if __name__ == "__main__":
    start_tray_thread(on_exit)
    assistant_loop()
