from json import load

from dataclasses import dataclass
from typing import List


@dataclass
class Credentials:
    username: str
    password: str


def load_credentials(filename: str) -> List[Credentials]:
    with open(filename) as credentials_file:
        return [
            Credentials(credentials[0], credentials[1])
            for credentials in load(credentials_file)
        ]
