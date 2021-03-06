""" Filesystem operations """

from pathlib import Path


class FileService:
    def list_directory(self, directory: Path, pattern: str):
        files = directory.glob(pattern)
        return [file for file in files if file.is_file()]
