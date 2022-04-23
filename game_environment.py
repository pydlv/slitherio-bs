import time
import typing
from typing import Optional

import gym
import numpy as np
from gym import spaces

from common import OBSERVATION_SIZE
from game_driver import GameDriver
from util import angle_to_mouse_coords

TWO_PI = np.pi * 2


class SlitherioEnv(gym.Env):
    metadata = {'render.modes': []}

    driver: GameDriver
    last_snake_size: Optional[int]
    last_snake_angle = 0.0

    def __init__(self):
        super(SlitherioEnv, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Box(0, 1, shape=(1, 2))

        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(*OBSERVATION_SIZE, 3), dtype=np.uint8)

        self.driver = GameDriver()

    def step(self, action: typing.Any):

        # if len(action) == 1:
        #     # For some reason it sometimes omits the second value
        #     d, b = action[0][0], 0.0
        # else:
        try:
            d, b = action[0]
        except TypeError:
            # For some reason it randomly doesn't nest arrays occasionally
            d, b = action

        angle_adjustment = (d - 0.5) * np.pi

        new_angle = (self.last_snake_angle + angle_adjustment) % TWO_PI

        # print(f"Setting angle to {self.last_snake_angle} + d{angle_adjustment} = {new_angle}")

        # New mouse coords
        nx, ny = angle_to_mouse_coords(new_angle)
        boosting = b >= 0.5

        self.driver.take_action((nx, ny), boosting)

        observation = self.driver.observation()

        is_playing, size, reversed_angle = self.driver.get_game_data()

        if reversed_angle is not None:
            self.last_snake_angle = new_angle

        if is_playing:
            if self.last_snake_size is not None:
                reward = size - self.last_snake_size - 1
            else:
                # It's the 1st turn give no reward
                reward = 0
        else:
            if self.last_snake_size is not None:
                print("Detected game ended. Giving penalty")
                reward = -self.last_snake_size
            else:
                print("Stepped before game started...")
                reward = 0

        info = {"is_playing": is_playing, "size": size, "reward": reward}

        if is_playing:
            self.last_snake_size = size

        game_ended = not is_playing and self.last_snake_size is not None
        if reward < -1 or reward > 0:
            print("Got reward:", reward)

        return observation, reward, game_ended, info

    def reset(self):
        print("Resetting environment.")

        self.last_snake_size = None

        self.driver.respawn()

        return self.driver.observation()

    def render(self, mode='human'):
        print("Rendering for no apparent reason")

    def close(self):
        self.driver.close()