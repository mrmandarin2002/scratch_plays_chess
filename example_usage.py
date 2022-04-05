from time import sleep

from config import load_config
from consts import CONFIG_FILENAME
from credentials import load_credentials
from browser import Browser
from logs_manager import LogsManager


if __name__ == "__main__":

    config = load_config(CONFIG_FILENAME)

    credentials = load_credentials(config.credentials_filename)

    logs_manager = LogsManager(config.logs_filename)

    browser = Browser(credentials[0], "chromedriver", logs_manager)

    browser.login()

    try:
        browser.find_new_game("5 min")
    except Exception as e: # this went off once, still don't know why
        print(f"PROBLEM HAPPENED: {e}")

    sleep(3)
    if browser.playing_white:
        browser.move("h2h3")

    while True:
        browser.refresh_moves()
        print(browser.get_own_clock(), browser.get_opponent_clock())
        sleep(1)

    sleep(3600)
