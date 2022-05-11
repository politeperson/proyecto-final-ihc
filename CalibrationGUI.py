#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np
import glob

# from opencvAruco import calibrator

"""
Demo program that displays a webcam using OpenCV
"""


class Calibration():
    def __init__(self):
        self.tablero = (7, 7)  # tablero 8x8, se suma +1 para el borde
        self.frameSize = (720, 640)
        # Criterio
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30,
                         0.001)
        # Preparamos los puntos del tablero
        self.points_obj = np.zeros((self.tablero[0] * self.tablero[1], 3), np.float32)
        self.points_obj[:, :2] = np.mgrid[0:self.tablero[0], 0:self.tablero[1]].T.reshape(-1, 2)
        # Preparamos las listas para almacenar los puntos del mundo real y de la imagen
        self.points_3d = []
        self.points_img = []

    def calibrationCam(self):
        # photos = glob.glob(os.path.join(dirname,"../imgs/calibration/*.jpg"))
        photos = glob.glob('imgs/calibration/*.jpg')

        print(photos)
        for photo in photos:
            print(photo)
            img = cv2.imread(photo)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # buscamos las esquinas del tablero
            ret, corners = cv2.findChessboardCorners(gray, self.tablero, None)

            if ret == True:
                self.points_3d.append(self.points_obj)
                corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), self.criteria)
                self.points_img.append(corners)
                # cv2.drawChessboardCorners(img, self.tablero, corners2, ret)
                # cv2.imshow('IMG', img)

        # Calibración de la cámara
        try:
            ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(self.points_3d,
                                                                        self.points_img,
                                                                        self.frameSize,
                                                                        None, None)
        except:
            return None, None

        return cameraMatrix, dist


def calibration_window():
    sg.theme('DarkTeal9')

    # define the window layout
    layout = [
        [sg.Text('Calibrador', size=(40, 1), justification='center', font='Helvetica 20')],
        [sg.Text('Toma 6 fotos del tablero 8x8 en diferentes posiciones para calibrar la cámara.', size=(80, 1),
                 justification='left', font='Helvetica 10')],
        [sg.Image(filename='', key='image')],
        [
            sg.Button('Grabar', size=(10, 1), font='Helvetica 14'),
            sg.Button('Captura', size=(10, 1), font='Helvetica 14'),
            sg.Button('Parar', size=(10, 1), font='Any 14'),
            sg.Button('Salir', size=(10, 1), font='Helvetica 14'),
        ],
        [sg.Text(text="", key="log", size=(80, 1), justification='left',
                 font='Helvetica 10')],
    ]

    # create the window and show it without the plot
    window = sg.Window('Calibración de la cámara',
                       layout, location=(800, 400))

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(0)
    recording = False
    shot = False
    first_calibration = False
    counter_shots = 0
    cam_calibrator = Calibration()
    camera_calibrated = False

    while True:
        event, values = window.read(timeout=20)
        if event == 'Salir' or event == sg.WIN_CLOSED:
            break

        elif event == 'Grabar':
            recording = True

        elif event == "Captura":
            shot = True

        elif event == 'Parar':
            recording = False
            img = np.full((480, 640), 255)
            # this is faster, shorter and needs less includes
            img_bytes = cv2.imencode('.png', img)[1].tobytes()
            window['image'].update(data=img_bytes)

        if recording:
            ret, frame = cap.read()
            if counter_shots < 6 and shot:
                cv2.imwrite(f'imgs/calibration/calib_{counter_shots}.jpg', frame)
                counter_shots += 1
                shot = False
            elif counter_shots == 6 and not first_calibration:
                first_calibration = True
                window["log"].update("Tienes suficientes datos para calibrar la cámara")
                matrix, dist = cam_calibrator.calibrationCam()
                print(matrix, dist)

                np.savetxt("CamSettings/matrix.txt", matrix)
                np.savetxt("CamSettings/dist.txt", dist)

                if matrix is None or dist is None:
                    window['log'].update("La calibración falló, trate de tomar fotos de un tablero")
                else:
                    window['log'].update("Cámara calibrada correctamente :), ahora puede probar la siguiente GUI")

            img_bytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=img_bytes)

    window.close()
    cap.release()

