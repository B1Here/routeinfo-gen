from routeinfoeditor.blender.armatureutils import get_bones
from routeinfoeditor.csvgen.abstractcsvgen import AbstractCsvGen
from routeinfoeditor.nsmbw.routeinfoutils import (
    is_flag_point,
    is_level_point,
)


class PointCsvGen(AbstractCsvGen):
    def _create_csv(self) -> str:
        csv: str = ""
        id: int = 0
        bones = list(
            filter(
                lambda b: is_level_point(b.name) or is_flag_point(b.name),
                get_bones(self._context),
            )
        )

        for (index, bone) in enumerate(bones):
            point_settings = bone.route_info_point_settings

            csv += (
                f"{index},{bone.name},{self._csv_array_guard(point_settings.flags)},"
                + f"{self._csv_array_guard(point_settings.unlocked_levels)},"
                + f"{self._csv_array_guard(point_settings.unlocked_bones)},"
                + f"{self._csv_array_guard(point_settings.unlocked_levels_secret_exit)},"
                + f"{self._csv_array_guard(point_settings.unlocked_bones_secret_exit)},\r\n"
            )

        return csv

    def _get_file_name(self, world: str) -> str:
        return f"pointW{world}.csv"
