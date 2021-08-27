import os
from typing import Tuple, List

import keras
import numpy as np
from keras import Sequential
from keras.layers import Dense

from game import Game, Snake
from util import spread


class SlitherBot(object):
    def __init__(self):
        if os.path.isfile("./model.h5"):
            keras.models.load_model('./model.h5')
        else:
            self.model = Sequential()
            self.model.add(Dense(690, input_dim=690, activation="relu"))
            self.model.add(Dense(690, activation="relu"))
            self.model.add(Dense(950, activation="relu"))
            self.model.add(Dense(1190, activation="relu"))
            # self.model.add(Dense(150, activation="relu"))
            # self.model.add(Dense(75, activation="relu"))
            # self.model.add(Dense(37, activation="relu"))
            # self.model.add(Dense(16, activation="relu"))
            # self.model.add(Dense(8, activation="relu"))
            # self.model.add(Dense(4, activation="relu"))
            self.model.add(Dense(2, activation="sigmoid"))

    def save(self):
        self.model.save('./model.h5')

    def create_snake_state(self, snake: Snake):
        result = np.zeros(39)

        result[0] = snake.facing_angle

        points = spread(snake.points, 19)

        for i, point in enumerate(points):
            result[i * 2 + 1] = point.x
            result[i * 2 + 2] = point.y

        return result

    def create_state(self, game: Game):
        closest_snakes = game.get_closest_snakes()[:10]
        closest_foods = game.get_closest_foods()[:100]

        state = np.zeros(690)

        # Add our snake
        state[0:39] = self.create_snake_state(game.snake)

        # Add in the snake info
        start = 40

        for snake in closest_snakes:
            state[start:start+39] = self.create_snake_state(snake)
            start += 40

        missing_snakes = 9 - len(closest_snakes)
        start += 40 * missing_snakes

        # Add in food info
        for food in closest_foods:
            state[start] = food.x
            state[start + 1] = food.y
            state[start + 2] = food.size

            start += 4

        return state

    def choose_action(self, inputs: List[float]) -> Tuple[float, bool]:
        """
        Returns two floats one with the angle in radians and second binary 0 or 1 whether boost is activated
        :return:
        """
        assert len(inputs) == 690

        inputs = np.reshape(inputs, [1, 690])

        o1, o2 = self.model.predict(inputs)[0]

        return o1 * 2 * np.pi, bool(np.round(o2))

    def replay(self):
        ...
