# *************************************
#
# Clase: --> Mqtt 
# Modulo: -> mqtt.py
# Ubicacion -> c.mqtt
#
# Descripción:
#   Intenta la conexión con un BROKER MQTT a traves msoquitto (puerto: 1883)
#
# Requisitos:
#   CONECTAR CON EL BROKER MQTT SELECCIONADO
#       - PREVIAMENTE debe estar corriendo "mosquitto.exe" en esta máquina:
#       -> C:\Program Files\mosquitto\mosquitto.exe
#
# Fecha:
#   14 / enero / 2022
#
# ---------------------------------------------------------------

# python 3.6

import random
import time
from paho.mqtt import client as mqtt_client

class Mqtt:
    
    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self, broker):
        
        print("----------------------------")
        print(" CONSTRUCTOR: Mqtt")
        print("----------------------------")

        # ----------------------------------------------------------------
        # 1 - Set the parameter of MQTT Broker connection
        # random.randint randomly generate the MQTT client id.
        # ----------------------------------------------------------------

        self.broker = broker
        self.port = 1883        
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'

        self.mensaje_sub = ""

    def connect_mqtt(self):

        print("-------------------------------------")
        print(" CLASE: Mqtt")
        print(" connect_mqtt")
        print("--------------------------------------")
        
        # -----------------------------------------------------------------
        # 2 - MQTT connect function
        # ------------------------------------------------------------------
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("")
                print("*********************************************")
                print("-- Conexion establecida con el broker MQTT --")
                print("*********************************************")
                print("Broker: ",self.broker)
                print("Port: ",self.port)
                print("Client id: ",self.client_id)
                print("---------------------------------------")
            else:
                print("")
                print("************************************************")
                print(" --- Fallo la conexion con el broker ---")
                print("Failed to connect, return code %d\n", rc)
                print("************************************************")

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def publish(self, client, mensaje, topic):

        # --------------------------------------------------------------------
        # 3 - Publish messages
        # MQTT client publish to the topic "self.topic"
        # --------------------------------------------------------------------

        #msg = f"messages: {mensaje}"
        msg = mensaje
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    def subscribe(self, client: mqtt_client, topic):

        # --------------------------------------------------------------------
        # 4 - Subscribe
        # This function will be called after the client received messages
        # from the MQTT Broker.
        # --------------------------------------------------------------------

        def on_message(client, userdata, msg):

            self.mensaje_sub = msg.payload.decode()
            
            #print()
            #print(" ***********************************************************")
            #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            #print(" *********************************************************** ")
    
        client.subscribe(topic)
        client.on_message = on_message

    @property
    def msg_recibido(self):
        return self.mensaje_sub


