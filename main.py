#!/usr/bin/env python
import asyncio
import threading
import PySimpleGUI as sg
import cv2
import numpy as np
import mouse
import pyautogui
import CalibrationGUI
import SpeechGUI
import mic_vad_streaming
from speech.reproducer import reproduce_sound
from opencvAruco import detectMarkers

"""
ARUCO CONDIFUGRATIONS
"""
matrix = np.loadtxt('CamSettings/matrix.txt')
dist = np.loadtxt('CamSettings/dist.txt')

# DETECTOR ARUCO
# Inicializamos los parámetros del detector de arucos
parametros = cv2.aruco.DetectorParameters_create()

# Cargamos el diccionario de nuestro Aruco
diccionario = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)



"""
GUI IMAGES
"""
hello_run_img = cv2.imread('imgs/GUIs/hello_run.PNG')
hello_run_img = cv2.resize(hello_run_img, (512, 384), interpolation=cv2.INTER_AREA)

voice_recording_img = cv2.imread("imgs/GUIs/start-recording.png")
voice_recording_img = cv2.resize(voice_recording_img, (320, 240), interpolation=cv2.INTER_AREA)

voice_no_recording_img = cv2.imread("imgs/GUIs/stop-recording.png")
voice_no_recording_img = cv2.resize(voice_no_recording_img, (320, 240), interpolation=cv2.INTER_AREA)

no_recording_img = cv2.imread("imgs/GUIs/no_rec.png")
no_recording_img = cv2.resize(no_recording_img, (640, 480), interpolation=cv2.INTER_AREA)


"""
COLUMN LAYERS
"""
col1 = [
    [sg.Text('Instrucciones', size=(15,1), justification='left', font='Helvetica 10')],
    [sg.Button('Calibrador', size=(10, 1), font='Helvetica 14')],
    [sg.Button('Aruco', size=(10, 1), font='Helvetica 14')],
    [sg.Button('Hablar', size=(10, 1), font='Helvetica 14')],
    [sg.Button('Juego', size=(10, 1), font='Helvetica 14')],
    [sg.Button('Salir', size=(10, 1), font='Helvetica 14')],
]

col2 = [
    [sg.Multiline('Pasos básicos a seguir, clic en los diferentes botones: \n'
             '1) Calibrar la cámara [botón: Calibrador]\n'
             '2) Detección de marcadores Aruco [botón: Aruco]\n'
             '3) Probar la detección de voz [botón: Hablar]\n'
             '4) Probar el juego demo [botón: Juego].',
             size=(50, 7), justification='left', font='Helvetica 10', key='simple_instruction')],
    [sg.Image(key='image')],
    [
        sg.Button('Grabar', size=(10, 1), font='Helvetica 14'),
        sg.Button('Detener', size=(10, 1), font='Any 14'),
    ],
    [sg.Text('', size=(40, 1), justification='left', font='Helvetica 10', key='Logs')],
]


