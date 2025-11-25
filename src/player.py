import pygame
import pymunk
import math

class Player:
    def __init__(self, space, x, y, radius=45, mass=200, asset_path=None):
        self.radius = radius
        self.mass = mass

        # Cuerpo kinemático
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = x, y

        # Círculo para colisiones
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.2
        self.shape.friction = 3
        self.shape.collision_type = 2

        space.add(self.body, self.shape)

        # --- Imagen del jugador ---
        if asset_path:
            self.image = pygame.image.load(asset_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (radius*3, radius*4))
        else:
            self.image = None

    def update(self, dt, rink, target_x=None, target_y=None):
        if target_x is None or target_y is None:
            target_x, target_y = self.body.position

        # Limitar target dentro del rect base
        target_x = max(rink.rect.left + self.radius,
                       min(rink.rect.right - self.radius, target_x))
        target_y = max(rink.rect.top + self.radius,
                       min(rink.rect.bottom - self.radius, target_y))

        # Ajustar target usando las walls
        for wall in rink.walls:
            if isinstance(wall, pymunk.Segment):
                ax, ay = wall.a
                bx, by = wall.b
                abx = bx - ax
                aby = by - ay
                apx = target_x - ax
                apy = target_y - ay
                ab_len2 = abx**2 + aby**2
                t = max(0, min(1, (apx*abx + apy*aby) / ab_len2))
                nearest_x = ax + abx * t
                nearest_y = ay + aby * t
                dx_n = target_x - nearest_x
                dy_n = target_y - nearest_y
                dist = math.hypot(dx_n, dy_n)
                min_dist = self.radius + wall.radius

                if dist < min_dist and dist > 0:
                    nx = dx_n / dist
                    ny = dy_n / dist
                    target_x += nx * (min_dist - dist)
                    target_y += ny * (min_dist - dist)

        dx = target_x - self.body.position.x
        dy = target_y - self.body.position.y
        self.body.velocity = (dx / dt, dy / dt)

    def draw(self, screen):
        x, y = self.body.position
        if self.image:
            rect = self.image.get_rect(center=(int(x), int(y)))
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, (0, 0, 200), (int(x), int(y)), self.radius)

    def draw_debug(self, screen, rink=None):
        x, y = self.body.position
        pygame.draw.circle(screen, (255, 0, 0), (int(x), int(y)), self.radius, 1)
