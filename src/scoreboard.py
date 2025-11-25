import pygame
from pygame import Surface

ROWS, COLS = 7, 4

# Mapa de dígitos en una matriz 7x4
DIGIT_MAP = {
    "0": ["1111","1001","1001","1001","1001","1001","1111"],
    "1": ["0010","0110","0010","0010","0010","0010","0111"],
    "2": ["1111","0001","0001","1111","1000","1000","1111"],
    "3": ["1111","0001","0001","1111","0001","0001","1111"],
    "4": ["1001","1001","1001","1111","0001","0001","0001"],
    "5": ["1111","1000","1000","1111","0001","0001","1111"],
    "6": ["1111","1000","1000","1111","1001","1001","1111"],
    "7": ["1111","0001","0001","0001","0001","0001","0001"],
    "8": ["1111","1001","1001","1111","1001","1001","1111"],
    "9": ["1111","1001","1001","1111","0001","0001","1111"],
}


class DigitMatrix:
    def __init__(self, number, led_size=20, spacing=4):
        self.number = str(number)
        self.led_size = led_size
        self.spacing = spacing
        self.surface = self.render_digit()

    def render_digit(self) -> Surface:
        width = COLS * (self.led_size + self.spacing)
        height = ROWS * (self.led_size + self.spacing)
        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        pattern = DIGIT_MAP.get(self.number, DIGIT_MAP["0"])

        for row in range(ROWS):
            for col in range(COLS):
                x = col * (self.led_size + self.spacing)
                y = row * (self.led_size + self.spacing)
                rect = pygame.Rect(x, y, self.led_size, self.led_size)

                if pattern[row][col] == "1":
                    # LED exterior
                    pygame.draw.rect(surf, (255, 0, 0), rect, border_radius=4)
                    # LED interior
                    inner_size = int(self.led_size * 0.6)
                    offset = (self.led_size - inner_size) // 2
                    inner_rect = pygame.Rect(
                        x + offset, y + offset, inner_size, inner_size
                    )
                    pygame.draw.rect(surf, (253, 74, 44), inner_rect, border_radius=3)
                else:
                    pygame.draw.rect(surf, (50, 50, 50), rect, border_radius=4)

        return surf

    def draw(self, target: Surface, pos: tuple[int, int], scale=1.0):
        if scale != 1.0:
            scaled = pygame.transform.scale(
                self.surface,
                (int(self.surface.get_width() * scale),
                 int(self.surface.get_height() * scale))
            )
            target.blit(scaled, pos)
        else:
            target.blit(self.surface, pos)


class Scoreboard:
    def __init__(self, led_size=20, spacing=4):
        self.team1_score = 0
        self.team2_score = 0
        self.time_left =  120  # segundos (ej: 5 minutos)

        self.led_size = led_size
        self.spacing = spacing

    # ----- Lógica -----
    def set_score(self, team1: int, team2: int):
        self.team1_score = max(0, team1)
        self.team2_score = max(0, team2)

    def add_point(self, team: int):
        if team == 1:
            self.team1_score += 1
        elif team == 2:
            self.team2_score += 1

    def set_time(self, seconds: int):
        self.time_left = max(0, seconds)

    def tick(self, dt: float):
        """Resta tiempo (dt en segundos). Llamar cada frame."""
        self.time_left = max(0, self.time_left - dt)

    # ----- Render -----
    def draw_number(self, screen, number: int, pos, scale=1.0, max_display=99):
        """Dibuja un número de 2 dígitos (visual limitado a max_display)."""
        # limitar visualmente
        number = min(number, max_display)
        s = f"{number:02d}"  # 2 dígitos siempre
        x, y = pos
        for digit in s:
            d = DigitMatrix(digit, self.led_size, self.spacing)
            d.draw(screen, (x, y), scale)
            x += d.surface.get_width() * scale + 10

    def draw_time(self, screen, pos, scale=1.0):
        """Dibuja tiempo como MM  SS (con espacio para colocar ':' como imagen)."""
        minutes = int(self.time_left // 60)
        seconds = int(self.time_left % 60)
        m_str = f"{minutes:02d}"
        s_str = f"{seconds:02d}"

        x, y = pos

        # minutos
        for digit in m_str:
            d = DigitMatrix(digit, self.led_size, self.spacing)
            d.draw(screen, (x, y), scale)
            x += d.surface.get_width() * scale + 5

        # espacio grande para ":"
        x += 50 * scale

        # segundos
        for digit in s_str:
            d = DigitMatrix(digit, self.led_size, self.spacing)
            d.draw(screen, (x, y), scale)
            x += d.surface.get_width() * scale + 5

    def draw(self, screen, pos=(50,50), scale=1.0):
        """Dibuja marcador completo: SCORE1 TIME SCORE2"""
        x, y = pos

        # Equipo 1
        self.draw_number(screen, self.team1_score, (x + 296, y + 20), scale*1.2)

        # Tiempo en el centro
        self.draw_time(screen, (x + 386, y + 108), scale * 0.55)

        # Equipo 2
        self.draw_number(screen, self.team2_score, (x + 480, y + 20), scale*1.2)
