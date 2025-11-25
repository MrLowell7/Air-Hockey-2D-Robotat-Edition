import pygame
import pymunk

class Goal:
    def __init__(self, space, x, y, width, height, team: int):
        """
        team = 1 o 2 (equipo dueño de esta portería)
        La portería es un área rectangular invisible definida como shape estático en Pymunk.
        """
        self.team = team
        self.width = width 
        self.height = height 

        # cuerpo estático
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)

        # Polígono que define el área de gol
        vs = [
            (x - 1, y - 98),
            (x + width - 1, y - 98),
            (x + width - 1, y + height + 102),
            (x - 1, y + height + 102)
        ]
        self.shape = pymunk.Poly(self.body, vs)
        self.shape.sensor = True   # <- no bloquea el puck, solo detecta
        self.shape.collision_type = 10 + team  # cada portería tiene un tipo distinto

        space.add(self.body, self.shape)

    def draw_debug(self, screen):
        # Dibujamos solo para debug (azul)
        points = [(v[0], v[1]) for v in self.shape.get_vertices()]
        pygame.draw.polygon(screen, (0, 0, 255), points, 2)
