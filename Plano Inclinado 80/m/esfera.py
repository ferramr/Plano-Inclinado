# *************************************
#
# Clase: --> Esfera
# Modulo: -> esfera.py
# Ubicacion -> m.esfera
#
# Descripción:
#   Reconocimiento y seguimiento de la ESFERA
#
# Fecha:
#   enero 18/2022
#
# ************************************

from collections import deque
import numpy as np
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import imutils
import cv2
import time

global muestras
global contador_muestras
global center

class Esfera:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,rangoColor):
        print("----------------------------")
        print(" CONSTRUCTOR: Esfera")
        print("----------------------------")

        global muestras
        global contador_muestras
        
        self.colorLower = rangoColor[0]
        self.colorUpper = rangoColor[1]
        # -----------------------------------------------------------------------
        # Diccionario de posicion de la esfera:
        # pos = {"xy":(x, y), "center":center}
        #        coordenadas      centro de
        #         posicion           masa
        #          esfera           esfera
        # -----------------------------------------------------------------------
        self.pos = {}
        # -----------------------------------------------------------------------
        # Definición de una "cola" (array) de dos posiciones para identificar el 
        # movimiento de la canica cuando las dos localidades presentan un valor 
        #       diferente en las coordenadas de posición de esta.
        # El arreglo "pos" registra las posiciones anterior y actual:
        #       pos[-1] <- Posicion ANTERIOR
        #       pos[0]  <- Posicion ACTUAL
        # -----------------------------------------------------------------------
        # --- Tamaño de la "cola" (array) "pts" ---
        self.buffer = 2
        self.pts = deque(maxlen=self.buffer)

        muestras = []
        contador_muestras = 0

    def midpoint(self, ptA, ptB):
            return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

    def seguir_trayectoria_esfera(self,frame,hsv):

        global center
        
        #print("-------------------------------------")
        #print(" CLASE: Movil")
        #print(" seguimiento")
        #print("--------------------------------------")
        # --- Mascara para detección delcolor ---
        mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
        # --- Dilatacion y erosion para limpiar contorno de canica ---
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        # ----------------------------------------------------
        # Encuentra el contorno de la máscara (canica) e
        # inicializa las coordenadas (x,y) del centro de
        #                 de la canica
        # ----------------------------------------------------
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)# --- Si localiza el contorno de la canica ---

        # --- Si localiza el contorno de la canica ---
        #   3 - "Inicializa Plano Inclinado con Angulo CERO"
        #   4 - "Posiciona Plano Inclinado con Angulo SOLICITADO"
        #   5 - "Libera Esfera"
        if (len(cnts) > 0):
                # -----------------------------------------------
                # Encuentra el contorno mas grande en la máscara
                # -----------------------------------------------
                c = max(cnts, key=cv2.contourArea)
                # -----------------------------------------------
                # Calcula el minimo circulo interior y su
                #       centroide (centro de masa)
                # -----------------------------------------------
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # --- Si la canica tiene un radio mínimo de:   ---
                if radius > 4:     # 10:
                    # ---------------------------------------------
                    # Dibuja el circulo amarillo alrededor de la
                    #                 canica
                    # ---------------------------------------------
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                            (0, 255, 255), 2)
                    # ---------------------------------------------
                    # Dibuja un punto rojo en el centro de la canica
                    # ---------------------------------------------
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)

    @property
    def center(self):
        return center

    def muestrear_posiciones_esfera(self,frame,center):

        global muestras
        global contador_muestras

        # --- Activa una marca "t" en el cronómetro ---
        t = time.time()
        # -------------------------------------------------------
        # Almacena en el diccionario "pos", las coordenadas de la
        #        posición de la canica y su centro
        # -------------------------------------------------------
        pos = {"center":center,"t":t}
        # -------------------------------------------------------
        # Almacena en el arreglo "cola" de diccionarios "pts" el
        #               diccionario "pos"
        # -------------------------------------------------------
        self.pts.appendleft(pos)

        # -------------------------------------------------------
        # Si la canica no ha iniciado su movimiento, las dos
        #   localidades del arreglo "cola" de diccionarios
        #                  están vacias
        # -------------------------------------------------------

        if self.pts[-1]["center"] != None and self.pts[0]["center"] != None:          
            # -------------------------------------------------------
            # Captura posiciones instantáneas del movimiento del
            # "centro de masa" de la canica:
            # pts[0]  -> posicion actual
            # pts[-1] -> posicion inmediatamente anterior
            # -------------------------------------------------------
            x0 = self.pts[0]["center"][0]
            y0 = self.pts[0]["center"][1]
            t0 = self.pts[0]["t"]
            x1 = self.pts[-1]["center"][0]
            y1 = self.pts[-1]["center"][1]
            t1 = self.pts[-1]["t"]
            # --- Calcula la distancia instantánea recorrida ---
            dx = x0-x1
            dy = y0-y1
            dm = np.sqrt(dx*dx + dy*dy)
            #print("dm = ",dm," | dx = ",dx," | dy = ",dy)
            
            # *******************************************************
            #
            #      --- INICIO DE DESPLAZAMIENTO DE LA ESFERA ---
            #
            # Aqui, la esfera INICIA su desplazamiento y se CAPTURAN
            # todas sus posiciones INSTANTANEAS y los TIEMPOS de cada
            # una de ellas, en el DICIIONARIO "n", conforme a la
            # siguiente concvencion:
            #
            # n -> numero de muestra
            # p1 -> coordenada instantanea anterior: (x1,y1)
            # p0 -> coordenada instantanea actual: (x0,y0)
            # dx -> desplazamiento en "x"
            # dy -> desplazamiento en "y"
            # dm -> distancia recorrida en pixeles del punto
            #       p1 al punto p0
            # t -> tiempo instantaneo del punto p0
            #
            # *******************************************************
            # -------------------------------------------------------
            # Comprueba si existe cambio en la posición del centro
            # de la esfera (dm > 3), lo cual indicaría que esta inició
            #                  su movimiento
            # -------------------------------------------------------

            if dm > 3.0 and dx > 0 and dy > 0:
                m = {"n":contador_muestras,"p1":(x1,y1,t1),"p0":(x0,y0,t0),
                     "dx":dx,"dy":dy,"dm":dm}
                muestras.append(m)
                contador_muestras +=1

    @property
    def muestras(self):
        return muestras

    def imprimir_muestras_capturadas(self):

        print()
        print(" ------------------------------------")
        print("  CLASE: Esfera ")
        print("     Impresion de muestras:")
        print(" ------------------------------------")
        for m in muestras:
            print(m)
                    
    def inicializar_variables_muestreo(self):

        global muestras
        global contador_muestras
        
        # --- LIMPIAR ARREGLOS Y DICCIONARIOS ---   
        self.pts = deque(maxlen=self.buffer)
        # --- Arreglo de diccionarios ---
        muestras = []
        # --- Diccionarios ---
        pos = {}
        m = {}
        # --- Contador de muestras ---
        contador_muestras = 0

    def diagrama_cuerpo_libre(self,frame):

        # ---------------------------------------------
        # Centro de la esfera en el 75% de su recorrido
        # ---------------------------------------------
        prop = int(len(muestras)/4)
        x0, y0, t0 = muestras[len(muestras)-prop]["p0"]
        x0 = 570 + 20
        # --- Siguiente muestra ---
        x1, y1, t1 = muestras[len(muestras)-prop+2]["p0"]
        
        # ---------------------------------------------
        # Dibuja el circulo amarillo alrededor de la
        #                 canica
        # ---------------------------------------------
        cv2.circle(frame, (int(x0), int(y0)), 20,
                (0, 255, 255), 2)
        # ---------------------------------------------
        # Dibuja un punto rojo en el centro de la canica
        # ---------------------------------------------
        cv2.circle(frame, (int(x0), int(y0)), 5, (0, 0, 255), -1)

        # ---------------------------------------------
        # Dibuja un vector de gravedad
        # ---------------------------------------------
        color = (0, 255, 0)
        thickness = 3
        cv2.line(frame, (int(x0), int(y0)), (int(x0), int(y0)+50), color, thickness)
        # --- Flecha ---
        cv2.line(frame, (int(x0-5), int(y0)+50), (int(x0+5), int(y0)+50), color, thickness)
        cv2.line(frame, (int(x0+5), int(y0)+50), (int(x0), int(y0)+60), color, thickness)
        cv2.line(frame, (int(x0), int(y0)+60), (int(x0-5), int(y0)+50), color, thickness)

        # ---------------------------------------------
        # Dibuja un vector de aceleracion
        # ---------------------------------------------
        color = (0, 255, 255)
        thickness = 2
        # --- Ecuacion de la recta de la aceleracion ---
        if (x1-x0) != 0:
            m = (y1 - y0)/(x1 - x0)
        else:
            m = 10
        g = 60    
        b = y1 - m*x1
        teta = np.arctan(m)
        fi = np.pi/2 - teta
        q = g*np.sin(fi)
        n = q*np.cos(teta)
        p = q*np.sin(teta)
        x5 = int(x0 + n)
        y5 = int(y0 + p)
        cv2.circle(frame, (int(x5), int(y5)), 5, (0, 0, 255), -1)
        
        
        cv2.line(frame, (int(x0), int(y0)), (int(x5), int(y5)), color, thickness)
        cv2.line(frame, (int(x5), int(y5)), (int(x0), int(y0)+60), color, thickness)
        # --- Flecha ---
##        cv2.line(frame, (int(x0-5), int(y0)+50), (int(x0+5), int(y0)+50), color, thickness)
##        cv2.line(frame, (int(x0+5), int(y0)+50), (int(x0), int(y0)+60), color, thickness)
##        cv2.line(frame, (int(x0), int(y0)+60), (int(x0-5), int(y0)+50), color, thickness)
        
