from functools import reduce
from time import sleep

from typing import Union, List, Tuple

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from undetected_chromedriver import Chrome

from credentials import Credentials
from consts import (
    DDOS_PROTECTION_TEXT,
    LOGIN_PAGE,
    USERNAME_INPUT_PLACEHOLDER,
    PASSWORD_INPUT_PLACEOHLDER,
    LOGIN_BUTTON_TEXT,
    LOGIN_PAGE_TEXT,
    NEW_GAME_PAGE,
    PLAY_BUTTON_TEXT,
    TIME_CATEGORIES,
    MATCHMAKING_TEXT,
    SKIP_TRIAL_BUTTON_TEXT,
    FAIR_PLAY_TEXT,
    FAIR_PLAY_BUTTON_TEXT
)
from logs_manager import LogsManager
from exceptions import ElementNotFound


def get_page_text(webdriver: Chrome):
    return webdriver.find_element("tag name", "html").text


def in_page_text(
    text: Union[str, List[str]],
    webdriver: Chrome,
    case_sensitive: bool=True
) -> bool:
    page_text = get_page_text(webdriver)

    if not case_sensitive:
        page_text = page_text.lower()
        if type(text) == str:
            text = text.lower()
        else:
            text = [s.lower() for s in text]

    if type(text) == str:
        return text in page_text
    else:
        return reduce(
            lambda x, y: x and y,
            [s in page_text for s in text],
            True
        )


def click_element(tag_name: str, text: str, webdriver: Chrome) -> None:
    for element in webdriver.find_elements("tag name", tag_name):
        if element.text == text:
            element.click()
            return
    e_text = f"Could not find <{tag_name}> tag with text: \"{text}\""
    raise ElementNotFound(e_text)


def type_in_element(placeholder: str, x: str, webdriver: Chrome) -> None:
    for element in webdriver.find_elements("tag name", "input"):
        if element.get_attribute("placeholder") == placeholder:
            element.send_keys(x)
            return
    raise ElementNotFound(
        f"Could not find input element with placeholder: \"{placeholder}\""
    )


