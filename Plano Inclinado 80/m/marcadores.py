# *************************************
#
# Clase: --> Marcadores 
# Modulo: -> marcadores.py
# Ubicacion -> m.marcadores
#
# Descripción:
#   Calcula la distancia entre los centros
#   de dos marcadores
#
# Fecha:
#   diciembre 29/2021
#
# ************************************

import numpy as np
#from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import imutils
import cv2

global angulo
global D
global plano_inclinado
global recta

class Marcadores:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,rangoColor,longitud_plano):
        print("----------------------------")
        print(" CONSTRUCTOR: Marcadores")
        print("----------------------------")
        self.colorLower = rangoColor[0]
        self.colorUpper = rangoColor[1]
        self.longitud_plano = longitud_plano
        self.calibrar = 0

    def midpoint(self, ptA, ptB):
            return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

    def distancia_entre_marcadores(self,frame,hsv):
        #print("-------------------------------------")
        #print(" CLASE: Marcadores")
        #print(" distancia_entre_marcadores")
        #print("--------------------------------------")
        # --- Mascara para detección delcolor ---
        mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
        # --- Dilatacion y erosion para limpiar contorno de canica ---
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # ----------------------------------------------------
        # Encuentra el contorno de la máscara (esfera) e
        # inicializa las coordenadas (x,y) del centro de
        #                 de la canica
        # ----------------------------------------------------
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        (cnts, _) = contours.sort_contours(cnts)
        
        self.colors = ((0, 0, 255), (240, 0, 159), (0, 165, 255), (255, 255, 0),
                (255, 255, 255)) # (255, 0, 0)
        refObj = None
        # Referencia: Diametro de un centavo de dolar: 0.955in
        ref = 3.00 # cm
        pixelsPerMetric = None

        # loop over the contours individually
        for c in cnts:
                # if the contour is not sufficiently large, ignore it
                if cv2.contourArea(c) < 2:
                        continue
                # compute the rotated bounding box of the contour
                box = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                # order the points in the contour such that they appear
                # in top-left, top-right, bottom-right, and bottom-left
                # order, then draw the outline of the rotated bounding
                # box
                box = perspective.order_points(box)
                # compute the center of the bounding box
                cX = np.average(box[:, 0])
                cY = np.average(box[:, 1])

                # if this is the first contour we are examining (i.e.,
                # the left-most contour), we presume this is the
                # reference object
                if refObj is None:
                        # unpack the ordered bounding box, then compute the
                        # midpoint between the top-left and top-right points,
                        # followed by the midpoint between the top-right and
                        # bottom-right
                        (tl, tr, br, bl) = box
                        (tlblX, tlblY) = self.midpoint(tl, bl)
                        (trbrX, trbrY) = self.midpoint(tr, br)
                        # compute the Euclidean distance between the midpoints,
                        # then construct the reference object
                        dX = tlblX - trbrX
                        dY = tlblY - trbrY
                        D = round(np.sqrt(dX*dX + dY*dY),1)
                        #D = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
                        #refObj = (box, (cX, cY), D / args["width"])
                        refObj = (box, (cX, cY), D / ref)
                        continue

        # draw the contours on the image
        # stack the reference coordinates and the object coordinates
        # to include the object center
        self.refCoords = np.vstack([refObj[0], refObj[1]])
        self.objCoords = np.vstack([box, (cX, cY)])

    def calibrar_plano_horizontal(self,frame):
        # --------------------------------------------------------------------------
        #      Comprueba que el plano inclinado se encuentre a CERO GRADOS
        #   Comprueba que la camara WEB se encuentre alineada HORIZONTALMENTE
        # --------------------------------------------------------------------------
        # --- Marcador "A" <- izquierda ---
        (xA, yA) = self.refCoords[4]
        # --- Marcador "B" <- derecha ---
        (xB, yB) = self.objCoords[4]
        # --- CALIBRACION ---
        # --- Comprueba que el plano inicializa con angulo = 0 grados y
        #     la camara WEB se encuentra totalmente HORIZONTAL
        # -------------------------------------------------------------
        dy = np.absolute(yB - yA)
        if dy > 2:
            print("CALIBRAR !!")
            # --- Calibrar el Plano Inclinado en angulo CERO GRADOS ---
            cv2.putText(frame, "*** ! CALIBRAR *** dy = "+str(dy), (int(mX), int(mY - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
            return False
        else:
            return True
        
    def dibujar_linea_horizontal(self,frame):
        # --------------------------------------------------------------------------
        # Dibuja una linea entre el centro del Objeto de Referencia "refCoords[4]"
        # y el centro del Objeto Siguiente "objCoords[4]"
        # --------------------------------------------------------------------------
        # --- Marcador "A" <- izquierda ---
        (xA, yA) = self.refCoords[4]
        # --- Marcador "B" <- derecha ---
        (xB, yB) = self.objCoords[4]
        # --- Punto medio entre los puntos "A" y "B" ---
        (mX, mY) = self.midpoint((xA, yA), (xB, yB))
        # --- Color de a linea entre "A" y "B" ---
        color = self.colors[4]
        # --- Punto "A" ---
        cv2.circle(frame, (int(xA), int(yA)), 5, color, -1)
        # --- Punto "B" ---
        cv2.circle(frame, (int(xB), int(yB)), 5, color, -1)
        # --- Linea de Hipotenusa "D" ---
        cv2.line(frame, (int(xA), int(yA)), (int(xB), int(yB)), color, 2)

        cv2.putText(frame, "{:.1f} cm".format(self.longitud_plano), (int(mX), int(mY - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
            
    def calibrar_angulo_cero(self):
        return self.calibrar

    def dibujar_triangulo_rectangulo(self,frame):
        
        global angulo
        global D
        global plano_inclinado
        global recta
        
        # --------------------------------------------------------------------------
        # Dibuja un Triangulo Rectangulo que representa el Plano Inclinado
        # --------------------------------------------------------------------------
        # --- Marcador "A" <- izquierda ---
        (xA, yA) = self.refCoords[4]
        # --- Marcador "B" <- derecha ---
        (xB, yB) = self.objCoords[4]
        # --- Punto medio entre los puntos "A" y "B" ---
        (mX, mY) = self.midpoint((xA, yA), (xB, yB))
        # --- Color de a linea entre "A" y "B" ---
        color = self.colors[4]

        # ----------------------------------------------------
        #     D = Distancia entre "A" y "B" <- Hipotenusa
        # ----------------------------------------------------
        dx = xA - xB
        dy = yA - yB
        # --- REFERENCIA: "D" en pixeles ---
        # --- Longitud del plano inclinado en pixeles ---
        D = round(np.sqrt(dx*dx + dy*dy),1)

        # ----------------------------------------------------
        #     a = Ancho de la base del triangulo rectangulo
        # ----------------------------------------------------
        dx = xA - xB
        dy = yB - yB
        # --- Punto medio de la base del triangulo ---
        (amX, amY) = self.midpoint((xA, yB), (xB, yB))
        # --- REFERENCIA: "a" en pixeles --- 
        a = round(np.sqrt(dx*dx + dy*dy),1)     
        # --- REFERENCIA: Ancho de la base del triangulo en cm ---
        coordX_text_angulo = xB - a*0.25
        if D != 0:
            a = round(a*self.longitud_plano/D,1) # <- cm
        
        # ----------------------------------------------------
        #     h = Altura del triangulo rectangulo
        # ----------------------------------------------------
        dx = xA - xA
        dy = yB - yA
        # --- Punto medio de la altura del triangulo ---
        (hmX, hmY) = self.midpoint((xA, yB), (xA, yA))
        # --- REFERENCIA: "h" en pixeles ---
        h = round(np.sqrt(dx*dx + dy*dy),1)
        # --- REFERENCIA: Altura del triangulo en cm ---
        coordY_text_angulo = yB - 10
        if D != 0:
            h = round(h*self.longitud_plano/D,1)

        # ----------------------------------------------------
        #            VERTICES del triangulo
        # ---------------------------------------------------- 
        # --- Punto "A" ---
        cv2.circle(frame, (int(xA), int(yA)), 5, color, -1)
        # --- Punto "B" ---
        cv2.circle(frame, (int(xB), int(yB)), 5, color, -1)
        # --- Punto "C" (vertice superior del trinagulo ---
        cv2.circle(frame, (int(xA), int(yB)), 5, color, -1)

        # ----------------------------------------------------
        #      Linea de la HIPOTENUSA "D"
        # ----------------------------------------------------
        cv2.line(frame, (int(xA), int(yA)), (int(xB), int(yB)), color, 2)
        # ----------------------------------------------------
        #      Linea de la BASE "a"
        # ----------------------------------------------------
        cv2.line(frame, (int(xA), int(yB)), (int(xB), int(yB)), color, 2)
        # ----------------------------------------------------
        #      Linea de la ALTURA "h"
        # ----------------------------------------------------
        cv2.line(frame, (int(xA), int(yB)), (int(xA), int(yA)), color, 2)

        
        # ----------------------------------------------------
        # Acotación de la HIPOTENUSA "D" [PLANO INCLINADO]
        # ----------------------------------------------------
        # --- En "cm" ---
        cv2.putText(frame, "{:.1f} cm".format(self.longitud_plano), (int(mX), int(mY - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        # --- En "pixeles" ---
        #cv2.putText(frame, str(D)+" pix", (int(mX), int(mY + 10)),
        #        cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        # ----------------------------------------------------
        # Acotación de la BASE "a" 
        # ----------------------------------------------------
        cv2.putText(frame, str(a)+" cm", (int(amX), int(amY + 25)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        # ----------------------------------------------------
        # Acotación de la ALTURA "h" 
        # ----------------------------------------------------
        cv2.putText(frame, str(h)+" cm", (int(hmX + 5), int(hmY)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        # ----------------------------------------------------------
        #            Calculo del ANGULO del Plano Inclinado
        # ----------------------------------------------------------
        # PLANO INCLINADO:   0      0 <- Punto "0"
        #                     \     1 <- Punto "1"
        #                      \    2 <- Punto "2"
        #                    2--1
        # ----------------------------------------------------------

        if D == 0:
            sin_angulo = 0
            angulo = 0
        else:
            sin_angulo = h/self.longitud_plano
            angulo = np.arcsin(sin_angulo)* 180 / np.pi  # Angulo en grados
            angulo = round(angulo,2)  

        # --- Punto medio de la base del triangulo ---
        (aqX, aqY) = self.midpoint((xA, yB), (xB, yB))

        # --- Angulo del Plano Inclinado ---
        cv2.putText(frame, str(angulo)+" grados", (int(coordX_text_angulo), int(coordY_text_angulo)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        # --- Plano Inclinado ---
        plano_inclinado = (D, angulo)

        # --- Ecuacion: y = mx + b
        m = h/a
        b = yA - m*xA
        recta = (m, b)

    @property
    def angulo(self):
        return angulo

    @property
    def D(self):
        return D # <- Distancia en pixeles que equivale a 38.0 cm

    @property
    def plano_inclinado(self):
        return plano_inclinado

    @property
    def recta(self):
        return recta
