#******************************************************
#
#  PLANO INCLINADO - Proyecto Capstone IoT - por:
#
#       - Eduardo Rodriguez Martínez
#       - Fernando Ramirez Rojas                            
#
#     Algoritmo:
#
#  1. Establecer comunicacion serial con Arduino/ESP32CAM
#  2. CONECTAR CON EL BROKER PUBLICO MQTT SELECCIONADO
#  3. Inicializar cámara
#  4. REMOTO: Envia "angulo de inclinacion" por "MQTT" en el tema:
#       - "python/rx"
#  5. REMOTO: Recibe el "estado" del experimento por "MQTT" en el tema:
#       - "python/mqtt"
#  6. Reenviar el "angulo solicitado" a ARDUINO por comuncacion serial (USB)
#  7. Realizar Procesamiento Digital de Imágenes con Realidad Aumentada
#  8. REMOTO: Recibe "resultados del experimento" por "MQTT" en el tema:
#       - "python/mqtt"
#
#                                   31 / enero / 2022
#
#  Requiere tener conectado ARDUINO corriendo el programa:
#
#   "plano_inclinado_80.ino"
#
#
#******************************************************************************************

import imutils
import cv2
import json

from c.comunicacion import Comunicacion
from c.mqtt import Mqtt
from m.dsp import DSP
from m.marcadores import Marcadores
from m.esfera import Esfera
from v.graficador import Graficador
from v.display import Display
# +++++++++++++++++++++++++++++++++++++++++++++++
# erm_08-02-2021:
from forms import ExperimentForm
# +++++++++++++++++++++++++++++++++++++++++++++++

# +++++++++++++++++++++++++++++++++++++++++++++++
# erm_01-02-2021:
# modulos para usar Flask
from flask import Response
from flask import Flask
from flask import render_template, request, redirect, url_for
# modulos para usar hilos
import threading
import argparse
# +++++++++++++++++++++++++++++++++++++++++++++++

# --- Comunicacion serial con ARDUINO ---
com = Comunicacion()
serialConnection = com.inicializar_comunicacion_serial()
# +++++++++++++++++++++++++++++++++++++++++++++++
# erm_02-02-2020:
outputFrame = None              # variable global que contiene la trama actual
lock = threading.Lock()         # asegura que solo un hilo tenga acceso
experimento_en_curso = False    # Experimento en curso (bloqueante)   
# +++++++++++++++++++++++++++++++++++++++++++++++

# +++++++++++++++++++++++++++++++++++++++++++++++
# erm_01-02_2020
# --- Inicializacion del objeto Flask ---
app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20f0'
# +++++++++++++++++++++++++++++++++++++++++++++++

# -----------------------------------------------------------------------
#       Inicializa la cámara web
# -----------------------------------------------------------------------
vs = cv2.VideoCapture(0)

# +++++++++++++++++++++++++++++++++++++++++++++++
# erm_01-02-2021:
# ---------------------------------------
# --- Estructura de flujos para Flask ---
# ---------------------------------------
# Empezamos por la pagina principal
@app.route("/", methods=["GET", "POST"])
def index():
    global experimento_en_curso
    form = ExperimentForm()
    if form.validate_on_submit():
        angulo = form.angulo.data
        com.ecribir_comando_serial(serialConnection,angulo)
        experimento_en_curso = True

        next = request.args.get('next', None)
        if next:
            return redirect(next)
        return redirect(url_for('index'))
	# return the rendered template
    return render_template("index.html", form=form, flag=experimento_en_curso)
# +++++++++++++++++++++++++++++++++++++++++++++++

