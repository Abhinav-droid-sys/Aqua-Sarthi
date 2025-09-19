# modules/voice_input.py
import speech_recognition as sr

def get_voice_query():
    """
    Uses local microphone (server-side) to record a short audio and transcribe using Google's recognizer.
    Works when Streamlit is run locally with microphone access.
    """
    recognizer = sr.Recognizer()
    try:
        mic = sr.Microphone()
    except Exception as e:
        return f"[voice error] Microphone not available: {e}"

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        # Inform user on console
        print("Listening... speak now")
        audio = recognizer.listen(source, phrase_time_limit=6)

    try:
        # language can be 'hi-IN' or 'en-IN' — Google will auto-detect if needed
        text = recognizer.recognize_google(audio, language="hi-IN")
        return text
    except sr.UnknownValueError:
        return "[voice error] Could not understand audio"
    except sr.RequestError as e:
        return f"[voice error] Recognition service error: {e}"
