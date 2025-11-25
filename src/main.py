import pygame
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Air Hockey 2D")

    game = Game(screen)
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()
