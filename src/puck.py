import pygame
import pymunk

class Puck:
    def __init__(self, space: pymunk.Space, x, y, radius=15, mass=120, max_speed=1000, asset_path=None):
        self.radius = radius
        self.max_speed = max_speed
        inertia = pymunk.moment_for_circle(mass, 0, radius)

        self.body = pymunk.Body(mass, inertia)
        self.body.position = (x, y)

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.2   # rebote moderado
        self.shape.friction = 10      # buen rozamiento
        self.shape.collision_type = 1

        space.add(self.body, self.shape)

        # --- Imagen del puck ---
        if asset_path:
            self.image = pygame.image.load(asset_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (radius*2.5, radius*2.5))
        else:
            self.image = None

    def reset(self, x, y):
        """Reinicia el puck en el centro sin velocidad"""
        self.body.position = (x, y)
        self.body.velocity = (0, 0)

    def limit_speed(self):
        """Limita y amortigua la velocidad del puck."""
        vx, vy = self.body.velocity
        speed = (vx ** 2 + vy ** 2) ** 0.5
        if speed > self.max_speed:
            scale = self.max_speed / speed
            vx *= scale
            vy *= scale
        else:
            vx *= 0.995
            vy *= 0.995
        self.body.velocity = (vx, vy)

    def keep_inside_rink(self, rink):
        """Evita que el puck atraviese las paredes del rink o se quede pegado en esquinas."""
        x, y = self.body.position
        vx, vy = self.body.velocity

        rebound_damping = 0.92        # rebote con ligera pérdida de energía
        correction_strength = 0.6     # qué tan fuerte corrige si se incrusta en una pared
        extra_padding = 0.5           # pequeña separación adicional para evitar quedarse dentro

        for wall in rink.walls:
            if isinstance(wall, pymunk.Segment):
                ax, ay = wall.a
                bx, by = wall.b

                # Vector AB (dirección del segmento)
                abx = bx - ax
                aby = by - ay
                ab_len2 = abx**2 + aby**2

                # Proyección del punto puck sobre el segmento (clamp 0..1)
                apx = x - ax
                apy = y - ay
                t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab_len2))

                # Punto más cercano en el segmento
                nearest_x = ax + abx * t
                nearest_y = ay + aby * t

                # Vector desde el segmento hacia el puck
                dx = x - nearest_x
                dy = y - nearest_y
                dist = (dx * dx + dy * dy) ** 0.5
                min_dist = self.radius + wall.radius + extra_padding

                # Si está demasiado cerca o dentro del muro
                if dist < min_dist and dist > 0:
                    nx = dx / dist
                    ny = dy / dist

                    # Desplazar suavemente al puck fuera del muro
                    correction = (min_dist - dist) * correction_strength
                    x += nx * correction
                    y += ny * correction

                    # Rebote de velocidad (reflexión)
                    dot = vx * nx + vy * ny
                    vx -= 2 * dot * nx
                    vy -= 2 * dot * ny

                    # Pequeña amortiguación para estabilidad
                    vx *= rebound_damping
                    vy *= rebound_damping

                    # Límite superior de velocidad para evitar “saltos”
                    speed = (vx**2 + vy**2) ** 0.5
                    if speed > 1000:
                        factor = 1000 / speed
                        vx *= factor
                        vy *= factor

        # Aplicar nueva posición y velocidad
        self.body.position = (x, y)
        self.body.velocity = (vx, vy)

    def draw(self, screen):
        x, y = int(self.body.position.x), int(self.body.position.y)
        if self.image:
            rect = self.image.get_rect(center=(x, y))
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, (30, 30, 30), (x, y), self.radius*10)

    def draw_debug(self, screen):
        x, y = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(screen, (255, 0, 0), (x, y), self.radius, 1)