class Browser:

    def __init__(
        self,
        credentials: Credentials,
        executable_path: str,
        logs_manager: LogsManager
    ):
        self.credentials = credentials

        options = Options()
        options.add_argument("--disable-notifications")
        self.webdriver = Chrome(
            options=options,
            executable_path=executable_path
        )

        self.logs_manager = logs_manager

        self.in_game = False
        self.game_id = 0
        self.opponent = ""
        self.opponent_rating = 0
        self.playing_white = True
        self.board_element = None
        self.board_position = None
        self.board_w = None
        self.board_h = None

        self.moves = []


    def bypass_ddos_protection(self) -> None:
        while in_page_text(DDOS_PROTECTION_TEXT, self.webdriver): sleep(1)


    def login(self) -> None:
        self.webdriver.get(LOGIN_PAGE)

        self.bypass_ddos_protection()

        if in_page_text(LOGIN_PAGE_TEXT, self.webdriver):

            type_in_element(
                USERNAME_INPUT_PLACEHOLDER,
                self.credentials.username,
                self.webdriver
            )
            type_in_element(
                PASSWORD_INPUT_PLACEOHLDER,
                self.credentials.password,
                self.webdriver
            )

            click_element("button", LOGIN_BUTTON_TEXT, self.webdriver)
            self.bypass_ddos_protection()

        if in_page_text(SKIP_TRIAL_BUTTON_TEXT, self.webdriver):
            click_element("button", SKIP_TRIAL_BUTTON_TEXT, self.webdriver)


    def parse_opponent_tagline(self) -> Tuple[str, int]:

        username = self.webdriver.find_element(
            "css selector",
            "a.user-username-dark"
        ).text

        rating = self.webdriver.find_element(
            "css selector",
            "span.user-tagline-rating.user-tagline-dark"
        )

        return username, rating


    def new_game(self) -> None:

        self.playing_white = "clock-black" in self.webdriver.find_element(
            "css selector",
            "div.clock-top"
        ).get_attribute("class")

        self.opponent, self.opponent_rating = self.parse_opponent_tagline()

        self.board_element = self.webdriver.find_element(
            "tag name", "chess-board"
        )
        self.board_position = self.board_element.location.values()
        self.board_w, self.board_h = self.board_element.size.values()

        self.game_id = self.logs_manager.start_game(
            self.opponent, self.playing_white
        )
        self.in_game = True


    def find_new_game(self, time_category: str) -> None:
        self.webdriver.get(NEW_GAME_PAGE)

        if in_page_text(FAIR_PLAY_TEXT, self.webdriver):
            click_element("button", FAIR_PLAY_BUTTON_TEXT, self.webdriver)

        if in_page_text(time_category, self.webdriver):
            click_element("button", PLAY_BUTTON_TEXT, self.webdriver)
        else:
            for c in TIME_CATEGORIES:
                try:
                    click_element("button", c, self.webdriver)
                    break
                except ElementNotFound:
                    pass

            sleep(1)

            click_element("button", time_category, self.webdriver)

            sleep(1)

            click_element("button", PLAY_BUTTON_TEXT, self.webdriver)

        while not in_page_text(MATCHMAKING_TEXT, self.webdriver): pass
        while in_page_text(MATCHMAKING_TEXT, self.webdriver): pass
        sleep(1)

        self.new_game()


    def get_offset(self, tile: str) -> Tuple[int, int]:
        tile = str(ord(tile[0])-96) + tile[1]
        h, v = list(tile)
        h = int(h) - 1
        v = int(v) - 1
        if self.playing_white:
            v = (v - 7) * -1
        else:
            h = (h - 7) * -1
        return (
            self.board_w / 16 + self.board_w / 8 * h,
            self.board_h / 16 + self.board_h / 8 * v
        )


    def move(self, move: str, delay: float=0.0) -> None:
        move = move.lower()

        tile_1 = move[0:2]
        tile_2 = move[2: ]

        tile_1_offsets = self.get_offset(tile_1)
        tile_2_offsets = self.get_offset(tile_2)

        action_1 = ActionChains(self.webdriver)
        action_1.move_to_element_with_offset(
            self.board_element,
            tile_1_offsets[0],
            tile_1_offsets[1]
        )
        action_2 = ActionChains(self.webdriver)
        action_2.click()
        action_3 = ActionChains(self.webdriver)
        action_3.move_to_element_with_offset(
            self.board_element,
            tile_2_offsets[0],
            tile_2_offsets[1]
        )
        action_4 = ActionChains(self.webdriver)
        action_4.click()
        action_1.perform()
        action_2.perform()
        sleep(delay)
        action_3.perform()
        action_4.perform()
        self.logs_manager.move(self.game_id, move)


    def refresh_moves(self) -> None:
        self.moves = []
        for move_row in self.webdriver.find_elements("css selector", "div.move"):
            white_moves = move_row.find_elements("css selector", "div.white.node")
            if white_moves:
                white_node = white_moves[0]
                white_move = white_node.text
                node_html = white_node.get_attribute("innerHTML")
                if "figurine" in node_html:
                    white_move = node_html.split("figurine=\"")[1].split("\"")[0] + white_move
                self.moves.append(white_move)

            black_moves = move_row.find_elements("css selector", "div.black.node")
            if black_moves:
                black_node = black_moves[0]
                black_move = black_node.text
                node_html = black_node.get_attribute("innerHTML")
                if "figurine" in node_html:
                    black_move = node_html.split("figurine=\"")[1].split("\"")[0] + black_move
                self.moves.append(black_move)


    def await_opponent_move(self) -> str:

        moves_len = len(self.moves)

        while len(self.moves) == moves_len:
            self.refresh_moves()

        self.logs_manager.move(self.game_id, self.moves[-1])
        return self.moves[-1]


    def parse_clock_time(self, clock_text: str) -> float:
        clock_text = clock_text.strip()
        minutes = float(clock_text.split(":")[0]) * 60
        seconds = float(clock_text.split(":")[1])
        return minutes + seconds


    def get_own_clock(self) -> float:
        return self.parse_clock_time(
            self.webdriver.find_element(
                "css selector",
                "div.clock-top"
            ).text
        )


    def get_opponent_clock(self) -> float:
        return self.parse_clock_time(
            self.webdriver.find_element(
                "css selector",
                "div.clock-bottom"
            ).text
        )

    def game_finished(self) -> bool:
        if self.webdriver.find_elements("css selector", "span.draw-button-label"):
            return False
        else:
            return True
