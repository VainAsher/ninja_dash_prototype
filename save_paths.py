"""Centralised helpers for save / config file locations."""
from pathlib import Path

APP_DIR_NAME = "ninja_dash"


def get_save_dir() -> Path:
    home = Path.home()
    save_dir = home / f".{APP_DIR_NAME}"
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


def get_save_path(filename: str) -> Path:
    return get_save_dir() / filename
