import os

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
            model = CustomTD3.load("snake_model", env=env, action_noise=action_noise, verbose=1)
        else:
            model = CustomTD3("CnnPolicy", env, action_noise=action_noise, verbose=1)

        # Train the agent
        model.learn(total_timesteps=int(2e5))

        # Save the agent
        model.save("snake_model")
