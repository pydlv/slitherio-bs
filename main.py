import math
import random
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from game import Game
from gui import Display
from network import SlitherBot

with open("getcanvas.js", "r") as f:
    canvas_script = f.read()


def angle_to_mouse_coords(angle):
    x = math.cos(angle) * 1000
    y = math.sin(angle) * 1000
    return x, y


with webdriver.Firefox() as driver:
    driver.set_window_position(2000, 0)

    driver.get("http://slither.io")

    play_button = driver.find_element_by_xpath('//*[@id="playh"]/div/div/div[3]')
    play_button.click()

    bot = SlitherBot()

    game = Game()
    display = Display()

    display.set_game(game)

    while True:
        try:
            game_data = driver.execute_script(canvas_script)
        except StaleElementReferenceException:
            print("Driver is stale")
            time.sleep(1)
            continue

        game.update_from_game_data(game_data)

        if not game.game_started:
            print("Waiting for game to load.")
        else:
            if not game_data["playing"]:
                print("Game ended.")
                break

            # We are playing
            # Get bot action
            state = bot.create_state(game)

            radians, boost = bot.choose_action(state)

            print(radians, boost)

            # Update window with bot output
            nx, ny = angle_to_mouse_coords(radians)
            driver.execute_script(f"window.xm={nx};window.ym={ny};")

        display.update()

        time.sleep(0.05)  # Update 20 times a second
