""" Handles operations for writing, moving and removing files on disk"""

from typing import Any
from config import configuration
from os.path import exists, isfile
from os import remove, getcwd
from pathlib import Path
from shutil import copy

class FileManager:

    def __init__(self, cfg: configuration) -> None:
        self.cfg = cfg

    def write(self, path: Path, data: Any) -> str:
        with open(path, 'w+') as f:
            f.write(data)
        return path

    def read(self, path: Path) -> any:
        if not (exists(path) and isfile(path)): return None
        with open(path, "rb") as f:
            contents = f.read()
            return contents


    def delete(self, path: Path) -> bool:
        if not exists(path): return False
        remove(path)
        return True

    def copy(self, path: Path, destination: Path) -> bool:
        copy(path, destination)
        return True


    def delete_all_archives_in_path(self, path: Path):
        # todo: remove all zip files in a given path
        pass

    def exists_locally(self, path: Path) -> bool:
        return exists(path) and isfile(path)