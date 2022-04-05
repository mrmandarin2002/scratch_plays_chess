from json import load

from dataclasses import dataclass


@dataclass
class Config:
    credentials_filename: str
    logs_filename: str


def load_config(filename: str) -> Config:
    with open(filename) as config_file:
        return Config(*(load(config_file).values()))
