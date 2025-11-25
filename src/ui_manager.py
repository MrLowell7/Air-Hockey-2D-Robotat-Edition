import pygame
from enum import Enum
import math

class GameState(Enum):
    RUNNING = 0
    PAUSED = 1
    RESET_WARNING = 2
    FINISHED = 3
    READY_GO = 4    # nuevo estado

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.RUNNING
        self.timer = 120 # segundos
        self.font = pygame.font.Font("../assets/VCR_MONO.ttf", 80)
        self.font_small = pygame.font.Font("../assets/VCR_MONO.ttf", 40)
        self.result_text = ""
        self.warning_active = False

        self.warning_type = None # 'center', 'player1', 'player2'

        # --- Cargar imágenes de advertencia ---
        self.warning_images = {}
        
        for key, filename in {
            "center": "warning_middlemarker.png",
            "player1": "warning_player1.png",
            "player2": "warning_player2.png",
        }.items():
            try:
                path = f"../assets/{filename}"
                self.warning_images[key] = pygame.transform.scale(
                    pygame.image.load(path).convert_alpha(),
                    (int(screen.get_width() * 0.4), int(screen.get_height() * 0.5))
                )
            except Exception as e:
                print(f"[WARN] No se pudo cargar {filename}: {e}")
                self.warning_images[key] = None


        # Overlay semitransparente (negro con opacidad)
        self.overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))  # RGBA con alpha = 150 (transparencia media)

    # ------------------------------------------------------
    def set_warning(self, warning_type: str):
        """Activa una advertencia específica: 'center', 'player1', 'player2'."""
        if warning_type not in ("center", "player1", "player2"):
            print(f"Tipo de advertencia inválido: {warning_type}")
            return
        
        #if self.warning_type == "center" and warning_type != "center":
        #    return
    
        self.warning_type = warning_type
        self.warning_active = True
        self.state = GameState.RESET_WARNING
        #print(f"[UIManager] set_warning -> {warning_type}")


    # ------------------------------------------------------
    def clear_warning(self):
        """Desactiva cualquier advertencia activa."""
        self.warning_active = False
        self.warning_type = None
        if self.state == GameState.RESET_WARNING:
            self.state = GameState.RUNNING
        #print("[UIManager] clear_warning()")
        
    # ------------------------------------------------------
    def draw_ready_go(self, text, color=(255, 255, 255), alpha=180):
        """Dibuja el overlay para la secuencia READY/GO."""
        self.draw_overlay(alpha=alpha)
        self.draw_center_text(text, self.font, color=color)
        #pygame.display.flip()

    # ------------------------------------------------------
    def update_timer(self, dt):
        if self.state == GameState.RUNNING:
            self.timer -= dt
            if self.timer <= 0:
                self.timer = 0
                self.state = GameState.FINISHED

    # ------------------------------------------------------
    def toggle_pause(self):
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING

    # ------------------------------------------------------
    def draw_overlay(self, alpha=180):
        """Dibuja un overlay semitransparente sobre la pantalla."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))  # alfa controla la opacidad
        self.screen.blit(overlay, (0, 0))

    # ------------------------------------------------------
    def draw_center_text(self, text, font, color=(255, 255, 255)):
        """Dibuja texto centrado en la pantalla."""
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(surf, rect)

    # ------------------------------------------------------
    def draw_timer(self):
        """Muestra el tiempo en formato MM:SS arriba al centro."""
        minutes = int(self.timer // 60)
        seconds = int(self.timer % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        surf = self.font_small.render(time_text, True, (255, 255, 255))
        rect = surf.get_rect(center=(self.screen.get_width() / 2, 30))
        self.screen.blit(surf, rect)

    # ------------------------------------------------------
    def draw(self, continue_timer=0):
        """Dibuja overlays y mensajes según el estado del juego."""
        if self.state == GameState.PAUSED:
            self.draw_overlay()
            # --- Efecto de parpadeo para 'PAUSED' ---
            blink_speed = 2.5  # ciclos por segundo
            blink = (math.sin(pygame.time.get_ticks() * 0.005 * blink_speed) + 1) / 2
            if blink > 0.5:
                self.draw_center_text("PAUSED", self.font)

        elif self.state == GameState.FINISHED:
            self.draw_overlay()

            if continue_timer > 3 and self.result_text != "GAME OVER":
                # --- Efecto de parpadeo para 'CONTINUE?' ---
                blink_speed = 3  # ciclos por segundo
                alpha = (math.sin(continue_timer * blink_speed * math.pi) + 1) / 2  # entre 0 y 1

                if alpha > 0.5:
                    self.draw_center_text("CONTINUE?", self.font)
            else:
                # Mostrar resultado o Game Over normalmente
                if self.result_text:
                    self.draw_center_text(self.result_text, self.font)
                else:
                    self.draw_center_text("GAME OVER", self.font)

        elif self.state == GameState.RESET_WARNING and self.warning_active:
            # print(f"[UI] Mostrando warning: {self.warning_type}")
            self.draw_overlay()
            image = self.warning_images.get(self.warning_type)
            if image:
                img_rect = image.get_rect(center=self.screen.get_rect().center)
                self.screen.blit(image, img_rect)
            else:
                self.draw_center_text("WARNING", self.font, (255, 100, 100))



