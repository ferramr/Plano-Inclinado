# *************************************
#
# Clase: --> DSP 
# Modulo: -> dsp.py
# Ubicacion -> m.dsp
#
# Descripción:
#   Procesamiento digital de señales
#   Actualiza el diccionario:
#
# Fecha:
#   enero 18/2022
#
# ************************************

import json
import numpy as np

global t                # t - tiempo de la muestra "n"
global d                # d - distancia de la muestra "n"
global posicion         # posicion = (d, t)

global D                # D - Lonigtud del plano inclinado en "pixeles"
global angulo           # angulo - Angulo del plano inclinado
global plano_inclinado  # plano_inclinado = (D, angulo)

global model_d          # model_d - Ecuacion de la Distancia(t)
global model_v          # model_v - Ecuacion de la Velocidad(t)
global model_a          # model_a - Ecuacion de la Aceleracion(t)
global modelos          # modelos = (model_d, model_v, model_a)

global u                # u - coeficiente de friccion dinamica

global texto            # texto - texto informativo a desplegar
global ijson

class DSP:

    # -------------------------------------------------------
    #           CONSTRUCTOR
    # -------------------------------------------------------
    def __init__(self,longitud_plano):
        print("----------------------------")
        print(" CONSTRUCTOR: DSP")
        print("----------------------------")

        global t
        global d
        global plano_inclinado 

        t = []
        d = []
        plano_inclinado = []

        self.longitud_plano = longitud_plano

    def procesar_muestras_capturadas(self,muestras,plano_inc):
        print("-------------------------------------")
        print(" CLASE: DSP")
        print(" procesar_muestras_capturadas")
        print("--------------------------------------")

        # ---------------------------------------------------------
        # plano_inclinado = (D, angulo) -> Vector de dos valores:
        #
        #  D = Lonigtud de la hipotenusa en "pixeles"
        #       Se toma como referencia esta longitud en "pixeles" para
        #       relacionarla con la longitud de "self.longitud_plano"
        #       cm medidos entre los marcadores
        #
        #  angulo = Angulo de inclinacion en grados
        # ---------------------------------------------------------

        global t
        global d
        global posicion # <- posicion (d, t)

        global D
        global angulo
        global plano_inclinado

        global model_d
        global model_v
        global model_a

        global modelos # <- modelos (model_d, model_v, model_a)

        global u

        tmpo = []
        dpix = []
        posicion = []

        # ---------------------------------------------------
        # Captura de los valores de Longitud y Angulo del
        # Plano Inclinado
        # ---------------------------------------------------
        plano_inclinado = plano_inc
        D = plano_inclinado[0]       # <- Longitud en "pixeles"
        angulo = plano_inclinado[1]
        print("D [pixeles] = ",plano_inclinado[0])
            

        # --- Formato del arreglo de diccionarios: "muestras: m" ---
        #
        # m = {"n":contador_muestras,
        #      "p1":(x1,y1,t1),         # <- Muestra anterior
        #      "p0":(x0,y0,t0),         # <- Muestra actual
        #      "dx":dx,"dy":dy,"dm":dm} # <- Distancias instantaneas
        #
        # n -> numero de muestra
        # p1 -> coordenada instantanea anterior: (x1,y1,t1)
        # p0 -> coordenada instantanea actual: (x0,y0,t0)
        # dx -> desplazamiento en "x"
        # dy -> desplazamiento en "y"
        # dm -> distancia recorrida en pixeles del punto
        #       p1 al punto p0
        # 
        # -----------------------------------------------------------

        # ---- o: <- Origen [xo, yo, to <- referidos al origen] ---
        xo, yo, to = muestras[0]["p1"]   
        # --- Vectores de tiempo y distancia, en "pixeles", en t = 0 ---
        tmpo.append(0)
        dpix.append(0)

        max_dx = muestras[0]["dx"]
        max_dy = muestras[0]["dy"]
        max_dm = muestras[0]["dm"]
        # --- Calculo de "distancias" al origen "o" ---             
