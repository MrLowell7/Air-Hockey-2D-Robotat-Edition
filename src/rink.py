import pygame
import pymunk
import math

class Rink:
    def __init__(self, space: pymunk.Space, x, y, width, height, corner_radius=150, wall_thickness=5):
        self.rect = pygame.Rect(x - 50, y + 130, width + 557, height + 420)
        self.corner_radius = corner_radius
        self.wall_thickness = wall_thickness

        body = space.static_body
        l, t, r, b = self.rect.left, self.rect.top, self.rect.right, self.rect.bottom

        walls = []

        # Lados rectos acortados (dejamos espacio para las esquinas)
        walls.append(pymunk.Segment(body, (l+corner_radius, t), (r-corner_radius, t), wall_thickness))  # arriba
        walls.append(pymunk.Segment(body, (r, t+corner_radius), (r, b-corner_radius), wall_thickness))  # derecha
        walls.append(pymunk.Segment(body, (r-corner_radius, b), (l+corner_radius, b), wall_thickness))  # abajo
        walls.append(pymunk.Segment(body, (l, b-corner_radius), (l, t+corner_radius), wall_thickness))  # izquierda

        # Esquinas redondeadas como arcos hechos de segmentos
        corners = [
            ((l+corner_radius, t+corner_radius), math.pi, 1.5*math.pi),   # arriba-izquierda
            ((r-corner_radius, t+corner_radius), 1.5*math.pi, 2*math.pi), # arriba-derecha
            ((r-corner_radius, b-corner_radius), 0, 0.5*math.pi),         # abajo-derecha
            ((l+corner_radius, b-corner_radius), 0.5*math.pi, math.pi),   # abajo-izquierda
        ]

        arc_segments = 20  # más segmentos = curva más suave
        for center, start_angle, end_angle in corners:
            cx, cy = center

            #Radio ligeramente más pequeño para suavizar la unión entre segmentos
            inner_r = corner_radius - wall_thickness * 0.5

            # Primer punto del arco (inicio del ángulo)
            prev = (
                cx + inner_r * math.cos(start_angle),
                cy + inner_r * math.sin(start_angle)
            )

            # Generar los segmentos del arco
            for i in range(1, arc_segments + 1):
                angle = start_angle + (end_angle - start_angle) * (i / arc_segments)
                point = (
                    cx + inner_r * math.cos(angle),
                    cy + inner_r * math.sin(angle)
                )

                seg = pymunk.Segment(body, prev, point, wall_thickness)
                seg.elasticity = 0.95
                seg.friction = 0.01
                seg.collision_type = 99

                walls.append(seg)
                prev = point
        
        # Configuración común
        for wall in walls:
            wall.elasticity = 0.95
            wall.friction = 0.01
            wall.collision_type = 99

        # Agregar todas las paredes de una sola vez
        space.add(*walls)

        self.walls = walls


    def draw_debug(self, screen):
        for wall in self.walls:
            if isinstance(wall, pymunk.Segment):
                p1 = wall.a
                p2 = wall.b
                pygame.draw.line(screen, (0, 255, 0), p1, p2, 2)
