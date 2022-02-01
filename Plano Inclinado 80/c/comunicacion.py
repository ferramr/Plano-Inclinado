# *************************************
#
# Clase: --> Comunicación 
# Modulo: -> comunicacion.py
# Ubicacion -> c.comunicacion
#
# Descripción:
#   Intenta la conexión con ARDUINO a través
#   del puerto Serial USB
#
# Requisitos:
#   Requiere tener conectado ARDUINO corriendo el programa:
#
#   Arduino/COMUNICACION SERIAL Python Arduino/plano_inclinado_70/
#   plano_inclinado_100.ino
#
# Fecha:
#   enero 14/2022
#
# ************************************

import serial
import serial.tools.list_ports
import time

class Comunicacion:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self):
        print("----------------------------")
        print(" CONSTRUCTOR: Comunicacion")
        print("----------------------------")
        self.cms = 0

    def inicializar_comunicacion_serial(self):
        print("-------------------------------------")
        print(" CLASE: Comunicacion")
        print(" inicializar_variables_comunicacion")
        print("--------------------------------------")
        # -----------------------------------------------------------------------
        #       Localiza PUERTO USB (COM) de Arduino
        # -----------------------------------------------------------------------
        self.baudRate = 9600         # Velocidad de transmisión: 9600 baudios
        ports = list(serial.tools.list_ports.comports())

        for p in ports:
            if "Arduino" in p.description:
                print("Arduino p: ",p)
            if "COM" in p.description:
                try:
                    serialConnection = serial.Serial(p[0],self.baudRate,timeout = 0)  # Instance serial object
                    print("")
                    print("**************************************")
                    print("-- Conexion establecida con ARDUINO --")
                    print("**************************************")
                    print("serialConnection.name: ",serialConnection.name)
                    print("serialConnection.port: ",serialConnection.port)
                    print("serialConnection.baudrate: ",serialConnection.baudrate)
                    print("---------------------------------------")
                    self.com = p[0]
                    return serialConnection
                except:
                    print("")
                    print("************************************************")
                    print("No se pudo establecer la comuncacion con ARDUINO")
                    print("************************************************")
                    return "Fallo la comunicacion serial"

    def leer_comando_serial(self,serialConnection):
        
        serialConnection.flush()
        string_recibido = serialConnection.readline()

        # --- Convierte BYTES a TEXTO (utf-8)
        comando = string_recibido.decode("utf-8")
        # > bytes_to_texto =  Inicializando
        # --- Limpia la cadena de texto de caracteres no deseables ---
        comando = comando.strip()

        if comando != '':
            print()
            print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
            print(" CLASE: Comunicacion [Arduino]")
            print(" Funcion: leer_comando_serial: ")
            print("Contador: ",self.cms," | comando RECIBIDO de ARDUINO: ",comando)
            print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
            self.cms += 1
            return int(comando)

    def ecribir_comando_serial(self,serialConnection,comando):
        print("")
        print("------------------------------------")
        print(" CLASE: Comunicacion [Arduino]")
        print(" Funcion: escribir_comando_serial: ")
        print(" ANGULO ENVIADO a ARDUINO: ",comando)
        print("------------------------------------")
        time.sleep(1)
        serialConnection.write(comando.encode())
        time.sleep(1)
