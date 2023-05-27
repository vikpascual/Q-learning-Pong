# pong_1_9.py: Mostrar puntuación de la partida

import random
import pygame
from pygame.locals import QUIT
import sys

# Constantes para la inicialización de la superficie de dibujo
VENTANA_HORI = 800  # Ancho de la ventana
VENTANA_VERT = 700  # Alto de la ventana
FPS = 240  # Fotogramas por segundo
BLANCO = (255, 255, 255)  # Color del fondo de la ventana (RGB)
NEGRO = (0, 0, 0)  # Color del texto (RGB)


class PelotaPong:
    def __init__(self, fichero_imagen):
        # --- Atributos de la Clase ---

        # Imagen de la Pelota
        self.imagen = pygame.image.load(fichero_imagen).convert_alpha()

        # Dimensiones de la Pelota
        self.ancho, self.alto = self.imagen.get_size()

        # Posición de la Pelota
        self.x = VENTANA_HORI / 2 - self.ancho / 2
        self.y = VENTANA_VERT / 2 - self.alto / 2

        # Dirección de movimiento de la Pelota
        self.dir_x = random.choice([-5, 5])
        self.dir_y = random.choice([-5, 5])

        # Puntuación de la pelota
        self.puntuacion = 0
        self.puntuacion_ia = 0

class RaquetaPong:
    def __init__(self):
        self.imagen = pygame.image.load("assets/jugador1.png").convert_alpha()

        # --- Atributos de la Clase ---

        # Dimensiones de la Raqueta
        self.ancho, self.alto = self.imagen.get_size()

        # Posición de la Raqueta
        self.x = 0
        self.y = VENTANA_VERT / 2 - self.alto / 2

        # Dirección de movimiento de la Raqueta
        self.dir_y = 0

def main():
    # Inicialización de Pygame
    pygame.init()

    # Inicialización de la superficie de dibujo (display surface)
    ventana = pygame.display.set_mode((VENTANA_HORI, VENTANA_VERT))
    
    pygame.display.set_caption("Pong")

    # Inicialización de la fuente
    fuente = pygame.font.Font(None, 60)

    pelota = PelotaPong("assets/pelota.png")

    repeticion = open(sys.argv[1],"r").readlines()
    raqueta_1 = RaquetaPong()
    raqueta_2 = RaquetaPong()

    for linea in repeticion:
        datos = linea.split("$")
        #actualizamos posiciones de raquetas
        raqueta_1.x = float(datos[0].split(",")[1])
        raqueta_2.x = float(datos[1].split(",")[1])
        raqueta_1.y = float(datos[0].split(",")[2])
        raqueta_2.y = float(datos[1].split(",")[2])
        pelota.x = float(datos[2].split(",")[0])
        pelota.y = float(datos[2].split(",")[1])
        pelota.puntuacion = datos[3].split(",")[0]
        pelota.puntuacion_ia = datos[3].split(",")[1]
        # Bucle principal
        ventana.fill(NEGRO)
        ventana.blit(pelota.imagen, (pelota.x, pelota.y))
        ventana.blit(raqueta_1.imagen, (raqueta_1.x, raqueta_1.y))
        ventana.blit(raqueta_2.imagen, (raqueta_2.x, raqueta_2.y))

        texto = f"{pelota.puntuacion} : {pelota.puntuacion_ia}"
        letrero = fuente.render(texto, False, BLANCO)
        ventana.blit(letrero, (VENTANA_HORI / 2 - fuente.size(texto)[0] / 2, 50))

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit()
    main()