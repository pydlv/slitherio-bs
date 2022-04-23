import os
import random
import time
from typing import Tuple

import keras
import numpy as np
from keras import Sequential, backend
from keras.layers import Dense
from keras.optimizers import Adam

from game import Game, Snake
from util import spread


class SlitherBot(object):
    def __init__(self):
        self.gamma = 1.0
        self.alpha_decay = 0
        self.epsilon_min = 0.01
        self.epsilon = 0.3
        self.epsilon_decay = 1
        self.learning_rate = 1e-2

        if os.path.isfile("./model.h5"):
            self.model = keras.models.load_model('./model.h5')
        else:
            self.model = Sequential()
            self.model.add(Dense(150, input_dim=693, activation="relu"))
            self.model.add(Dense(25, activation="relu"))
            # self.model.add(Dense(150, activation="relu"))
            # self.model.add(Dense(75, activation="relu"))
            # self.model.add(Dense(37, activation="relu"))
            # self.model.add(Dense(16, activation="relu"))
            # self.model.add(Dense(8, activation="relu"))
            # self.model.add(Dense(4, activation="relu"))
            self.model.add(Dense(2, activation="sigmoid"))
            self.model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))

        backend.set_value(self.model.optimizer.lr, self.learning_rate)

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

        state = np.zeros(693)

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

        # Add our actual position to the state
        state[691] = game.snake.actual_pos_x
        state[692] = game.snake.actual_pos_y

        state = np.reshape(state, [1, 693])

        return state

    def get_epsilon(self, t):
        return self.epsilon
        # return max(self.epsilon_min, min(self.epsilon, 1.0 - math.log10((t + 1) * self.epsilon_decay)))

    def choose_action(self, inputs, epsilon: float) -> Tuple[float, float]:
        """
        Returns two floats one with the angle in radians and second binary 0 or 1 whether boost is activated
        :return:
        """
        if np.random.random() <= epsilon:
            # print(time.time(), "Random action", epsilon)
            return random.uniform(0, 1), -1

        o1, o2 = self.model.predict(inputs)[0]

        print(f"Normal action {o1}, {o2}")

        return o1, o2

    def feedback(self, state, radians, boost, reward, done, next_state):
        # Basically we want to fit it to the OPPOSITE action * reward
        if abs(reward) > 1:
            print("Got reward", reward)

        targets = [None, min(max(boost + reward, 0), 1)]

        # if done:
        #     radians_to_use = radians
        # else:
        #     next_prediction = self.model.predict(next_state)[0]
        #     radians_to_use = next_prediction[0]

        radians_to_use = radians

        target_radians = radians_to_use if reward > 0 else radians_to_use + 0.5
        target_radians %= 1

        targets[0] = target_radians

        targets_f = self.model.predict(state)
        targets_f[0][0] = targets[0]
        targets_f[0][1] = targets[1]

        print(f"Fitting to target {targets_f[0]}")

        self.model.fit(state, targets_f, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
