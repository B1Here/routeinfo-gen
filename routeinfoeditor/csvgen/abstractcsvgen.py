import re
from abc import ABC, abstractmethod

import bpy


class AbstractCsvGen(ABC):
    def __init__(self, context: bpy.types.Context):
        self._context = context

    def exec(self) -> str:
        world = self._get_world_from_armature(self._context.armature)
        csv = self._create_csv()
        path: str = self._context.armature.route_info_csv_settings.file_path
        if not path.endswith("/"):
            path += "/"
        file_name = f"{path}{self._get_file_name(world)}"
        self._save_file(csv, file_name)

        return file_name

    def _save_file(self, content: str, path: str) -> None:
        with open(bpy.path.abspath(path), "wb") as file:
            file.write(content.encode("shift_jis"))

    def _get_world_from_armature(self, armature: bpy.types.Armature | None) -> str:
        if armature is None:
            return "0"
        match = re.match(r"^CS_W(\d[ab]?)$", armature.name)
        if match:
            return match.group(1)
        return "0"

    @abstractmethod
    def _create_csv(self) -> str:
        pass

    @abstractmethod
    def _get_file_name(self, world: str) -> str:
        pass

    def _csv_array_guard(self, string: str) -> str:
        return f'"{string}"' if "," in string else string
