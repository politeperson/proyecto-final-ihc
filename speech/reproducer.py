# IMPORTAMOS RECURSOS NECESARIOS.
import pyaudio
import wave


def reproduce_sound(path2file):
    chunk = 1024

    # ABRIMOS UBICACIÓN DEL AUDIO.
    f = wave.open(path2file, "rb")

    # INICIAMOS PyAudio.
    p = pyaudio.PyAudio()

    # ABRIMOS STREAM
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)

    # LEEMOS INFORMACIÓN
    data = f.readframes(chunk)

    # REPRODUCIMOS "stream"
    while data:
        stream.write(data)
        data = f.readframes(chunk)

    # PARAMOS "stream".
    stream.stop_stream()
    stream.close()

    # FINALIZAMOS PyAudio
    p.terminate()
