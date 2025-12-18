from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from enum import Enum, auto
import os
from pathlib import Path
from io import BytesIO, IOBase
import shutil
from typing import cast


class FileReadType(Enum):
    IN_MEMORY = auto()
    TEMP_FILE = auto()


class FileSystemNode:
    @abstractmethod
    def write_to_filesystem(self, parent_directory: Path, name: str) -> None:
        pass


class InMemoryFile(FileSystemNode):
    def __init__(self, extension: str, data: IOBase):
        self._extension = extension
        self._data = data

    def write_to_filesystem(self, parent_directory: Path, name: str) -> None:
        full_path = parent_directory / (name + self._extension)
        data_flag = "b" if isinstance(self._data, BytesIO) else ""

        with open(full_path, "w" + data_flag) as file:
            self._data.seek(0)
            shutil.copyfileobj(self._data, file)


class TempFileCopy(FileSystemNode):
    def __init__(self, extension: str, temp_file_path: Path):
        self._extension = extension
        self._temp_file_path = temp_file_path

    def write_to_filesystem(self, parent_directory: Path, name: str) -> None:
        full_path = parent_directory / (name + self._extension)
        shutil.copy(self._temp_file_path, full_path)
        self._temp_file_path.unlink()


class Directory(FileSystemNode):
    def __init__(self) -> None:
        self._children: dict[str, FileSystemNode] = {}

    def write_to_filesystem(self, parent_directory: Path, name: str) -> None:
        full_path = parent_directory / name
        os.mkdir(full_path)
        for child_name in self._children:
            self._children[child_name].write_to_filesystem(full_path, child_name)

    def add_child(self, parent_path: Path, name: str, node: FileSystemNode) -> None:
        depth = len(parent_path.parts)

        if depth == 0:
            self._children[name] = node
        elif depth == 1:
            final_parent = parent_path.parts[0]
            parent = self._get_directory(final_parent)
            parent.add_child(Path("."), name, node)
        else:
            next_directory = parent_path.parts[0]
            relative_parent = parent_path.relative_to(next_directory)
            parent = self._get_directory(next_directory)
            parent.add_child(relative_parent, name, node)

    def _get_directory(self, name: str) -> Directory:
        if not name in self._children:
            self._children[name] = Directory()
        elif not isinstance(self._children[name], Directory):
            raise ValueError(
                f"Cannot get directory {name} because it is already a "
                f"{type(self._children[name]).__name__}."
            )

        return cast(Directory, self._children[name])


class FileSystemTree:
    def __init__(self, root: FileSystemNode):
        self._root = root

    def write_to_filesystem(self, parent_directory: Path, name: str) -> None:
        self._root.write_to_filesystem(parent_directory, name)

    def add_child(self, path: Path, node: FileSystemNode) -> None:
        if not isinstance(self._root, Directory):
            raise TypeError(
                "Can only add a child node when the root node is a Directory, "
                f"not {type(self._root).__name__}"
            )

        parent_path = path.parents[0]
        name = path.stem
        self._root.add_child(parent_path, name, node)

    @classmethod
    def create_from_file(
            cls, extension: str, read_type: FileReadType, *args
    ) -> FileSystemTree:
        file = cls._create_file_by_type(extension, read_type, args)
        return FileSystemTree(file)

    # files maps the path to the resulting file to the read type and list of arguments
    # to create the file with. Either [BaseIO] for in memory files, or [Path] for a temp
    # file copy.
    @classmethod
    def create_from_files(
            cls, files: Mapping[Path, tuple[FileReadType, list]]
    ) -> FileSystemTree:
        data_root_directory = Directory()
        file_system_tree = FileSystemTree(data_root_directory)

        for path in files:
            read_type, file_args = files[path]
            extension = path.suffix
            file = cls._create_file_by_type(extension, read_type, file_args)
            file_system_tree.add_child(path, file)

        return file_system_tree

    @classmethod
    def _create_file_by_type(
            cls, extension: str, read_type: FileReadType, file_args
    ) -> FileSystemNode:
        match read_type:
            case FileReadType.IN_MEMORY:
                return InMemoryFile(extension, *file_args)
            case FileReadType.TEMP_FILE:
                return TempFileCopy(extension, *file_args)
            case _:
                raise ValueError("Invalid FileReadType")
