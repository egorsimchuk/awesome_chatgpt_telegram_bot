"""Helpful utilities"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Union


def get_root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def get_path_from_root_dir(path: Union[str, Path]) -> Path:
    return get_root_dir().joinpath(path)


def utc_now() -> int:
    """Return now UTC timestamp in seconds"""
    return int(datetime.now(timezone.utc).timestamp())
