from browser import Browser
from engine_wrapper import EngineWrapper

from exceptions import NoChallenges, InExistingGame


class Bot:

    def __init__(self,
        browser: Browser,
        engine_wrapper: EngineWrapper
    ):
        self.browser = browser
        self.engine_wrapper = engine_wrapper

    def new_game(self, time_category: str, win: bool) -> None:
        if self.browser.in_game:
            raise InExistingGame("Browser object already in a game")

        self.browser.find_new_game(time_category)
        self.play(win)


    def challenge(self, username: str, time_category: str) -> None:
        # initiate a challenge to a given username for a game with a given time category
        pass

    def accept_challenge(self) -> None:
        # accept the current challenge
        pass

    def feed(self, username: str) -> None:
        # wait for challenge from username then accept the game and lose
        pass


    def play(self, win: bool) -> None:
        playing = True
        while playing:
            try:
                pass
            except KeyboardInterrupt:
                playing = False
