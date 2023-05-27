import socket
import random
import numpy as np
import sys
import time
import pickle

class agente:
    def __init__(self):
        self.IP = "127.0.0.1"
        self.puerto = 8080
        # Definir los parámetros del entorno Pong
        self.NUM_ACCIONES = 3  # Arriba, Abajo, Ninguna
        self.NUM_ESTADOS = 150000  # Número de percepciones o estados
        # Inicializar la tabla Q con valores aleatorios
        self.Q = np.random.rand(self.NUM_ESTADOS, self.NUM_ACCIONES)
        self.mapeado = {}
        self.indice_actual_asignar = 0
        self.acciones = {0: "UP", 1:"DOWN", 2:"NONE"}
        self.acciones_rev = {"UP":0, "DOWN":1, "NONE":2}
        
        # Definir los parámetros del algoritmo de Q-learning
        self.EPSILON = 0.1  # Tasa de exploración
        self.ALPHA = 0.05  # Tasa de aprendizaje
        self.GAMMA = 0.9  # Factor de descuento
        self.mi_puntuacion = 0
        self.puntuacion_enemiga = 0
        self.estado_prev = None
        self.accion_prev = None

    def set_connection(self, ip, puerto):
        self.IP = ip
        self.puerto = int(puerto)

    # Función para seleccionar una acción 
    def seleccionar_accion(self, estado):
        if random.random() < self.EPSILON: # para explorar
            return random.randint(0, self.NUM_ACCIONES - 1)
        else: 
            return np.argmax(self.Q[estado, :])
        
    def actualizar_Q(self, recompensa):
        indice_Q_actual = self.mapeado[self.estado_prev]
        indice_Q_futuro = self.mapeado[self.estado]
        accion = self.acciones_rev[self.accion_prev]
        self.Q[indice_Q_actual, accion] = (1-self.ALPHA) * self.Q[indice_Q_actual, accion] + self.ALPHA * (recompensa + self.GAMMA * np.max(self.Q[indice_Q_futuro, :]))
        #self.Q[indice_Q_actual, accion] += self.ALPHA * (recompensa + self.GAMMA * np.max(self.Q[indice_Q_futuro, :]) - self.Q[indice_Q_actual, 
                                                                                         #accion])
        
    def getRecompensa(self):
        recompensa = 0
        #SI HA HABIDO UN CAMBIO DE PUNTOS MAL
        if self.prev_mi_puntuacion - self.mi_puntuacion != 0:
            recompensa -= 1
        if self.puntuacion_enemiga - self.prev_puntuacion_enemiga != 0:
            recompensa -= 1
        '''
        # ESTAS RECOMPENSAS OFRECEN UN BUEN NIVEL DE JUEGO MAS RAPIDAMENTE
        #SI LA PELOTA REBOTA EN UNA PALA ES BUENO
        if self.estado_prev[2] == 1 and self.estado[2] == 0 and self.prev_mi_puntuacion == self.mi_puntuacion:
            recompensa += 0.1
        if self.estado_prev[2] == 0 and self.estado[2] == 1 and self.puntuacion_enemiga == self.prev_puntuacion_enemiga:
            recompensa += 0.1
        
        if self.estado_prev[2] == 1 and (self.estado_prev[7] == 0 or self.estado_prev[7] == 4) and self.accion_prev == "NONE": 
            recompensa -= 0.1
        if self.estado_prev[2] == 1 and self.estado_prev[7] == 0 and self.accion_prev == "UP": 
            recompensa += 0.1
        if self.estado_prev[2] == 1 and self.estado_prev[7] == 4 and self.accion_prev == "DOWN": 
            recompensa += 0.1
        '''    
        #[distancia_pelota,velocidad_pelota,acercandose,zona_vertical_enemigo,
        # zona_vertical_propia,zona_vertical_pelota,zona_horizontal_pelota,zona_impacto_pelota]
            
        
        return recompensa
    
    def play(self):
        HOST = self.IP
        PORT = self.puerto
        VENTANA_HORI = 800  # Ancho de la ventana
        VENTANA_VERT = 700
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(60)
        client_socket.connect((HOST, PORT))
        self.mi_puntuacion = 0
        self.puntuacion_enemiga = 0
        self.estado_prev = None
        self.accion_prev = None
        while True:
            
            data_start = client_socket.recv(512)
            
            # Decodificar la señal de inicio
            start = data_start.decode('ascii')
            start = start.split("$")
            #si acaba la partida
            if start[0] == "END":
                if id_raqueta == "0":
                    mi_puntuacion = start[1]
                    puntuacion_enemiga = start[2]
                else:
                    mi_puntuacion = start[2]
                    puntuacion_enemiga = start[1]
                print("Mi puntuacion es: ",mi_puntuacion)
                print("Puntuación enemiga: ",puntuacion_enemiga)
                break
            datos_raqueta = start[1]
            id_raqueta = datos_raqueta.split(" ")[1]
            x_raqueta = float(datos_raqueta.split(" ")[3].replace("(","").replace(",",""))
            y_raqueta = float(datos_raqueta.split(" ")[4].replace(")",""))
            datos_pelota = start[2]
            x_pelota = float(datos_pelota.split(" ")[2].replace("(","").replace(",",""))
            y_pelota = float(datos_pelota.split(" ")[3].replace(")",""))
            dir_x_pelota = float(datos_pelota.split(" ")[6].replace("(","").replace(",",""))
            dir_y_pelota = float(datos_pelota.split(" ")[7].replace(")",""))
            velocidad_pelota = int(datos_pelota.split("velocidad ")[1])
            datos_raqueta_enemiga = start[3]
           #x_raqueta_enemiga = float(datos_raqueta_enemiga.split(" ")[3].replace("(","").replace(",",""))
            y_raqueta_enemiga = float(datos_raqueta_enemiga.split(" ")[4].replace(")",""))
            
            if id_raqueta == "0":
                self.mi_puntuacion = int(start[5])
                self.puntuacion_enemiga = int(start[6])
            else:
                self.mi_puntuacion = int(start[6])
                self.puntuacion_enemiga = int(start[5])

            #PERCEPCIONES
            distancia_pelota = np.sqrt(np.power(x_pelota - x_raqueta,2) + np.power(y_pelota - y_raqueta,2))
            acercandose = int(distancia_pelota > np.sqrt(np.power((x_pelota + dir_x_pelota) - x_raqueta,2) + np.power((y_pelota + dir_y_pelota) - y_raqueta,2)))
            distancia_pelota = int(distancia_pelota // (VENTANA_HORI // 5))
            #dividimos el campo en 5 zonas verticales siendo 0 la mas arriba y 4 la mas baja hay que discretizar
            zona_vertical_enemigo = int(y_raqueta_enemiga // (VENTANA_VERT // 5))
            zona_vertical_propia = int(y_raqueta // (VENTANA_VERT // 5))
            zona_vertical_pelota = int(y_pelota // (VENTANA_VERT // 5))
            zona_horizontal_pelota = int(x_pelota // (VENTANA_HORI // 5))
            #0 = no impacta pasa por encima, 1 impacta en el centro de la raqueta, 2 arriba, 3 = zona baja, 4 no impacta pasa por abajo
            zona_impacto_pelota = 0
            if acercandose: #siempre s
                #SIMULAMOS TRAYECTORIAS
                aux_x = x_pelota
                aux_y = y_pelota
                dir_x_aux = dir_x_pelota
                dir_y_aux = dir_y_pelota
                
                if id_raqueta == "0":
                    count = 0
                    while aux_x > x_raqueta and dir_x_aux <= 0:
                        if(count >10000):
                            print("ERROR",aux_x, x_raqueta, dir_x_aux,dir_x_pelota, acercandose)
                            print(int(distancia_pelota > np.sqrt(np.power((x_pelota + dir_x_pelota) - x_raqueta,2) + np.power((y_pelota + dir_y_pelota) - y_raqueta,2))))
                            break
                        
                        aux_x += dir_x_aux- velocidad_pelota * 0.25
                        if dir_y_aux <= 0:
                            aux_y += dir_y_aux - velocidad_pelota * 0.25
                        else:
                            aux_y += dir_y_aux + velocidad_pelota * 0.25
                        if aux_y <= 0:
                            dir_y_aux = -dir_y_aux
                        if aux_y + 21 >= VENTANA_VERT:
                            dir_y_aux = -dir_y_aux
                        count += 1
                else:
                    count = 0
                    while aux_x < x_raqueta and dir_x_aux >= 0:
                        if(count >10000):
                            print("ERROR1",aux_x, x_raqueta, dir_x_aux)
                            break
                        if dir_x_aux>= 0:
                            aux_x += dir_x_aux+ velocidad_pelota * 0.25
                        if dir_y_aux <= 0:
                            aux_y += dir_y_aux - velocidad_pelota * 0.25
                        else:
                            aux_y += dir_y_aux + velocidad_pelota * 0.25
                        if aux_y <= 0:
                            dir_y_aux = -dir_y_aux
                        if aux_y + 21 >= VENTANA_VERT:
                            dir_y_aux = -dir_y_aux
                #LONGITUD VERTICAL de la raqueta es 108 tenemos 3 zonas luego 108 / 3 = 36
                #PENDIENTE
                zona_impacto_pelota = y_raqueta - aux_y
                if zona_impacto_pelota > 54:
                    zona_impacto_pelota = 0
                elif zona_impacto_pelota < -54:
                    zona_impacto_pelota = 4
                elif abs(zona_impacto_pelota) < 18:
                    zona_impacto_pelota = 1
                elif zona_impacto_pelota > 18:
                    zona_impacto_pelota = 3
                elif zona_impacto_pelota < 18:
                    zona_impacto_pelota = 2
            velocidad_pelota = 0
            self.estado = [distancia_pelota,
                           velocidad_pelota,
                           acercandose,
                           zona_vertical_enemigo,
                           zona_vertical_propia,
                           zona_vertical_pelota,
                            zona_horizontal_pelota,
                            zona_impacto_pelota]
            self.estado = tuple(self.estado)
            try:
                indice_Q = self.mapeado[self.estado]
            except: #Si el estado no esta mapeado
                self.mapeado[self.estado] = self.indice_actual_asignar
                indice_Q = self.indice_actual_asignar
                self.indice_actual_asignar += 1
            
            if self.estado_prev is not None: #Si no hay estado inicial
                recompensa = self.getRecompensa()
                self.actualizar_Q(recompensa)

            accion = self.acciones[self.seleccionar_accion(indice_Q)]
            self.estado_prev = self.estado
            self.accion_prev = accion
            self.prev_mi_puntuacion = self.mi_puntuacion
            self.prev_puntuacion_enemiga = self.puntuacion_enemiga
            
            message = "ACTION$"+accion+"$"+id_raqueta+"$END"
            while len(bytes(message, encoding="ascii")) < 50:
                message += "$"
            client_socket.send(bytes(message, encoding="ascii"))
            #print(self.estado)
            '''
            log = open("percepciones"+id_raqueta+".log","a")
            log.write(";".join(map(lambda x: str(x), [distancia_pelota,velocidad_pelota,acercandose,zona_vertical_enemigo,zona_vertical_propia,zona_vertical_pelota,
                                                    zona_horizontal_pelota,zona_impacto_pelota])) + "\n")
            log.close()
            '''
            #accion = random.choice(["UP","DOWN", "NONE"])
            
                
            

            
        client_socket.close()


def main():
    if len(sys.argv) != 4:
        print("Ejecución: client.py IP PUERTO MODELO")
        sys.exit()
    try:
        file = open(sys.argv[3], 'rb')
        agent = pickle.load(file)
        
    except:
        agent = agente()
    agent.set_connection(sys.argv[1],sys.argv[2])
    
    while True:
        agent.play()
        print(f"Dimensión matriz: {len(agent.mapeado)}")
        file = open(sys.argv[3], 'wb')
        pickle.dump(agent, file)
        file.close()
        time.sleep(0.1)
if __name__ == "__main__":
    main()
