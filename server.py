# pong_1_9.py: Mostrar puntuación de la partida

import random
import socket
from PIL import Image
import math
import sys
if len(sys.argv) != 2:
    sys.exit()
# Constantes para la inicialización de la superficie de dibujo
VENTANA_HORI = 800  # Ancho de la ventana
VENTANA_VERT = 700  # Alto de la ventana
FPS = 60  # Fotogramas por segundo
BLANCO = (255, 255, 255)  # Color del fondo de la ventana (RGB)
NEGRO = (0, 0, 0)  # Color del texto (RGB)


class PelotaPong:
    def __init__(self, fichero_imagen):
        # --- Atributos de la Clase ---

        # Imagen de la Pelota
        self.imagen = Image.open(fichero_imagen)

        # Dimensiones de la Pelota
        self.ancho, self.alto = self.imagen.size

        # Posición de la Pelota
        self.x = VENTANA_HORI / 2 - self.ancho / 2
        self.y = VENTANA_VERT / 2 - self.alto / 2

        # Dirección de movimiento de la Pelota
        self.dir_x = random.choice([-5, 5])
        self.dir_y = random.choice([-5, 5])

        # Puntuación de la pelota
        self.puntuacion = 0
        self.puntuacion_ia = 0

        #total rebotes en raqueta para la velocidad
        self.rebotes = 0
        self.media_rebotes_punto = 0

    def __str__(self):
        return f"Pelota en ({self.x}, {self.y}) con direccion ({self.dir_x}, {self.dir_y}) con velocidad {self.rebotes}"

    def mover(self):
        if self.dir_x <= 0:
            self.x += self.dir_x - self.rebotes * 0.25
        else:
            self.x += self.dir_x + self.rebotes * 0.25
        if self.dir_y <= 0:
            self.y += self.dir_y - self.rebotes * 0.25
        else:
            self.y += self.dir_y + self.rebotes * 0.25

    def rebotar(self):
        if self.x <= -self.ancho:
            self.reiniciar()
            self.puntuacion_ia += 1
        if self.x >= VENTANA_HORI:
            self.reiniciar()
            self.puntuacion += 1
        if self.y <= 0:
            self.dir_y = -self.dir_y
        if self.y + self.alto >= VENTANA_VERT:
            self.dir_y = -self.dir_y

    def reiniciar(self):
        self.x = VENTANA_HORI / 2 - self.ancho / 2
        self.y = VENTANA_VERT / 2 - self.alto / 2
        self.dir_x = -self.dir_x
        self.dir_y = random.choice([-5, 5])
        self.media_rebotes_punto += self.rebotes
        self.rebotes = 0
        


class RaquetaPong:
    def __init__(self,id):
        self.id = id
        self.imagen = Image.open("assets/jugador1.png")

        # --- Atributos de la Clase ---

        # Dimensiones de la Raqueta
        self.ancho, self.alto = self.imagen.size

        # Posición de la Raqueta
        self.x = 0
        self.y = VENTANA_VERT / 2 - self.alto / 2

        # Dirección de movimiento de la Raqueta
        self.dir_y = 0

    def __str__(self):
        return f"Raqueta {self.id} en ({self.x}, {self.y}) con direccion {self.dir_y}"
    
    def mover(self):
        self.y += self.dir_y
        if self.y <= 0:
            self.y = 0
        if self.y + self.alto >= VENTANA_VERT:
            self.y = VENTANA_VERT - self.alto

    def golpear(self, pelota):
        if (
            pelota.x < self.x + self.ancho
            and pelota.x > self.x
            and pelota.y + pelota.alto > self.y
            and pelota.y < self.y + self.alto
        ):
            # Calcular el punto donde golpeó la pelota en la pala
            hit_point = (pelota.y + pelota.alto/2) - (self.y + self.alto/2)
            
            # Normalizar el punto de golpe para que esté entre -1 y 1
            hit_point /= (self.alto/2)
            
            # Calcular el ángulo de rebote en función del punto de golpe
            MAX_ANGLE = 80
            angle = hit_point * MAX_ANGLE
            
            # Cambiar la dirección de la pelota y ajustar la velocidad
            pelota.dir_x = -pelota.dir_x
            pelota.dir_y = pelota.rebotes * 0.25 * math.sin(math.radians(angle))
            #velocidad
            pelota.rebotes += 1


