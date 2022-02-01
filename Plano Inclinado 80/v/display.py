# *************************************
#
# Clase: --> Display 
# Modulo: -> display.py
# Ubicacion -> v.display
#
# Descripción:
#   Muestra informacion del sistema sobre la imagen
#
# Fecha:
#   diciembre 31/2021
#
# ************************************

import time
import datetime
import imutils
import cv2

p_ref = (570, 110)
w_ref = 270
h_ref = 30

class Display:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self):
        print("----------------------------")
        print(" CONSTRUCTOR: Display")
        print("----------------------------")

    def mostrar_portada_principal(self,frame):

        # --- Imagen para superposicion y transparencia ---
        overlay = frame.copy()   
        # --------------------------------------------------------------
        #    overlay --> Imagen superpuesta a mostrar en tamaño DISPLAY 
        # --------------------------------------------------------------
        portada = imutils.resize(cv2.imread("Portada 4.png"),400)
        h, w = portada.shape[:2]    # 300 x 400
        hf, wf = frame.shape[:2]    # 637 x 850
        #print(" frame hf = ",hf," |wf = ",wf)

        portada = imutils.resize(portada, width=600)
        h, w = portada.shape[:2]

        pip_h = 80 #40 #25
        pip_w = 20 
            
        overlay[pip_h:pip_h+h,pip_w:pip_w+w] = portada

        # --- Overlay de dos imagenes ---
        alpha = 1.0 # 0.6 el mejor # 0.8
        cv2.addWeighted(overlay,alpha,frame,1-alpha,0,frame)

    def mostrar_fecha_sistema(self,frame):

        # --------------------------
        # Mostrar fecha sobre video
        # --------------------------
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        topLeft = (p_ref[0], (p_ref[1]-40))
        bottomRight = (p_ref[0]+w_ref, p_ref[1]-40-h_ref)

        topLeft_label = ((topLeft[0]+25), (topLeft[1]-10))

        font = cv2.FONT_HERSHEY_SIMPLEX
        color_bg = (255,0,0)        # Color fondo: Azul oscuro 
        color_txt = (255,255,255)   # Color texto: Blanco 

        cv2.rectangle(frame, topLeft,bottomRight,color_bg, -1)
        # --- TEXTO/DATOS DISPLAY [letras/digitos blancol]
        cv2.putText(frame, str(now),topLeft_label,font,0.6, color_txt,2,cv2.LINE_AA)

    def crear_ventana_informativa(self,frame,nv,texto):

        global p_ref
        # -----------------------------------------------------------
        #   Ventana Horizontal de 240 x 30
        # -----------------------------------------------------------
        num_ventana = nv
        dh = (num_ventana-1)*h_ref
        gap = (num_ventana-1)*5
        topLeft = (p_ref[0], (p_ref[1]+dh+gap))
        bottomRight = (p_ref[0]+w_ref, p_ref[1]+dh+gap+h_ref)

        topLeft_label = ((topLeft[0]+10), (topLeft[1]+20))

        font = cv2.FONT_HERSHEY_SIMPLEX
        color_bg = (255,0,0)        # Color fondo: Azul oscuro 
        color_txt = (255,255,255)   # Color texto: Blanco 

        cv2.rectangle(frame, topLeft,bottomRight,color_bg, -1)
        
        # --- TEXTO/DATOS DISPLAY [letras/digitos blancol]
        cv2.putText(frame, texto[nv],topLeft_label,font,0.6, color_txt,2,cv2.LINE_AA)
