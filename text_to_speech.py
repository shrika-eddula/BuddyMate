import gtts
from playsound import playsound
from gtts import gTTS
from io import BytesIO


def Speak(text):
    # Generate the speech audio and store it in mp3_fp
    mp3_fp = BytesIO()
    #intro = "Greetings, this is a United States Army device, my purpose is to assess your injury and report back to my home base, and then proceed with further instructions."
    tts = gTTS(text, lang='en')
    tts.write_to_fp(mp3_fp)

    # Save the speech audio to a temporary file
    mp3_fp.seek(0)
    with open('temp.mp3', 'wb') as f:
        f.write(mp3_fp.read())

    # Play the audio using playsound
    playsound('temp.mp3')
