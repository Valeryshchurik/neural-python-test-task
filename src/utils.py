import traceback
from pathlib import Path


def get_unique_filepath(filepath: Path) -> Path:
    if not filepath.exists():
        return filepath
    stem, suffix = filepath.stem, filepath.suffix
    directory = filepath.parent
    counter = 1
    while True:
        new_name = f"{stem}({counter}){suffix}"
        new_path = directory / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def prepare_traceback_text(e: Exception):
    return ''.join(traceback.format_exception(type(e), e, e.__traceback__))
