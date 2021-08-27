import math
from typing import Optional

import pygame

from game import Game

WIDTH = 1000
HEIGHT = 800

POINT_SIZE = 5  # 1 point in the game world = 5x5 pixels in pygame
DEFAULT_ZOOM = 1  # higher = more zoomed out


class Display(object):
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.flip()

        self.center_x = 0
        self.center_y = 0
        self.game: Optional[Game] = None

    def set_game(self, game: Game):
        self.game = game

    def get_zoom(self):
        # return DEFAULT_ZOOM + (len(self.game.snake.points) / 15)
        return 5

    def to_relative_point(self, x, y) -> (float, float):
        """
        Converts absolute point to relative point
        """
        zoom = self.get_zoom()
        return (x - self.center_x) / zoom + (WIDTH / 2), (y - self.center_y) / zoom + (HEIGHT / 2)

    def point_to_rect(self, x, y, point_size=POINT_SIZE) -> pygame.Rect:
        return pygame.Rect(x, y, point_size, point_size)

    def update(self):
        pygame.event.get()

        # Make sure we are playing and our snake is not None, otherwise, just render step
        if not self.game.playing or not self.game.snake:
            pygame.display.flip()
            return

        # Clear the previous screen
        self.screen.fill((0, 0, 0))

        # Update the current center of the screen to where our snake is
        self.center_x = self.game.snake.x
        self.center_y = self.game.snake.y

        # Draw all the snakes
        for snake in self.game.snakes:
            for point in snake.points:
                r_x, r_y = self.to_relative_point(point.x, point.y)
                pygame.draw.rect(self.screen, snake.color, self.point_to_rect(r_x, r_y))

            # Draw the snake heading line
            line_start = (snake.head.x, snake.head.y)
            line_length = 100 + 5 * snake.length
            line_end = (
                math.cos(snake.facing_angle) * line_length + line_start[0],
                math.sin(snake.facing_angle) * line_length + line_start[1]
            )
            pygame.draw.line(self.screen, snake.color, self.to_relative_point(*line_start),
                             self.to_relative_point(*line_end), 1)

        # Draw all the food
        for food in self.game.foods:
            r_x, r_y = self.to_relative_point(food.x, food.y)
            pygame.draw.rect(self.screen, (177, 177, 177), self.point_to_rect(r_x, r_y, point_size=3))

        pygame.display.flip()
