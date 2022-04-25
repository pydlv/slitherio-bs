import os
import time

from common import IS_WINDOWS, LEARNING_RATE

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

import numpy as np
from stable_baselines3 import TD3, get_system_info
from stable_baselines3.common.noise import NormalActionNoise

from game_environment import SlitherioEnv


class CustomTD3(TD3):
    def train(self, gradient_steps: int, batch_size: int = 100) -> None:
        print("Training")

        super(CustomTD3, self).train(gradient_steps, batch_size)

        print("Saving model")
        self.save("snake_model")

        self.env.reset()


if __name__ == "__main__":
    get_system_info()

    with SlitherioEnv() as env:
        n_actions = env.action_space.shape[-1]
        action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        if os.path.exists("snake_model.zip"):
            print("Loading previous model")
            model = CustomTD3.load("snake_model", action_noise=action_noise, verbose=1, learning_rate=LEARNING_RATE)
            model.set_env(env)
        else:
            model = CustomTD3("CnnPolicy", env, action_noise=action_noise, verbose=1, learning_rate=LEARNING_RATE)

        # Train the agent
        if not IS_WINDOWS:
            model.learn(total_timesteps=int(2e5))
        else:
            # Watch trained agent
            env.reset()

            # Wait for the game to start
            while not env.playing:
                is_playing, size, reversed_angle = env.driver.get_game_data()
                env.playing = is_playing
                time.sleep(0.5)

            obs = env.driver.observation()
            while env.playing:
                action, _states = model.predict(obs)

                obs, rewards, dones, info = env.step(action)
