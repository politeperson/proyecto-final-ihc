import cv2
import numpy as np
import glob
import os


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
        dirname = os.path.dirname(__file__)
        print(dirname)
        # photos = glob.glob(os.path.join(dirname,"../imgs/calibration/*.jpg"))
        photos = glob.glob1('B:\\UCSP\\Interacción Humano Computador\\Proyecto_Final_IHC_2022_I\\ElDefinitivo\\imgs\\'
                            'calibration', '*.jpg')
        print(photos)
        for photo in photos:
            print(photo)
            img = cv2.imread(f'../imgs/calibration/{photo}')

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