##        for i in range(1,len(muestras)):
##            # --- Filtrar muestras (limpiar) ---
##            if i < len(muestras):
##                if muestras[i]["dx"] > max_dx and muestras[i]["dy"] > max_dy and muestras[i]["dm"] > max_dm:
##                    max_dx = muestras[i]["dx"]
##                    max_dy = muestras[i]["dy"]
##                    max_dm = muestras[i]["dm"]
##                    # --- i: <- Valores "instantáneos" referidos al origen "o" ---
##                    xi, yi, ti = muestras[i]["p0"]
##                    x = xi - xo
##                    y = yo - yi
##                    # --- Tiempo "tro" y distancia "dro" referidos al origen ---
##                    tro = round((ti - to),2)
##                    dro = round(np.sqrt(x*x + y*y),2)
##                    # --- Vectores de tiempo y distancia ---
##                    tmpo.append(tro)
##                    dpix.append(dro)

        # --- Calculo de "distancias" al origen "o" ---             
        for i in range(1,len(muestras)):
            # --- Filtrar muestras (limpiar) ---
           
            if muestras[i]["dx"] > max_dx: 
                max_dx = muestras[i]["dx"]
            if muestras[i]["dy"] > max_dy: 
                max_dy = muestras[i]["dy"]
            if muestras[i]["dm"] > max_dm:
                max_dm = muestras[i]["dm"]
            # --- i: <- Valores "instantáneos" referidos al origen "o" ---
            xi, yi, ti = muestras[i]["p0"]
            x = xi - xo
            y = yo - yi
            # --- Tiempo "tro" y distancia "dro" referidos al origen ---
            tro = round((ti - to),2)
            dro = round(np.sqrt(x*x + y*y),2)
            # --- Vectores de tiempo y distancia ---
            tmpo.append(tro)
            dpix.append(dro)

        # --- Acondicionar datos de tiempo (tmpo) para graficación t[seg] ---
        tmin = tmpo[0]
        tmax = tmpo[len(tmpo)-1]
        t = np.linspace(tmin, tmax, len(tmpo))        

        # --- Acondicionar datos de distancia (dpix) para graficación d[cm] ----
        # ----------------------------------------------------------------------
        # La longitud del plano inclinado (self.longitud_plano cm) se toma como REFERENCIA
        # para calcular las distancias en "cm" de cada muestra (x,y,t) al origen:
        # Dref_pix -> Longitud del plano inclinado
        # d -> Distancia de cada "muestra" al origen, caculada utilizando una
        #      regla de tres simple: "dp*self.longitud_plano/Dref_pix"
        # ----------------------------------------------------------------------
        Dref_pix = plano_inclinado[0] 
        d = [round(dp*self.longitud_plano/Dref_pix,3) for dp in dpix]  

        # --- Arreglo "posicion" ---------------------------------------------
        #           p <- ([distancia al origen en cm], [tiempo en seg]) 
        # --------------------------------------------------------------------
        for i in range(len(t)):
            #posicion.append([d[i], round(t[i],3)])
            posicion.append([d[i], round(tmpo[i],3)])

        # --------------------------------------------------------------------
        # Modelado matemático mediante un polinomio de 2ndo. Orden de la
        # relación entre distancia recorrida y tiempo:
        # Distancia = d_t = F(t) = ad^2 +bd + c
        # tmpo <- tiempos (en seg) medidos para cada muestra
        #         desde el origen "to = 0"
        # d <- distancias (en cm) medidas para cada muestra
        #         desde el origen "do = 0"
        # --------------------------------------------------------------------
        #   Calculo de los coeficientes: a, b y c de: F(t) = ax^2 +bx + c
        # --------------------------------------------------------------------
        d_t = np.polyfit(tmpo, d, 2)

        # --------------------------------------------------------------------
        # --- Modelos matemáticos en formato de polinomio: F(t) = ax^2 +bx + c
        # --------------------------------------------------------------------
        # --------------------------------------------------------------------
        # Distancia(t) = model_d = ax^2 +bx + c
        # --------------------------------------------------------------------
        model_d = np.poly1d(d_t)
        # --------------------------------------------------------------------
        # Velocidad(t) = model_v = d(Distancia)/dt = 2ax +b <- 1era. DERIVADA
        # --------------------------------------------------------------------
        model_v = model_d.deriv()
        # --------------------------------------------------------------------
        # Aceleracion(t) = model_a = d(Velocidad)/dt = 2a <- 1era. DERIVADA
        # --------------------------------------------------------------------
        model_a = model_v.deriv()

        # --- Arreglo de Modelos ---
        modelos = (model_d, model_v, model_a)

        # --------------------------------------------------------------------
        #     Calculo del Coeficiente de Fricción Dinámica "u"
        # --------------------------------------------------------------------
        # --- Calculo del angulo del plano inclinado en "radianes" ---
        angulo_rad = angulo*np.pi/180
        # --- Calculo de la "Aceleracion" en "m/s^2" ---
        am = model_a[0]/100
        # --- Calculo de la componente de la aceleracion de la Gravedad [9.8m/s^2]
        # sobre la linea de desplazamiento de la esfera
        # ---------------------------------------------------------------------
        agtc = 9.8*(np.cos(angulo_rad))*np.tan(angulo_rad)
        agc = 9.8*np.cos(angulo_rad)
        # --- Calculo del coeficiente de friccion dinamica ---
        u = round(((am - agtc)/agc),4)
    
    @property
    def t(self):
        # t <- Arreglo de "tiempos" de muestreo
        return t

    @property
    def d(self):
        # d <- Arreglo de "distancias" de cada muestra en "cm"
        return d

    @property
    def posicion(self):
        # posicion <- Arreglo [d, t]
        return posicion

    @property
    def D(self):
        # D <- Longitud del plano inclinado en "pixeles"
        return D

    @property
    def angulo(self):
        # angulo <- Angulo del plano inclinado
        return angulo

    @property
    def plano_inclinado(self):
        # plano_inclinado <- Arreglo [D, angulo]
        return plano_inclinado

    @property
    def model_d(self):
        # model_d <- Polinomio cuadrático de distancia [d(t), t]
        return model_d

    @property
    def model_v(self):
        # model_v <- Polinomio lineal de velocidad [v(t), t]
        return model_v

    @property
    def model_a(self):
        # model_a <- Polinomio constante de aceleracion [a(t), t]
        return model_a

    @property
    def modelos(self):
        # modelos <- Arreglo de modelos [model_d, model_v, model_a]
        return modelos

    @property
    def u(self):
        # u <- Coeficiente de friccion dinamica
        return u

    def texto_informacion_display(self):
        # ------------------------------------------------------------------
        # Informacion a mostrarse en las "ventanas de texto" que aparecen
        # en la parte derecha de la imagen del plano inclinado con fondo
        # azul y texto en blanco.
        # ------------------------------------------------------------------

        global texto
        global valor
        global d

        texto = []

        texto.append("angulo: "+str(round((angulo-0.15),1))+" grados")
        texto.append("muestras: "+str(len(posicion)))
        texto.append("distancia rec: "+str(round((d[len(d)-1]/100),3))+" m")
        texto.append("tiempo: "+str(posicion[len(posicion)-1][1])+" seg")
        texto.append("aceleracion: "+str(round(model_a(0)/100,2))+" m/s^2")
        texto.append("coef.fricc. u: "+str(u))

    @property
    def texto(self):
        return texto
    
    def imprimir_informacion_sistema(self):
        # ------------------------------------------------------------------
        # Informacion FINAL del experimento que se enviara por "MQTT" para su
        # procesamiento al cliente remoto [IoT]
        # ------------------------------------------------------------------

        global t
        global d
        global posicion
        global D
        global angulo
        global u

        print()
        print(" -----------------------------------------------")
        print("  Clase: DSP ::")
        print("     Imprime Posicion ('distancia[cm]' y 'tiempo[seg]') ")
        print(" -----------------------------------------------")
        print(" Longitud del plano inclinado: ",D," pixeles")
        print(" Longitud del plano inclinado: ",self.longitud_plano," cm")
        print(" Angulo del plano inclinado:   ",angulo," grados")
        print(" Coeficiente de Friccion Dinamica:   ",u)
        print()
        print("n,  d[cm],  t[seg],   d(t),   v(t),   a(t)")
        for i in range(len(posicion)):
            t_t = posicion[i][1]
            d_t = round(model_d(t_t)/100,3)
            v_t = round(model_v(t_t)/100,3)
            a_t = round(model_a(t_t)/100,3)
            print(i,"  ",posicion[i][0],"  ",posicion[i][1],
                  "  ",d_t,"  ",v_t,"  ",a_t)
        print(" -----------------------------------------------")

    def convertir_informacion_json(self):

        global ijson
       
        # --------------------------------------------------------
        #  Convertir la informacion del sistema en un diccionario
        # --------------------------------------------------------
        dic = {"longitud":self.longitud_plano,"angulo":angulo,"u":u}
        for i in range(len(posicion)):
            j = posicion[i][1]
            n = str(i)
            t = "t" + n
            d = "d" + n
            v = "v" + n
            a = "a" + n
            dic.update({t:j,d:round(model_d(j)/100,3),
                        v:round(model_v(j)/100,3),a:round(model_a(j)/100,3)})

        print()
        print(" --------------------------------------------------")
        print(" Informacion del Sistema en formato de diccionario:")
        print(" --------------------------------------------------")
        print(dic)

        # convert into JSON:
        ijson = json.dumps(dic)

        # the result is a JSON string:
        print()
        print(" --------------------------------------------------")
        print(" Informacion del Sistema en formato JSON:")
        print(" --------------------------------------------------")
        print(ijson)

    @property
    def ijson(self):
        return ijson
            
        
