import cv2
import numpy as np

# rotate a markers corners by rvec and translate by tvec if given
# input is the size of a marker.
# In the markerworld the 4 markercorners are at (x,y) = (+- markersize/2, +- markersize/2)
# returns the rotated and translated corners and the rotation matrix
def rotate_marker_corners(rvec, markersize, tvec = None):
    mhalf = markersize / 2.0
    # convert rot vector to rot matrix both do: markerworld -> cam-world
    mrv, jacobian = cv2.Rodrigues(rvec)

    #in markerworld the corners are all in the xy-plane so z is zero at first
    X = mhalf * mrv[:,0] #rotate the x = mhalf
    Y = mhalf * mrv[:,1] #rotate the y = mhalf
    minusX = X * (-1)
    minusY = Y * (-1)

    # calculate 4 corners of the marker in camworld. corners are enumerated clockwise
    markercorners = []
    markercorners.append(np.add(minusX, Y)) #was upper left in markerworld
    markercorners.append(np.add(X, Y)) #was upper right in markerworld
    markercorners.append(np.add( X, minusY)) #was lower right in markerworld
    markercorners.append(np.add(minusX, minusY)) #was lower left in markerworld
    # if tvec given, move all by tvec
    if tvec is not None:
        C = tvec #center of marker in camworld
        for i, mc in enumerate(markercorners):
            markercorners[i] = np.add(C,mc) #add tvec to each corner
    #print('Vec X, Y, C, dot(X,Y)', X,Y,C, np.dot(X,Y)) # just for debug
    markercorners = np.array(markercorners,dtype=np.float32) # type needed when used as input to cv2
    return markercorners, mrv




def paintMarker(frame, diccionario, parametros, matrix, dist):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detectamos los marcadores en la imagen
    # Camera matrix: Calibración de la imagen
    esquinas, ids, candidatos_malos = cv2.aruco.detectMarkers(gray, diccionario,
                                                              parameters=parametros,
                                                              cameraMatrix=matrix,
                                                              distCoeff=dist)
    try:
        # Si hay marcadores detectados por el marcador
        if np.all(ids != None):
            # Iterar en marcadores
            for i in range(0, len(ids)):
                # Estime la pose de cada marcador y devuelva los valores rvec y tvec
                # --- diferentes de los coeficientes de la camara
                rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(
                    esquinas[i], 0.02, matrix, dist)

                # el marcador aruco tiene tamaño 50 pixeles
                # marker_corners, mrv = rotate_marker_corners(rvec, 50)
                # print("Marker Corners: ", marker_corners)

                rVecStr = f"RVEC x:{round(rvec[i][0][0], 2)} y:{round(rvec[i][0][1], 2)} z:{round(rvec[i][0][2], 2)}"
                tVecStr = f"TVEC x:{round(tvec[i][0][0], 2)} y:{round(tvec[i][0][1], 2)} z:{round(tvec[i][0][2], 2)}"
                # print(rvec[0][0][0],rvec[0][0][1],rvec[0][0][2])
                cv2.putText(frame, rVecStr,
                            (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 225, 250), 2)
                cv2.putText(frame, tVecStr,
                            (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 225, 250), 2)

                # Eliminamos el error de la matriz de valores numpy
                (rvec - tvec).any()

                # Dibuja un cuadrado alrededor de los marcadores
                cv2.aruco.drawDetectedMarkers(frame, esquinas)

                # Dibujamos los ejes
                cv2.aruco.drawAxis(frame, matrix, dist, rvec, tvec, 0.01)

                # Coordenada X del centro del marcador
                c_x = (esquinas[i][0][0][0] + esquinas[i][0][1][0] +
                       esquinas[i][0][2][0] + esquinas[i][0][3][0]) / 4

                # Coordenada Y  del centro del marcador
                c_y = (esquinas[i][0][0][1] + esquinas[i][0][1][1] +
                       esquinas[i][0][2][1] + esquinas[i][0][3][1]) / 4

                # Mostramos el ID
                # cv2.putText(frame, 'ID' + str(ids[i]), (int(c_x), int(c_y)),
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50,225,250), 2)

                # Extraemos los puntos de las esquinas en coordenadas separadas
                c1 = (esquinas[0][0][0][0], esquinas[0][0][0][1])
                c2 = (esquinas[0][0][1][0], esquinas[0][0][1][1])
                c3 = (esquinas[0][0][2][0], esquinas[0][0][2][1])
                c4 = (esquinas[0][0][3][0], esquinas[0][0][3][1])
                v1, v2 = c1[0], c1[1]
                v3, v4 = c2[0], c2[1]
                v5, v6 = c3[0], c3[1]
                v7, v8 = c4[0], c4[1]

                # dibujamos una pirámide
                # Cara inferior
                # cv2.line(frame, (int(v1), int(v2)), (int(v3), int(v4)), (255, 0, 255), 3)
                # cv2.line(frame, (int(v5), int(v6)), (int(v7), int(v8)), (255, 0, 0), 3)
                # cv2.line(frame, (int(v1), int(v2)), (int(v7), int(v8)), (0, 0, 255), 3)
                # cv2.line(frame, (int(v3), int(v4)), (int(v5), int(v6)), (0, 255, 0), 3)

                # Esquinas
                # cex1, cey1 = (v1 + v5) // 2, (v2 + v6) // 2
                # cex2, cey2 = (v3 + v7) // 2, (v4 + v8) // 2
                # cv2.line(frame, (int(v1), int(v2)), (int(cex1), int(cey1 - 200)),
                #          (255, 0, 255), 3)
                # cv2.line(frame, (int(v5), int(v6)), (int(cex1), int(cey1 - 200)),
                #          (255, 0, 255), 3)
                # cv2.line(frame, (int(v3), int(v4)), (int(cex1), int(cey1 - 200)),
                #          (255, 0, 255), 3)
                # cv2.line(frame, (int(v7), int(v8)), (int(cex1), int(cey1 - 200)),
                #          (255, 0, 255), 3)
    except:
        if ids is None or len(ids) == 0:
            print("***************** Marker Detection Failed ************************")

    # fliping the frame to avoid reversed capture on camera
    # frame = cv2.flip(frame, 1)

    if esquinas != ():
        return frame, esquinas[0][0]
    return frame, ()