import math
import os
import random
from typing import Tuple, List, Union

import keras
import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from game import Game, Snake
from util import spread


class ActionHistoryItem(object):
    def __init__(self, state, radians: float, boost: Union[bool, int], reward: float):
        self.state = state
        self.radians = radians
        self.boost = boost
        self.reward = reward


class SlitherBot(object):
    def __init__(self):
        self.gamma = 1.0
        self.alpha_decay = 0.01
        self.epsilon_min = 0.01
        self.epsilon = 1.0
        self.epsilon_decay = 0.995

        if os.path.isfile("./model.h5"):
            self.model = keras.models.load_model('./model.h5')
        else:
            self.model = Sequential()
            self.model.add(Dense(691, input_dim=691, activation="relu"))
            self.model.add(Dense(691, activation="relu"))
            self.model.add(Dense(950, activation="relu"))
            self.model.add(Dense(1190, activation="relu"))
            # self.model.add(Dense(150, activation="relu"))
            # self.model.add(Dense(75, activation="relu"))
            # self.model.add(Dense(37, activation="relu"))
            # self.model.add(Dense(16, activation="relu"))
            # self.model.add(Dense(8, activation="relu"))
            # self.model.add(Dense(4, activation="relu"))
            self.model.add(Dense(2, activation="sigmoid"))
            self.model.compile(loss="mse", optimizer=Adam(lr=0.01, decay=self.alpha_decay))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

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

        state = np.zeros(691)

        # Add our snake
        state[0:39] = self.create_snake_state(game.snake)

        # Add in the snake info
        start = 40

        for snake in closest_snakes:
            state[start:start+39] = self.create_snake_state(snake)
            start += 39

        missing_snakes = 9 - len(closest_snakes)
        start += 39 * missing_snakes

        # Add in food info
        for food in closest_foods:
            state[start] = food.x
            state[start + 1] = food.y
            state[start + 2] = food.size

            start += 3

        # Add our size to state
        state[690] = game.snake.size

        return state

    def get_epsilon(self, t):
        return max(self.epsilon_min, min(self.epsilon, 1.0 - math.log10((t + 1) * self.epsilon_decay)))

    def choose_action(self, inputs: List[float], epsilon: float) -> Tuple[float, bool]:
        """
        Returns two floats one with the angle in radians and second binary 0 or 1 whether boost is activated
        :return:
        """
        if np.random.random() <= epsilon:
            return random.uniform(0, 1) * 2 * np.pi, random.choice((True, False))

        inputs = np.reshape(inputs, [1, 691])

        o1, o2 = self.model.predict(inputs)[0]

        return o1 * 2 * np.pi, bool(np.round(o2))

    def feedback(self, state, reward, done, next_state):
        targets = [reward, reward]
        if not done:
            next_prediction = self.model.predict(next_state)[0]
            targets = [
                reward + self.gamma * j for j in next_prediction
            ]

        targets_f = self.model.predict(state)
        targets_f[0][0] = targets[0]
        targets_f[0][1] = targets[1]

        self.model.fit(state, targets_f)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
