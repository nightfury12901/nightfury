"""
Text-to-speech using pyttsx3 (offline, uses installed Windows SAPI voices).
"""
import pyttsx3

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate", 175)
    return _engine


def speak(text):
    print(f"Jarvis says: {text}")
    engine = _get_engine()
    engine.say(text)
    engine.runAndWait()
