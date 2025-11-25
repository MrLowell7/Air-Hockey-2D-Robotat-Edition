import pygame
import pymunk
import math
from scoreboard import Scoreboard
from rink import Rink
from puck import Puck
from player import Player
from goal import Goal
from ui_manager import UIManager, GameState
import json
import paho.mqtt.client as mqtt
import threading
import numpy as np
import cv2

class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Espacio físico
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)

        # Fondo
        self.background = pygame.image.load("../assets/fondo.png").convert()
        self.background = pygame.transform.scale(self.background, screen.get_size())

        # Scoreboard
        self.scoreboard = Scoreboard(led_size=15, spacing=3)

        # --- Objetos de juego ---
        self.rink = Rink(self.space, 147, 101, 1167, 352, corner_radius=125)
        self.puck = Puck(self.space, self.rink.rect.centerx + 0, self.rink.rect.centery - 0, radius=15,
                        asset_path="../assets/puck.png")
        self.puck.shape.collision_type = 1

        self.players = [
            Player(self.space, 400, 610, asset_path="../assets/player1.png"),
            Player(self.space, 1500, 610, asset_path="../assets/player2.png")
        ]

        # Crear porterías (sensores)
        goal1_x = self.rink.rect.left
        goal1_y = self.rink.rect.centery - 50
        self.goal1 = Goal(self.space, goal1_x, goal1_y, 10, 100, team=2)

        goal2_x = self.rink.rect.right
        goal2_y = self.rink.rect.centery - 50
        self.goal2 = Goal(self.space, goal2_x - 8, goal2_y, 10, 100, team=1)

        # Configurar colisiones
        self.setup_collisions()

        # --- UI ---
        self.ui = UIManager(screen)
        self.debug = True

        # Variables auxiliares
        self.continue_timer = 0
        self.center_radius = 80  # radio para el warning
        self.pending_goal_team = None
        
    # ------------------------------------------------------
    def setup_collisions(self):
        """Configura todos los handlers de colisión."""
        # ---- Goles ----
        handler1 = self.space.add_collision_handler(1, self.goal1.shape.collision_type)
        handler1.begin = lambda arbiter, space, data: self.goal_scored(self.goal1.team) or True

        handler2 = self.space.add_collision_handler(1, self.goal2.shape.collision_type)
        handler2.begin = lambda arbiter, space, data: self.goal_scored(self.goal2.team) or True

        # ---- Puck vs Player ----
        def on_player_puck_collision(arbiter, space, data):
            player_shape, puck_shape = arbiter.shapes
            rel_vel = (puck_shape.body.velocity - player_shape.body.velocity).length

            if rel_vel < 100:  # impacto leve
                arbiter.elasticity = 0
                arbiter.friction = 1
            elif rel_vel < 200:  # medio
                arbiter.elasticity = 0.2
            else:  # fuerte
                arbiter.elasticity = 0.3
            return True

        handler = self.space.add_collision_handler(1, 2)  # 1=puck, 2=player
        handler.pre_solve = on_player_puck_collision
        
        handler_ghost = self.space.add_collision_handler(1, 99)  # puck vs player fantasma
        handler_ghost.pre_solve = lambda arbiter, space, data: False  # False = ignora la colisión

    # ------------------------------------------------------
    def goal_scored(self, team):
        """Marca que ocurrió un gol (diferido)."""
        self.pending_goal_team = team

    # ------------------------------------------------------
    def process_pending_goal(self):
        """Ejecuta el gol pendiente en un contexto seguro."""
        if self.pending_goal_team is not None:
            team = self.pending_goal_team
            self.pending_goal_team = None

            self.trigger_reset_warning()
            self.scoreboard.add_point(team)
            self.reset_puck()

    # ------------------------------------------------------
    def trigger_reset_warning(self):
        """Activa el estado de advertencia después de un gol."""
        self.ui.warning_active = True
        self.ui.state = GameState.RESET_WARNING

        # Detiene el puck y los jugadores
        self.puck.body.velocity = (0, 0)
        self.puck.body.angular_velocity = 0
        for p in self.players:
            p.body.velocity = (0, 0)

    # ------------------------------------------------------
    def reset_puck(self):
        """Resetea la posición del puck al centro."""
        self.puck.reset(self.rink.rect.centerx - 0, self.rink.rect.centery + 0)

    # ------------------------------------------------------
    def reset_game(self):
        """Reinicia todo el juego tras 'Continue'."""
        self.scoreboard.set_score(0, 0)
        
        self.ui.timer = 120
        self.scoreboard.set_time(self.ui.timer)

        self.ui.state = GameState.RUNNING
        self.ui.result_text = ""
        self.continue_timer = 0
        self.reset_puck()
        
    # ------------------------------------------------------
