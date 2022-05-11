import mouse
import speech_recognition as sr
import threading
import pyautogui

def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        # recognizer.pause_threshold = 1
        # recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio, language="es-PE")
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

import speech_recognition as sr
def voice_listener(text):
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
    recognizer.pause_threshold = 0.5
    microphone = sr.Microphone()
    # locker = threading.Lock()
    while True:
        guess = recognize_speech_from_mic(recognizer, microphone)
        if guess["transcription"]:
            text = guess["transcription"].lower()
            print("You said: ", text)
            if "click" in text:
                print("left click pressed")
                mouse.click('left')
        if not guess["success"]:
            # there was an error
            print("ERROR: {}".format(guess["error"]))
