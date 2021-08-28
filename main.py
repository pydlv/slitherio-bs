import math
import random
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from game import Game
from gui import Display
from network import SlitherBot, ActionHistoryItem

with open("getcanvas.js", "r") as f:
    canvas_script = f.read()


def angle_to_mouse_coords(angle):
    x = math.cos(angle) * 1000
    y = math.sin(angle) * 1000
    return x, y


def loop_1000():
    while True:
        for i in range(1000):
            yield i


with webdriver.Firefox() as driver:
    driver.set_window_position(2000, 0)

    driver.get("http://slither.io")

    epsilon_loop = loop_1000()

    with SlitherBot() as bot:
        display = Display()

        play_button = driver.find_element_by_xpath('//*[@id="playh"]/div/div/div[3]')
        play_button.click()

        while True:
            game = Game()
            display.set_game(game)

            previous_state = None

            epsilon = next(epsilon_loop)

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
                        # Provide final feedback to our bot
                        if previous_state:
                            bot.feedback(previous_state, -game.snake_last_size, True, None)

                        print("Game ended.")
                        break

                    # We are playing
                    # Get bot action
                    state = bot.create_state(game)

                    # Give feedback to our bot for the last action
                    if previous_state:
                        bot.feedback(previous_state, game.reward, False, state)

                    radians, boost = bot.choose_action(state, epsilon)

                    # Update window with bot output
                    nx, ny = angle_to_mouse_coords(radians)
                    driver.execute_script(f"window.xm={nx};window.ym={ny};setAcceleration({int(boost)})")

                display.update()

                time.sleep(0.05)  # Update 20 times a second

            bot.save()

            # Quick respawn
            driver.execute_script("""
            window.dead_mtm = 0;
            window.login_fr = 0;
            window.forcing = true;
            if (window.force_ip && window.force_port) {
                window.forceServer(window.force_ip, window.force_port);
            }
            window.connect();
            window.forcing = false;
            """)