# ------------------------------------------------------
    def check_initial_positions(self):
        """Verifica si los jugadores están en su lado correcto al iniciar el juego."""
        
        # Actualizar player a posición actual del mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cx, cy = self.rink.rect.center
        
        for player in self.players:
            player.body.position = (mouse_x, mouse_y)
            player.body.velocity = (0, 0)
            player.shape.collision_type = 2  # restaurar colisiones normales

        dist1 = math.hypot(self.players[0].body.position.x - cx, self.players[0].body.position.y - cy)
        dist2 = math.hypot(self.players[1].body.position.x - cx, self.players[1].body.position.y - cy)
        
        # Si alguno está dentro del área central
        if dist1 < self.center_radius + 25 or dist2 < self.center_radius + 25:
            self.ui.set_warning("center")
            return False

        # Si player1 está en el lado derecho
        if self.players[0].body.position.x >= cx:
            self.ui.set_warning("player1")
            return False

        # Si player2 está en el lado izquierdo
        #if self.players[1].body.position.x < cx:
        #    self.ui.set_warning("player2")
        #    return False

        # Si todo está correcto
        self.ui.clear_warning()
        return True

    # ------------------------------------------------------
    def handle_reset_warning(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cx, cy = self.rink.rect.center
        
        dist = math.hypot(mouse_x - cx, mouse_y - cy)
        
        if dist > self.center_radius + 25:
            # Si hay un warning distinto del centro activo, no hacer nada
            if self.ui.warning_active and self.ui.warning_type in ("player1", "player2"):
                return
            
            self.ui.warning_active = False
            self.ui.state = GameState.RUNNING

            self.reset_puck()

            # Actualizar player a posición actual del mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for player in self.players:
                player.body.position = (mouse_x, mouse_y)
                player.body.velocity = (0, 0)
                player.shape.collision_type = 2  # restaurar colisiones normales

        else:
            # Dentro del área → puck congelado
            self.ui.set_warning("center")

    # ------------------------------------------------------
    def handle_victory_input(self):
        """Maneja el input durante la pantalla de 'Continue?'."""
        # Bloquea entrada durante los primeros 3 segundos
        if self.continue_timer < 3:
            return None

        keys = pygame.key.get_pressed()

        # ENTER → reiniciar partida
        if keys[pygame.K_RETURN]:
            self.reset_game()
            self.ui.state = GameState.RUNNING
            return "restart"

        # ESC → terminar completamente
        elif keys[pygame.K_ESCAPE]:
            self.ui.result_text = "GAME OVER"
            self.continue_timer = 0
            self.ui.state = GameState.FINISHED
            return "game_over"

        return None

    # ------------------------------------------------------
    def finish_game(self):
        """Determina el ganador y muestra el resultado."""
        score1 = self.scoreboard.team1_score
        score2 = self.scoreboard.team2_score
        if score1 > score2:
            self.ui.result_text = "PLAYER 1 WINS"
        elif score2 > score1:
            self.ui.result_text = "PLAYER 2 WINS"
        else:
            self.ui.result_text = "TIE"
        self.ui.state = GameState.FINISHED
        self.continue_timer = 0

    # ------------------------------------------------------
    def update(self, dt: float):
        self.ui.update_timer(dt)

        # Final del tiempo → determinar resultado
        if self.ui.state == GameState.FINISHED and not self.ui.result_text:
            self.finish_game()

        # Procesar goles pendientes
        self.process_pending_goal()

        # Flujo por estado
        if self.ui.state == GameState.RUNNING:
            self.scoreboard.tick(dt)
            steps = 15
            dt_step = dt / steps
            for _ in range(steps):
                self.space.step(dt_step)

            # Limitar velocidad y mantener dentro del rink
            self.puck.limit_speed()
            self.puck.keep_inside_rink(self.rink)

            # Control del jugador con mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.players[0].update(dt, self.rink, mouse_x, mouse_y)

        elif self.ui.state == GameState.RESET_WARNING:
            self.handle_reset_warning()

        elif self.ui.state == GameState.FINISHED and self.ui.result_text != "GAME OVER":
            self.continue_timer += dt
            if self.continue_timer > 3:
                self.handle_victory_input()

    # ------------------------------------------------------
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.scoreboard.draw(self.screen, pos=(525, 70), scale=0.45)

        self.puck.draw(self.screen)
        for p in self.players:
            p.draw(self.screen)
            #if self.debug:
            #    p.draw_debug(self.screen, self.rink) #Los draw debug son las hitboxes
        
        #if self.debug:
            #self.rink.draw_debug(self.screen)
            #self.puck.draw_debug(self.screen)
            #self.goal1.draw_debug(self.screen)
            #self.goal2.draw_debug(self.screen)

        #self.ui.draw_timer()
        self.ui.draw(continue_timer=self.continue_timer)
        pygame.display.flip()

    # ------------------------------------------------------
    def run(self):
        running = True 
        initial_check_done = False 
        ready_go_stage = "ready"

        while running:
            dt = self.clock.tick(60) / 1000.0 

            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    running = False 

                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_q: 
                        self.scoreboard.add_point(1) 
                    if event.key == pygame.K_w: 
                        self.scoreboard.add_point(2) 
                    if event.key == pygame.K_d: 
                        self.debug = not self.debug 
                    if event.key == pygame.K_ESCAPE: 
                        self.ui.toggle_pause() 
                    if event.key == pygame.K_r: 
                        self.reset_game()
                        ready_go_stage = "ready"
                        self.ui.state = GameState.FINISHED

            # --- Pantalla de Victoria / Continue ---
            if self.ui.state == GameState.FINISHED:
                
                self.continue_timer += dt       # Avanza el contador mientras esté en pantalla de victoria
                
                action = self.handle_victory_input()
                if action == "restart":
                    initial_check_done = False  # volver a verificar posiciones iniciales
                    ready_go_stage = "ready"
                elif action == "game_over":
                    continue                    #running = False si se quiere terminar el game
                self.draw()
                pygame.display.flip()
                continue  # evitar actualizar física en este estado

            # --- Comprobación inicial ---
            if not initial_check_done:
                # --- Secuencia READY / GO (solo una vez) ---
                ready_go_timer = 0
                clock = pygame.time.Clock()

                while ready_go_stage != "done":
                    dt_ready = clock.tick(60) / 1000.0
                    ready_go_timer += dt_ready

                    # Redibuja fondo + jugadores + disco completo en cada frame
                    self.screen.blit(self.background, (0, 0))
                    self.scoreboard.draw(self.screen, pos=(525, 70), scale=0.45)
                    self.puck.draw(self.screen)
                    for p in self.players:
                        p.draw(self.screen)
                        
                    # Overlay semitransparente
                    if ready_go_stage == "ready":
                        self.ui.draw_overlay(alpha=180)
                        intensity = min(255, int((ready_go_timer / 0.5) * 255))  # sube en 0.5 s
                        self.ui.draw_center_text("READY?", self.ui.font, color=(intensity, intensity, intensity))
                        pygame.display.flip()

                        if ready_go_timer > 1.5:
                            ready_go_stage = "go"
                            ready_go_timer = 0

                    elif ready_go_stage == "go":
                        self.ui.draw_overlay(alpha=180)
                        self.ui.draw_center_text("GO!", self.ui.font, color=(0, 255, 100))
                        pygame.display.flip()

                        if ready_go_timer > 1.0:
                            ready_go_stage = "done"
                            
                # --- Ahora sí, verificar posiciones ---
                if self.check_initial_positions():
                    initial_check_done = True
                    print("Jugadores listos, inicia el juego.")
                    self.state = GameState.RUNNING
                    self.ui.state = GameState.RUNNING

                # siempre dibuja la escena mientras esperan posicionarse
                self.draw()
                pygame.display.flip()
                continue

            # --- Juego normal ---
            self.update(dt)
            self.draw()
            pygame.display.flip()

