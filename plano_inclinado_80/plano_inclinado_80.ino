/******************************************************
#
#  Comunicacion con Arduino - Python
#
#  - PYTHON y ARDUINO "platican" indefinidamente
#  - El intercambio de información se realiza por el puerto serial
#    enviando y recibiendo información en formato de BYTES
#
#     Algoritmo:
#
#  1. ARDUINO envía el texto. "Hola mundo -> 1234"
#  2. Cuando Python encuentra la palabra "mundo", le envia
#     a ARDUINO el número 9 para que su LED 13 encienda
#     y apague 9 veces
#  3. El proceso se repite ciclicamente
#
#                                   31 / enero / 2022
#
#  Requiere tener conectado ARDUINO corriendo el programa en Python::
#
#   plano_inclinado_80.py
#
#*******************************************************/

/***********************************************************
 * ESTADOS DEL SISTEMA:
 * Mensajes:  0 - "Sistema Activado"
 *            1 - "Solicitud Recibida"
 *            2 - "Inicializa Esfera"
 *            3 - "Inicializa Plano Inclinado con Angulo CERO"
 *            4 - "Posiciona Plano Inclinado con Angulo SOLICITADO"
 *            5 - "Libera Esfera"
 *            6 - "Finaliza Experimento"
 *            
 ***********************************************************/

#include <Servo.h>

Servo myservo;  // create servo object to control a servo

int angulo_actual = 1;
int angulo_objetivo = 1;
int inicio_secuencia = 1;
int retardo_angulo = 100;

String msg_enviado;
char option;
String data;
String comando;

int incomingByte = 0; // for incoming serial data
String cmd_recibido_python = "";

int pinLED = 13;

boolean sistema_on = true;
boolean experimento_en_curso = false;

void setup() {

  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  
  Serial.begin(9600);

 /*******************************
   * Interruptores manuales *
   *******************************/
  pinMode(2, INPUT);         // Angulo de 1 grado. Captura de canica
  digitalWrite(2, HIGH);     // turn on pullup resistors
  pinMode(3, INPUT);          // Angulo de 20 grados. Posicion HORIZONTAL
  digitalWrite(3, HIGH);     // turn on pullup resistors
  pinMode(4, INPUT);          // Angulo de 40 grados. [30 grados EFECTIVOS]
  digitalWrite(4, HIGH);     // turn on pullup resistors
  pinMode(5, INPUT);          // Angulo de 60 grados [50 grados EFECTIVOS]
  digitalWrite(5, HIGH);     // turn on pullup resistors

  pinMode(7, OUTPUT);       // Manejo del solenoide de liberacion

  myservo.write(1);

  desactivar_solenoida();

  msg_enviado = "0";      // 0 - "Sistema Activado"
  envia_msgs_python();

}

int entrada_2;

void loop() {

  if (!experimento_en_curso) {
    experimento_en_curso = true;
    recibe_msgs_python();
    // --- Sistema encendido ---
    if (sistema_on) {
      /*******************************
       * SIMULACIONES DE ANGULOS DE 
       * INCLINACION
       *******************************/
      if(!digitalRead(2)){
        angulo_objetivo = 1;  // Angulo de 1 grado. Captura de canica
        inicio_secuencia = 1;
      }
  
      if(!digitalRead(3)){
        angulo_objetivo = 20; // Angulo de 20 grados. Posicion HORIZONTAL. 0 grados
        calibrar_angulo_cero();
        inicio_secuencia = 0;
      }
    
      if(!digitalRead(4)){
        angulo_objetivo = 50; // [30 grados EFECTIVOS]
        inicio_secuencia = 1;
      }
    
      if(!digitalRead(5)){
        angulo_objetivo = 65; // [45 grados EFECTIVOS]
        inicio_secuencia = 1;
      }
    
      if (angulo_objetivo != 1 && inicio_secuencia){
        Serial.flush();
        msg_enviado = "1";     // 1 - "Solicitud Recibida"
        envia_msgs_python();
        ejecuta_secuencia_posicionamiento();
        inicio_secuencia = 0;
      } else {
        posiciona_plano_inclinado();
      }
    } else {
      // --- Apagar Sistema ---
      sistema_on = false;
    }
    experimento_en_curso = false;
  } 
}

void posiciona_plano_inclinado(){
  
 if (angulo_actual < angulo_objetivo) {
    for(int i=angulo_actual; i<=angulo_objetivo; i++){
      myservo.write(i);
      delay(retardo_angulo);
    }
  }

  if (angulo_actual > angulo_objetivo) {
    for(int i=angulo_actual; i>=angulo_objetivo; i--){
      myservo.write(i);
      delay(retardo_angulo);
    }
  }
  angulo_actual = angulo_objetivo;
}

