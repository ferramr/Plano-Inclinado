# *************************************
#
# Clase: --> Graficador 
# Modulo: -> graficador.py
# Ubicacion -> v.graficador
#
# Descripción:
#   Grafica posicion, velocidad y aceleracion
#
# Fecha:
#   enero 18/2022
#
# ************************************

import numpy as np
import matplotlib.pyplot as plt
import imutils
import cv2

class Graficador:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self):
        print("----------------------------")
        print(" CONSTRUCTOR: Graficador")
        print("----------------------------")

    def graficar_curvas_resultantes1(self,frame,t,d,modelos):
       
        # --------------------------------------------------
        # --- Modelos matemáticos en formato de polinomios
        # --------------------------------------------------
        model_d, model_v, model_a = modelos
        # --- model_d:
        #       -> Distancia(t) = ax^2 +bx + c
        # --- modelo_v:
        #       -> Velocidad(t) = d(Distancia)/dt = 2ax +b <- 1era. DERIVADA
        # --- model_a:
        #       -> Aceleracion(t) = d2(Distancia)/dt = 2a <- 2nda. DERIVADA
    
        # -----------------------------------------------------
        #   3 Graficas en una sola ventana:
        #       desplazamiento  -> verde    (subplot(2,2,1))
        #       velocidad       -> azul     (subplot(2,2,2))
        #       aceleracion     -> magenta  (subplot(2,2,3))
        # -----------------------------------------------------
        plt.clf()
        plt.figure(0)
        
        plt.subplot(2, 2, 1)
        plt.plot(t,model_d(t)/100, 'r-')
        #plt.xlabel("tiempo")
        plt.ylabel("distancia [m]")
        plt.grid()

        plt.subplot(2, 2, 2)
        plt.plot(t,model_v(t)/100, 'b-')
        #plt.xlabel("tiempo")
        plt.ylabel("velocidad [m/s]")
        plt.grid()

        plt.subplot(2, 2, 3)
        plt.plot(t,model_a(t)/100, 'm-')
        plt.xlabel("tiempo")
        plt.ylabel("aceleracion [m/s^2]")
        plt.grid()

        plt.subplot(2, 2, 4)
        plt.plot(t, d, 'bo')
        plt.xlabel("tiempo")
        plt.ylabel("muestras")
        plt.grid()

        plt.savefig("grafica_0.jpg")

        # --- Imagen para superposicion y transparencia ---
        overlay = frame.copy()   
        # --------------------------------------------------------------
        #    overlay --> Imagen superpuesta a mostrar en tamaño DISPLAY 
        # --------------------------------------------------------------
        grafica = imutils.resize(cv2.imread("grafica_0.jpg"),400)
        h, w = grafica.shape[:2]    # 300 x 400
        hf, wf = frame.shape[:2]    # 637 x 850
        #print(" frame hf = ",hf," |wf = ",wf)

        grafica = imutils.resize(grafica, width=600)
        h, w = grafica.shape[:2]

        pip_h = 40 #25
        pip_w = 20 
            
        overlay[pip_h:pip_h+h,pip_w:pip_w+w] = grafica

        # --- Overlay de dos imagenes ---
        alpha = 0.6 # 0.6 el mejor # 0.8
        cv2.addWeighted(overlay,alpha,frame,1-alpha,0,frame)

    def graficar_curvas_resultantes2(self,frame,t,d):
            print()

        # ---------------------------------------------------------------
        # --- Graficas ---
        # ---------------------------------------------------------------

        # -----------------------------------------------
        #   1 Grafica en una sola ventana:
        #     Desplazamiento, Velocidad y Aceleracion ---
        #     Grafica 0 :   desplazamiento  -> rojo
        #                   velocidad       -> azul
        #                   aceleracion     -> magenta
        # -----------------------------------------------
##    plt.clf()
##    plt.figure(0)
##
##    plt.plot(tiempo,model_d(tiempo), 'r-', label='line 1', linewidth=5)
##    plt.plot(tiempo,model_v(tiempo), 'b-', label='line 1', linewidth=5)
##    plt.plot(tiempo,model_a(tiempo), 'm-', label='line 1', linewidth=5)
##    plt.plot(t,d, 'ko', linewidth=5)
##
##    plt.title("d/v/a vs. t")
##    plt.xlabel("tiempo")
##    plt.ylabel("dist/vel/acel")
##    plt.grid()
##
##    plt.savefig("grafica_0.jpg")
            
