from typing import Iterable, NoReturn

__version__ = tuple[int, int, int] | tuple[int, int, int, int | str]

DATA = str
BIN_DIR = str

def _program(name: str, args: Iterable[str]) -> int: ...

def ninja() -> NoReturn: ...
