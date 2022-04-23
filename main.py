import math
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from game import Game
from gui import Display
from network import SlitherBot
from util import angle_to_mouse_coords

with open("getcanvas.js", "r") as f:
    canvas_script = f.read()


def loop_1000():
    while True:
        for i in range(1000):
            yield i


with webdriver.Firefox() as driver:
    driver.set_window_position(2000, 0)

    driver.get("http://slither.io")

    thousand_loop = loop_1000()

    with SlitherBot() as bot:
        display = Display()

        play_button = driver.find_element_by_xpath('//*[@id="playh"]/div/div/div[3]')
        play_button.click()

        while True:
            game = Game()
            display.set_game(game)

            previous_state, previous_radians, previous_boost = None, None, None

            epsilon = bot.get_epsilon(next(thousand_loop))

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
                        if previous_state is not None:
                            bot.feedback(previous_state,
                                         previous_radians,
                                         previous_boost,
                                         -game.snake_last_size,
                                         True, None)

                        print("Game ended.")
                        break

                    # We are playing
                    # Get bot action
                    state = bot.create_state(game)

                    # Give feedback to our bot for the last action
                    if previous_state is not None:
                        bot.feedback(previous_state, previous_radians, previous_boost, game.reward, False, state)

                    radians, boost = bot.choose_action(state, epsilon)

                    # Update window with bot output
                    nx, ny = angle_to_mouse_coords(radians * 2 * math.pi)
                    driver.execute_script(f"window.xm={round(nx, 4)};window.ym={round(ny, 4)};setAcceleration({int(boost > 0)})")

                    previous_state = state
                    previous_radians = radians
                    previous_boost = boost

                display.update()

                time.sleep(0.05)  # Update 20 times a second

            bot.save()

            # Quick respawn
            driver.execute_script("""
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
