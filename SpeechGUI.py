import PySimpleGUI as sg
import cv2
from mic_vad_streaming import get_word

"""
GUI IMAGES
"""
voice_recording_img = cv2.imread("imgs/GUIs/start-recording.png")
voice_recording_img = cv2.resize(voice_recording_img, (320, 240), interpolation=cv2.INTER_AREA)


def voiceGUI():
    layout = [
        [sg.Text('Instrucciones', size=(15, 1), justification='left', font='Helvetica 10')],
        [sg.Text('Empieza a hablar', size=(15, 1), justification='left', font='Helvetica 10')],
        [sg.Image(key='image', data=cv2.imencode('.png', voice_recording_img)[1].tobytes())],
        [sg.Text('', size=(40, 1), justification='left', font='Helvetica 10', key='voice')],
        [
            sg.Button('Grabar', size=(10, 1), font='Helvetica 14'),
            sg.Button('Salir', size=(10, 1), font='Any 14'),
        ]
    ]
    # create the window and show it without the plot
    window = sg.Window('Controlador de voz',
                       layout, location=(500, 400))

    while True:
        event, values = window.read(timeout=10)
        if event == 'Salir' or event == sg.WIN_CLOSED:
            break

        elif event == "Grabar":
            text = get_word()
            window['voice'].update(f'Palabra reconocida: {text}')

    window.close()