def main(num_game):
    HOST = '127.0.0.1'  # dirección IP del servidor
    PORT = int(sys.argv[1])    # puerto del servidor
    MAX_CONNECTIONS = 2 # número máximo de conexiones permitidas
    # Crear un objeto socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Asignar la dirección y puerto al objeto socket
    server_socket.bind((HOST, PORT))

    # Habilitar el socket para aceptar conexiones
    server_socket.listen(MAX_CONNECTIONS)

    print(f"Servidor escuchando en {HOST}:{PORT}")

    # Esperar por conexiones
    sockets = []
    while len(sockets) < MAX_CONNECTIONS:
        # Aceptar una conexión entrante
        client_socket, client_address = server_socket.accept()
        print(f"Conexión aceptada desde {client_address}")
        # Agregar el socket a la lista de sockets
        sockets.append(client_socket)
    

    raquetas = []
    counter = 0 #id de jugador
    pelota = PelotaPong("assets/pelota.png")
    pelota.mover()
    pelota.rebotar()
    #pelota_bytes = pickle.dumps(pelota)

    for i in range(0,2):
        raqueta = RaquetaPong(i)
        raqueta.x = 60 #raqueta izquierda
        if i > 0:
            raqueta.x = VENTANA_HORI - 60 - raqueta.ancho
        #raqueta_bytes = pickle.dumps(raqueta)
        raquetas.append(raqueta)
        

    for sock in sockets:
        #intenté serializar el objeto raqueta y pelota con pickle y enviarlo por el socket, pero el tamaño variaba y era mayor de 1024
        message = "STATE$"+str(raquetas[counter])+"$"+str(pelota)+"$"+str(raquetas[counter-1])+"$END$"+str(pelota.puntuacion)+"$"+str(pelota.puntuacion_ia)+"$"
        while len(message) < 512:
            message += "E"
        counter +=1
       
        sock.send(bytes(message, encoding="ascii"))

    # Bucle principal
    jugando = True
    while jugando:
        for sock in sockets:
            data = sock.recv(50)
            
            # Decodificar el mensaje recibido
            accion = data.decode("ascii")
            
            accion = accion.split("$")
            # Procesar la acción del jugador
            if accion[1] == "UP":
                # Mover la paleta del jugador hacia arriba
                raquetas[int(accion[2])].dir_y = -5
                
            elif accion[1] == "DOWN":
                # Mover la paleta del jugador hacia abajo
                raquetas[int(accion[2])].dir_y = 5
            else:
                raquetas[int(accion[2])].dir_y = 0

        for raqueta in raquetas:
            raqueta.mover() 
            raqueta.golpear(pelota)
        pelota.mover()
        pelota.rebotar()
        if pelota.puntuacion + pelota.puntuacion_ia < 50:
            counter = 0
            linea_repeticion = ""
            for sock in sockets:    
                message = "STATE$"+str(raquetas[counter])+"$"+str(pelota)+"$"+str(raquetas[counter-1])+"$END$"+str(pelota.puntuacion)+"$"+str(pelota.puntuacion_ia)+"$"
                linea_repeticion += f"{raquetas[counter].id},{raquetas[counter].x},{raquetas[counter].y}$"
                while len(message) < 512:
                    message += "$"
                sock.send(bytes(message, encoding="ascii"))
                counter += 1
            
            linea_repeticion += f"{pelota.x},{pelota.y},{pelota.dir_x},{pelota.dir_y}${pelota.puntuacion},{pelota.puntuacion_ia}"
            repeticion = open(f"logs/p{num_game}.log","a")
            repeticion.write(linea_repeticion+"\n")
            repeticion.close()
        else:
            jugando = False
        
            message = "END$"+str(pelota.puntuacion)+"$"+str(pelota.puntuacion_ia)+"$"
            while len(message) < 512:
                    message += "E"
            for sock in sockets:
                sock.send(bytes(message, encoding="ascii"))
                sock.close()
            sockets = []
            server_socket.close()
            #acaba la partida recogemos stats
            repeticion = open(f"logs/p{num_game}.log","a")
            pelota.media_rebotes_punto = pelota.media_rebotes_punto / 10
            repeticion.write(f"{num_game};{pelota.media_rebotes_punto}\n")
            repeticion.close()

            
if __name__ == "__main__":
    num_game = 320
    while True:
        main(num_game)
        num_game += 1