def main():
    sg.theme('DarkTeal9')

    layout = [
        [
            sg.Column(col1, element_justification='c'),
            sg.Column(col2, element_justification='c'),
        ]
    ]

    # create the window and show it without the plot
    window = sg.Window('Controlador del Sistema',
                       layout, location=(500, 400))

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(0)
    aruco_mode = False
    speech_mode = False
    aruco_and_speech_mode = False

    recording_cam = False
    recording_voice = False


    #thread_voice = threading.Thread(target=voice_recognizer.voice_listener, args=(text_from_voice,),
    #                                daemon=True)

    #thread_voice.start()

    scr_width, scr_height = pyautogui.size()
    first_time = False

    while True:
        event, values = window.read(timeout=10)
        if event == 'Salir' or event == sg.WIN_CLOSED:
            break

        elif event == "Calibrador":
            aruco_mode = False
            speech_mode = False
            recording_cam = False
            recording_voice = False
            CalibrationGUI.calibration_window()

        elif event == "Aruco":
            aruco_mode = True
            speech_mode = False
            recording_cam = True
            recording_voice = False
            window['simple_instruction'].update("Muestra un marcador Aruco de tamaño 5x5.")

        elif event == 'Hablar':
            aruco_mode = False
            speech_mode = False
            recording_cam = False
            recording_voice = False
            reproduce_sound('audio/mixkit-long-pop-2358.wav')
            SpeechGUI.voiceGUI()
            # aruco_mode = False
            # speech_mode = True
            # recording_cam = False
            # recording_voice = True
            #
            # # Reproduciendo el sonido cuando se hace click
            # window['simple_instruction'].update("Empieza a hablar")
            #
            # imgbytes = cv2.imencode('.png', voice_recording_img)[1].tobytes() # ditto
            # window['image'].update(data=imgbytes)

        elif event == "Juego":
            recording_voice = False
            aruco_mode = False
            speech_mode = False
            recording_cam = True


            imgbytes = cv2.imencode('.png', hello_run_img)[1].tobytes()
            window['image'].update(data=imgbytes)

            window['simple_instruction'].update(
                "Accede al juego desde el siguiente enlace:\n"
                "https://helloenjoy.itch.io/hellorun\n"
                "Muestra tu marcador para guiar el mouse")

            if not first_time:
                print("print first time")
                threading.Thread(target=mic_vad_streaming.continuous_speeching, args=(), daemon=True)
                first_time = True

        elif event == 'Grabar':
            if aruco_mode:
                recording_cam = True
            elif speech_mode:
                recording_voice = True
                img_bytes = cv2.imencode('.png', voice_recording_img)[1].tobytes()  # ditto
                window['image'].update(data=img_bytes)

        elif event == 'Detener':
            if aruco_mode:
                recording_cam = False
                imgbytes = cv2.imencode('.png', no_recording_img)[1].tobytes()
                window['image'].update(data=imgbytes)
            elif speech_mode:
                recording_voice = False
                imgbytes = cv2.imencode('.png', voice_no_recording_img)[1].tobytes()
                window['image'].update(data=imgbytes)

        if recording_cam:
            ret, frame = cap.read()

            frame_width = frame.shape[1]
            frame_height = frame.shape[0]

            aruco_detected, corners = detectMarkers.paintMarker(frame, diccionario, parametros, matrix, dist)

            if len(corners) != 0:
                center_aruco = np.sum(corners, axis=0) // 4

                m_width = scr_width / frame_width
                m_height = scr_height / frame_height

                tr_pos = np.array((m_width * center_aruco[0], m_height * center_aruco[1]))
                curr_pos = np.array(mouse.get_position())

                offset = tr_pos - curr_pos

                mouse.move(offset[0], offset[1], absolute=False, duration=0)

            img_bytes = cv2.imencode('.png', aruco_detected)[1].tobytes()  # ditto
            window['image'].update(data=img_bytes)

        # if recording_voice:
        #     text = asyncio.run(get_word())
        #     print("Detected: ", text)
        #     if "hello" in text:
        #         reproduce_sound('audio/mixkit-long-pop-2358.wav')

    window.close()
    cap.release()


main()


"""
Observaciones: falta voz
Interfaz interactiva: utilizable
Errores: mucho tiempo para aprender la tecnología a emplearse
no está mal la idea, se logró completar la interfaz
detectar la cámara
tengo el escenario
el tiempo real y el lenguaje de programación es lento
en teoría nadie llegó al punto donde el profesor quería
en la virtualidad se avanzaba mejor comparado a este semestre híbrido

Recomendación general: hacer un informe detallado del trabajo final, hacer un informe bien detallado y consistente
dependendiendo de los informes, este ayuda a reforzar la nota que se ha obtenido.

si el usuario no se tiene micrófono ni cámara advertirle al usuario y no dejarle jugar.

Cuestionario teórico: 3 papers y un capítulo del libro, preguntas.
"""