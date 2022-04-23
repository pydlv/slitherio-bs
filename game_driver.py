from io import BytesIO
from typing import Tuple, Optional

import PIL.Image
import numpy as np
import pygame
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from common import OBSERVATION_SIZE, IS_WINDOWS

PYGAME_WINDOW_SIZE = (800, 800)

if IS_WINDOWS:
    pygame.init()
    screen = pygame.display.set_mode(PYGAME_WINDOW_SIZE)


with open("getcanvas.js", "r") as f:
    canvas_script = f.read()


class GameDriver(object):
    def __init__(self):
        if not IS_WINDOWS:
            options = Options()
            options.headless = True

            self.driver = webdriver.Firefox(
                executable_path="./geckodriver",
                options=options
            )
        else:
            self.driver = webdriver.Firefox()

        self.driver.set_window_position(2000, 0)
        self.driver.set_window_size(400, 400)

        self.reload_game()

    def reload_game(self):
        self.driver.get("http://slither.io")

        play_button = self.driver.find_element_by_xpath('//*[@id="playh"]/div/div/div[3]')
        play_button.click()

        self.driver.execute_script("""
                window.lbf.remove()
                window.lbh.remove()
                window.lbn.remove()
                window.lbp.remove()
                window.lbs.remove()
                """)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.driver.close()

    def respawn(self):
        self.driver.execute_script("""
                    window.dead_mtm = 0;
                    window.login_fr = 0;
                    window.forcing = true;
                    window.xm = Math.random();
                    window.ym = Math.random();
                    if (window.force_ip && window.force_port) {
                        window.forceServer(window.force_ip, window.force_port);
                    }
                    window.connect();
                    window.forcing = false;
                    """)

        # self.reload_game()

    def observation(self) -> np.ndarray:
        if IS_WINDOWS:
            screen.fill((0, 0, 0))
            for _ in pygame.event.get():
                pass

        png = self.driver.get_screenshot_as_png()

        bio = BytesIO(png)

        img = PIL.Image.open(bio)

        img = img.convert("RGB").resize(OBSERVATION_SIZE)

        img.save("intermediate.png")

        if IS_WINDOWS:
            upscaled = img.resize(PYGAME_WINDOW_SIZE)

            img_bytes = upscaled.tobytes()

            pygame_img = pygame.image.frombuffer(img_bytes, PYGAME_WINDOW_SIZE, "RGB")
            screen.blit(pygame_img, screen.get_rect())
            pygame.display.flip()

        # noinspection PyTypeChecker
        return np.asarray(img)

    def get_game_data(self) -> Tuple[bool, Optional[int], Optional[float]]:
        data = self.driver.execute_script(canvas_script)

        is_playing: bool = data["playing"]
        size: Optional[int] = data["snake"]["length"] if data["snake"] else None
        angle = data["snake"]["angle"] if data["snake"] else None

        return is_playing, size, angle

    def take_action(self, mouse_coords: Tuple, boosting: bool):
        nx, ny = mouse_coords
        self.driver.execute_script(f"window.xm={round(nx, 4)};window.ym={round(ny, 4)};setAcceleration({int(boosting)})")