def experimento():
    # ------------------------------------
    #   AMARILLO -> Color de la "esfera"
    # ------------------------------------
    amarilloLower = (25, 68, 6)
    amarilloUpper = (35, 255, 155)
    rangoAmarillo = ((25, 68, 6),(35, 255, 155))

    # ------------------------------------
    #  AZUL CLARO -> Color de los
    #   marcadores de referencia
    # ------------------------------------
    azulClaroLower = (80, 100, 60)
    azulClaroUpper = (120, 180, 255)
    rangoAzulClaro = ((80, 100, 60), (120, 180, 255))

    # --- Longitud del plano inclinado en cm ---
    longitud_plano = 37.5

    # ----------------------------------------
    #         Creacion de objetos
    # ----------------------------------------
    # --- Procesamiento de Imagenes y Datos ---
    dsp = DSP(longitud_plano)
    # --- Manejo de graficas de desplazamiento,
    #         velocidad y aceleración
    graficas = Graficador()
    # --- Maracadores de referencia para
    #      medir distancias y angulos
    marcador = Marcadores(rangoAzulClaro,longitud_plano)
    # --- Esfera ---
    esfera = Esfera(rangoAmarillo)
    # --- Zonas informativas en el extremo 
    # derecho de la imagen (letras blancas,
    #           fondo azul)
    info = Display()

    # ----------------------------------------
    # Creacion del objeto MQTT
    # ----------------------------------------
    broker = '35.156.220.109' #'127.0.0.1'  # <- localhost  IP Publica:'35.156.220.109'
    topic_pub = "python/mqtt"
    topic_sub = "python/rx"

    client_mqtt = Mqtt(broker)
    client = client_mqtt.connect_mqtt()
    client.loop_start()
    client_mqtt.subscribe(client, topic_sub)
    msg = "Escribe un angulo en el interavlo [10, 45] grados:"
    client_mqtt.publish(client,msg,topic_pub)
    # ----------------------------------------

    # --- Estado del experimento ---
    secuencia = []
    secuencia.append('Sistema Activado')
    secuencia.append('Solicitud Recibida')
    secuencia.append('Inicializa Esfera')
    secuencia.append('Angulo CERO')
    secuencia.append('Angulo SOLICITADO')
    secuencia.append('Libera Esfera')
    secuencia.append('Finaliza Experimento')

    # --- Variables auxiliares ---
    sel = None                      # sel <- Seleccion del estado 

    # variables globales del buffer de video, la trama actual, y el candado
    global vs, outputFrame, lock, com, experimento_en_curso

    while True:

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # procesamiento_imagen(frame)
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # -----------------------
        #   Captura de frames
        # -----------------------
        ret, frame = vs.read()
        if frame is None:
            continue
    
        # ----------------------------------------------------
        # Sin importar el tamaño de los frames, se estandariza
        #   el tamaño del frame a un ancho de 850 pixeles
        # ----------------------------------------------------
        frame = imutils.resize(frame, width=850)

        # --- Filtro para minimizar ruido ---
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        # --- Coversion al espacio de color HSV ---
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        info.mostrar_fecha_sistema(frame)

