from typing import List

from util import hex_color_to_rgb, dist2


class SnakePoint(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Snake(object):
    def __init__(self,
                 is_own_snake,
                 x, y,
                 color: (int, int, int),
                 points,
                 facing_angle,
                 *, size=None):
        self.is_own_snake = is_own_snake
        self.x = x
        self.y = y
        self.color = color
        self.points = [SnakePoint(point[0], point[1]) for point in points]
        self.num_points = len(self.points)
        self.head = self.points[-1]
        self.facing_angle = facing_angle
        self.size = size


class Food(object):
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size


class Game(object):
    def __init__(self):
        self.playing = False
        self.game_started = False
        self.snake = None
        self.snakes: List[Snake] = []
        self.foods: List[Food] = []
        self.snake_last_size = 10  # Variable to keep track of last snack size so we can accurately reward bot
        self.reward = None

    def update_from_game_data(self, game_data):
        self.playing = game_data["playing"]

        if not self.game_started and self.playing:
            self.game_started = self.playing

        # Populate snakes
        self.snakes = []

        my_x = None
        my_y = None

        to_relative_point = lambda x, y: (x - my_x, y - my_y)

        map_snake = lambda s, is_own_snake: Snake(
            is_own_snake,
            *to_relative_point(s["x"], s["y"]),
            hex_color_to_rgb(s["color"]),
            [to_relative_point(p["x"], p["y"]) for p in s["points"]],
            s["facing_angle"],
            size=(s["length"] if is_own_snake else None)
        )

        gd_snake = game_data["snake"]
        if gd_snake is None:
            self.snake = None
        else:
            my_x = gd_snake["x"]
            my_y = gd_snake["y"]

            self.snake = map_snake(gd_snake, True)
            self.snakes.append(self.snake)

            if self.snake_last_size:
                # Calculate reward and update last size
                self.reward = self.snake.size - self.snake_last_size - 0.01
                if self.reward < 0:
                    self.reward *= 2

            self.snake_last_size = self.snake.size

        for snake in game_data["snakes"]:
            if snake["x"] != my_x and snake["y"] != my_y:
                self.snakes.append(map_snake(snake, False))

        # Populate foods
        self.foods = [Food(*to_relative_point(v["x"], v["y"]), v["size"]) for v in game_data["foods"] if v is not None]

    def get_closest_snakes(self):
        my_position = (self.snake.x, self.snake.y)

        distances = {}

        for snake in self.snakes:
            if snake.is_own_snake:
                continue

            closest_distance = None
            for pt in snake.points:
                distance = dist2(*my_position, pt.x, pt.y)
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance

            distances[snake] = closest_distance

        return sorted(filter(lambda x: not x.is_own_snake, self.snakes), key=lambda s: distances[s])

    def get_closest_foods(self):
        return sorted(self.foods, key=lambda food: dist2(self.snake.x, self.snake.y, food.x, food.y))