void calibrar_angulo_cero(){
  // ---------------------------------------------------------------------
  //        Captura esfera en posicion inicial para experimento
  // ---------------------------------------------------------------------
  // --- Envia mensaje informativo a Python ---
  Serial.flush();
  msg_enviado = "2";      // 2 - "Inicializa Esfera"
  envia_msgs_python();
  // --- Posiciona plano en angulo negativo para captura de la esfera ---
  angulo_objetivo = 1;
  posiciona_plano_inclinado();
  delay(100);
  // --- Captura esfera en posicion inicial ---
  liberar_esfera(); 

  // ---------------------------------------------------------------------
  //        Posiciona Plano Inclinado en Angulo CERO (horizontal)
  // ---------------------------------------------------------------------
  // --- Posiciona plano en angulo 20 correspondiente a posicion HORIZONTAL ---
  // El angulo de 20 corresponde a un angulo de offset
  angulo_objetivo = 20;
  posiciona_plano_inclinado();
  // --- Envia mensaje informativo a Python ---
  Serial.flush();
  msg_enviado = "3";      // 3 - "Inicializa Plano Inclinado con Angulo CERO"
  envia_msgs_python();
  delay(2000);
  
}

void ejecuta_secuencia_posicionamiento(){

  int temp = angulo_objetivo;

  // ---------------------------------------------------------------------
  //        Captura esfera en posicion inicial para experimento
  // ---------------------------------------------------------------------
  // --- Envia mensaje informativo a Python ---
  Serial.flush();
  msg_enviado = "2";      // 2 - "Inicializa Esfera"
  envia_msgs_python();
  // --- Posiciona plano en angulo negativo para captura de la esfera ---
  angulo_objetivo = 1;
  posiciona_plano_inclinado();
  delay(100);
  // --- Captura esfera en posicion inicial ---
  liberar_esfera(); 

  // ---------------------------------------------------------------------
  //        Posiciona Plano Inclinado en Angulo CERO (horizontal)
  // ---------------------------------------------------------------------
  // --- Posiciona plano en angulo 20 correspondiente a posicion HORIZONTAL ---
  // El angulo de 20 corresponde a un angulo de offset
  angulo_objetivo = 20;
  posiciona_plano_inclinado();
  // --- Envia mensaje informativo a Python ---
  Serial.flush();
  msg_enviado = "3";      // 3 - "Inicializa Plano Inclinado con Angulo CERO"
  envia_msgs_python();
  delay(2000);

  // ---------------------------------------------------------------------
  //        Posiciona Plano Inclinado en Angulo SOLICITADO
  // ---------------------------------------------------------------------
  // --- Envia mensaje informativo a Python ---
  Serial.flush();
  msg_enviado = "4";      // 4 - "Posiciona Plano Inclinado con Angulo SOLICITADO"
  envia_msgs_python();
  // --- BLOQUEA Liberacion de esfera ---
  bloquear_esfera();
  // --- Posiciona plano en en Angulo SOLICITADO ---
  angulo_objetivo = temp;
  posiciona_plano_inclinado();
  delay(2000);

  // ---------------------------------------------------------------------
  //        LIBERA Esfera
  // ---------------------------------------------------------------------
  // --- Envia mensaje informativo a Python ---
  Serial.flush();
  msg_enviado = "5";      // 5 - "Libera Esfera"
  envia_msgs_python();
  delay(500);
  desactivar_solenoida();
  liberar_esfera();
  delay(3000);

  // ---------------------------------------------------------------------
  //        FINALIZA Experimento
  // ---------------------------------------------------------------------
  // --- Envia mensaje informativo a Python ---
  Serial.flush();
  msg_enviado = "6";     // 6 - "Finaliza Experimento"
  envia_msgs_python();
}

void liberar_esfera(){
  // --- Comprime SOLENOIDE ---
  // Permite el paso de la esfera
  digitalWrite(7, HIGH);
  digitalWrite(8, LOW);
  delay(500);
  // --- Desactiva SOLENOIDE ---
  // Impide el paso de la esfera
  // FUERZA DEBIL DEL SOLENOIDA
  digitalWrite(7, LOW);
  digitalWrite(8, LOW);
}

void bloquear_esfera(){
  // --- Expande SOLENOIDE ---
  // Impide el paso de la esfera
  // FUERZA FUERTE DEL SOLENOIDA
  digitalWrite(7, LOW);
  digitalWrite(8, HIGH);
}

void desactivar_solenoida(){
  // --- Desactiva SOLENOIDE ---
  // Impide el paso de la esfera
  // FUERZA FUERTE DEL SOLENOIDA
  digitalWrite(7, LOW);
  digitalWrite(8, LOW);
  delay(100);
}

void envia_msgs_python(){
  Serial.println(msg_enviado);
  delay(1000);
}

void recibe_msgs_python(){

   if (Serial.available() > 0) {
    // Delay para dar tiempo al buffer para que reciba todos los caracteres
    delay(20); 
    // String para almacenar todos los caracteres recibidos
    cmd_recibido_python = "";  
    // ---------------------------------
    //  Lectura de los caracteres leidos 
    //  en el buffer: "cmd_recibido_python"
    // ---------------------------------
    while (Serial.available() > 0) {
       cmd_recibido_python += (char)Serial.read();
    } 

    if (cmd_recibido_python.toInt() < 50) {
      angulo_objetivo = cmd_recibido_python.toInt() + 20;  // Angulo Solicitado por mqtt
      inicio_secuencia = 1;
    } else {
      // Apagar Sistema
      sistema_on = false;
      // Guardar Sistema
      angulo_objetivo = 1;  // Angulo de 1 grado. Captura de canica
      posiciona_plano_inclinado();
      delay(200);
      // --- Captura esfera en posicion inicial ---
      liberar_esfera(); 
    }
    while (Serial.available()>0)  Serial.read();
   }
}
