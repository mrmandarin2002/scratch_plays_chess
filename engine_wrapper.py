from json import load
from inspect import stack
from random import random

from dataclasses import dataclass
from typing import Any, List, Tuple, Dict

from chess import Board
from chess.engine import (
    SimpleEngine,
    Limit,
    InfoDict
)

from exceptions import MissingMethodOverride


@dataclass
class EngineConfig:
    contempt: int
    multipv: int


def load_engine_config(filename: str) -> EngineConfig:
    with open(filename) as engine_config_file:
        return EngineConfig(*load(engine_config_file).values())


class WrapperConfig:
    def __init__(self, kwargs: Dict[str, Any]):
        for name, value in kwargs.items():
            setattr(self, name, value)


def load_wrapper_config(filename: str) -> WrapperConfig:
    with open(filename) as wrapper_config_file:
        return EngineConfig(load(wrapper_config_file))


class EngineWrapper:

    def __init__(
        self,
        engine_filename: str,
        engine_config: EngineConfig,
        wrapper_config: WrapperConfig
    ):

        self.engine = SimpleEngine.popen_uci(engine_filename)

        self.engine_config = engine_config
        self.engine.configure(self.engine_config.__dict__)
        self.board = Board()

        self.wrapper_config = wrapper_config

        self.total_time = 0.0
        self.time_control = 0.0
        self.own_clock = 0.0
        self.opponent_clock = 0.0


    def _missing(self) -> None:
        raise MissingMethodOverride(f"Oh noooooo~ >_< (you forgot to override \
{stack()[1].function} in {self.__class__})")


    def new_game(self, total_time: float, time_control: float, win: bool) -> None:
        """
        Resets board to beginning of game, and sets total time and time control
        variables.
        """
        self.board = Board()
        self.total_time = total_time
        self.time_control = time_control
        self.win = win


    def engine_time(self) -> float:
        """
        Calculates how much time to allow the engine to calculate
        This is the new version of
        `engine_class.ect(self, time_control, opponent_time)`

        Not implemented by default and will raise a `MissingMethodOverride`
        exception if a definition is not given by inherited class before method
        call.
        """
        self._missing()


    def engine_depth(self) -> int:
        """
        Calculates maximum depth for the engine
        This is the new version of
        `engine_class.ecd(self, time_control, own_time, opponent_time)`

        Not implemented by default and will raise a `MissingMethodOverride`
        exception if a definition is not given by inherited class before method
        call.
        """
        self._missing()


    def premove_delay(self) -> float:
        """
        Delay for selenium actions between premoves if any.
        Current default returns uniformly distributed random float in the
        interval [0.25 0.75).
        """
        return 0.25 + random() * 0.5


    def filter_moves(
        self,
        analysis: List[InfoDict]
    ) -> Tuple[bool, List[str], List[float]]:
        """
        Takes a list of engine moves from `engine.analyse()` and returns a
        tuple containing the following:
            - Boolean value denoting whether to cancel existing premoves. If no
              premoves are made or if they are never changed, this can be
              hardcoded to return False
            - List of moves to execute. If more than one move is in the list,
              the rest will be executed as premoves.
            - List of delays. Should be at least as long as list of moves.
              Delay between selenium action chains for each move. First element
              is delay before executing first move etc..

        Not implemented by default and will raise a `MissingMethodOverride`
        exception if a definition is not given by inherited class before method
        call.
        """
        self._missing()


    def play(self) -> Tuple[bool, List[str], List[float]]:
        """
        Performs engine analysis and returns results of `self.get_moves`
        method.
        """
        analysis = self.engine.analyse(
            self.board,
            Limit(time=self.engine_time(), depth=self.engine_depth()),
            multipv=self.engine_config.multipv
        )
        return self.filter_moves(analysis)


    def respond(
        self,
        moves: List[str],
        own_clock: float,
        opponent_clock: float
    ) -> Tuple[bool, List[str], List[float]]:
        """
        Pushes given moves to board, updates the clock variables and returns
        output of `self.play`.
        """
        for move in moves:
            self.board.push(move)

        self.own_clock = own_clock
        self.opponent_clock = opponent_clock

        return self.play()
