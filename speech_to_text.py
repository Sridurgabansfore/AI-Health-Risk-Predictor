import speech_recognition as sr

def get_voice_input():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=10)
        text = r.recognize_google(audio)
        return text
    except Exception as e:
        return f"Could not recognize voice: {str(e)}"
