from os.path import isfile
from threading import Thread
from json import load, dump
from json.decoder import JSONDecodeError

from dataclasses import dataclass
from typing import Any, List

from consts import (
    START_GAME_EVENT_STR,
    MOVE_EVENT_STR,
    END_GAME_EVENT_STR
)


@dataclass
class Log:
    event: str
    game_id: int
    data: Any


def construct_log(log: List) -> Log:
    return Log(log[0], log[1], log[2])


def serialize_log(log: Log) -> List:
    return [log.event, log.game_id, log.data]


class LogsManager(Thread):

    def __init__(self, filename: str):
        Thread.__init__(self)

        self.filename = filename

        self.logs = []
        self.game_ids = []
        if isfile(filename):
            try:
                with open(filename) as logs_file:
                    self.logs = [construct_log(log) for log in load(logs_file)]
            except JSONDecodeError:
                self.logs = []
            self.game_ids = [log.game_id for log in self.logs]

        self.logs_filename = filename
        self.logs_queue = []
        self.running = False
        self.finished = False


    def load_logs(self, filename: str):
        """
        Loads `Log` objects from given filename using `json.load`.
        """
        with open(filename) as logs_file:
            self.logs = [construct_log(log) for log in load(logs_file)]


    def dump_logs(self):
        """
        Converts all existing logs to JSON-serializable format then dumps them
        to `self.logs_file`.
        """
        with open(self.logs_filename, "w") as logs_file:
            dump([serialize_log(log) for log in self.logs], logs_file)


    def new_event(self, event: str, game_id: int, data: str):
        """
        Constructs and adds new `Log` object to `self.logs_queue`.
        """
        self.logs_queue.append(Log(event, game_id, data))


    def start_game(self, opponent: str, playing_white: bool) -> int:
        """
        Logs the start of a new game and returns a unique game id.
        """
        game_id = self.game_ids[-1] + 1 if self.game_ids else 0
        self.new_event(START_GAME_EVENT_STR, game_id, [opponent, playing_white])
        return game_id


    def move(self, game_id: int, move: str):
        """
        Logs a given move for the given game id.
        """
        self.new_event(MOVE_EVENT_STR, game_id, move)


    def end_game(self, game_id: int, won: bool):
        """
        Logs the end of the game with the given game id.
        """
        self.new_event(END_GAME_EVENT_STR, game_id, won)


    def run(self):
        self.running = True

        while self.running:
            while self.logs_queue:
                log = self.logs_queue.pop(0)
                self.logs.append(log)
                self.dump_logs()

        self.finished = True


    def stop(self):
        self.running = False
        self.join()
        self.logs_file.close()


    def __enter__(self):
        self.start()


    def __exit__(self):
        self.stop()