#        # -----------------------------------------------------------
#        # Recepcion de mensajes remotos por MQTT [angulo solicitado]
#        # -----------------------------------------------------------
#        if not(experimento_en_curso):
#            # --- Mensaje recibido por MQTT en el tema: python/rx [topic_sub] ---
#            msg = client_mqtt.msg_recibido
#            if msg != "":
#                # --- Comprueba que el angulo solicitado se encuentre ---
#                #               entre 5 y 45 grados
#                # --------------------------------------------------------
#                if int(msg) >= 5 and int(msg) <= 45:
#                    # --- Enviar angulo solicitado a ARDUINO ---
#                    com.ecribir_comando_serial(serialConnection,msg)
#                    angulo_valido = True
#                    # --- Bandera de "experimento en curso" ---
#                    experimento_en_curso = True
#                else:
#                    # --- El angulo se encuentra fuera de rango ---
#                    msg = "Angulo fuera de rango: [10, 45]"
#                    client_mqtt.publish(client,msg,topic_pub)
#                    angulo_valido = False
#                    # --- Libera bandera de "experimento en curso" ---
#                    experimento_en_curso = False
#                # --- Limpia campo de mensaje de "topic_sub" ---
#                msg = ""
#                client_mqtt.publish(client,msg,topic_sub)
#                continue

        if experimento_en_curso:
            # ----------------------------------
            # Lectura de comandos recibidos
            # desde arduino
            # ----------------------------------
            comando = com.leer_comando_serial(serialConnection)
            # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # erm_03-02-2022:
            # Descomentar la linea de abajo para probar el videostreaming sin 
            # necesidad de correr todo el experimento
            #comando = 0
            # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            if comando != None:
                sel = comando
                print("-------------------------------------------------")
                print(" Modelo:: ",secuencia[sel])
                print("-------------------------------------------------")
                # --- Publicacion en python/mqtt de la secuencia del experimento ---
                msg = secuencia[sel]
                client_mqtt.publish(client,msg,topic_pub)
            # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # erm_03-02-2022:
            # Se continua el ciclo while hasta recivir un comando
            else:
                continue
            # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            if sel == 0: # --- Sistema Activado ---
                info.mostrar_portada_principal(frame)

            elif sel == 1: # --- Sistema Activado ---
                info.mostrar_portada_principal(frame)

            elif sel == 2: # --- Inicializa Esfera ---    
                esfera.inicializar_variables_muestreo()
                            
            elif sel == 3: # --- Angulo CERO ---
                marcador.distancia_entre_marcadores(frame,hsv)
                marcador.dibujar_linea_horizontal(frame)

            elif sel == 4:  # --- Angulo Solicitado ---
                marcador.distancia_entre_marcadores(frame,hsv)
                marcador.dibujar_triangulo_rectangulo(frame)
                esfera.seguir_trayectoria_esfera(frame,hsv)

            elif sel == 5: # --- Libera Esfera ---
                marcador.distancia_entre_marcadores(frame,hsv)
                marcador.dibujar_triangulo_rectangulo(frame)
                            
                esfera.seguir_trayectoria_esfera(frame,hsv)
                esfera.muestrear_posiciones_esfera(frame,esfera.center)

            elif sel == 6: # --- Finaliza Experimento ---
                if comando == 6:
                    # --- Procesamiento de muestras de la esfera ---
                    esfera.imprimir_muestras_capturadas()
                    muestras = esfera.muestras
                    dsp.procesar_muestras_capturadas(muestras,marcador.plano_inclinado)
                    dsp.imprimir_informacion_sistema()
                    dsp.texto_informacion_display()
                    # --- Envio de informacion a MQTT en formato JSON ---
                    dsp.convertir_informacion_json()
                    msg = dsp.ijson
                    client_mqtt.publish(client,msg,topic_pub)
                    # --- Libera bandera de "experimento_en_curso" ---
                    experimento_en_curso = False

                # --- Dibujo de plano inclinado ---
                marcador.distancia_entre_marcadores(frame,hsv)
                marcador.dibujar_triangulo_rectangulo(frame)
                # --- Genera graficas de posicion, velocidad y aceleracion ---
                graficas.graficar_curvas_resultantes1(frame,dsp.t,dsp.d,dsp.modelos)

                # --- Genera ventanas informativas "azules" en
                #       el lateral derecho de la imagen
                for i in range(len(dsp.texto)):
                    info.crear_ventana_informativa(frame,i,dsp.texto)

                # --- Dibujo de cuerpo libre ---
                esfera.diagrama_cuerpo_libre(frame)
                msg = ""
                
        # --- Muestra cada frame ---
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # erm_03-02-2021:
        # Se comento la linea 280 y se añadieron las lineas 281-282 para 
        # desplegar el video en pagina web usando Flask
        # cv2.imshow("Frame", frame)
        with lock:
            #print("\nHaciendo copia de frame\n")
            outputFrame = frame.copy()
        ## +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # erm_03-02-2021:
        # Se comentaron las lineas 296-301 ya que la condicion de paro se
        # verifica en la rutina principal
        # # --- Captura de teclado ---
        # key = cv2.waitKey(1) & 0xFF
        # # -----------------------------------------------------
        # # Si se presiona la tecla "q" el programa termina
        # # -----------------------------------------------------
        # if key == ord("q"):
        #     break

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# erm_03-02-2021:
def generate():
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                continue

            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            if not flag:
                continue
        
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +  bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())

    t = threading.Thread(target=experimento)
    t.daemon = True
    t.start()

    app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)

print("\nEso es todo amigos!!\n")
# --- Coloca el plano inclinado en inclinacion de 1 grado ---
com.ecribir_comando_serial(serialConnection,"50")
serialConnection.write(9) 
serialConnection.close()

# --- Libera camara de video ---
vs.release()

    # --- Destruye ventanas ---
    #cv2.destroyAllWindows()