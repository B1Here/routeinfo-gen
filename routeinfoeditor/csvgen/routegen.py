from routeinfoeditor.csvgen.abstractcsvgen import AbstractCsvGen


class RouteCsvGen(AbstractCsvGen):
    def _create_csv(self) -> str:
        routes = self._context.armature.route_info_route_settings.routes

        csv = ""
        for route in routes:
            csv += (
                f"{route.name},{route.animation},"
                + f"{self._csv_array_guard(route.flags)}\r\n"
            )

        return csv

    def _get_file_name(self, world: str) -> str:
        return f"routeW{world}.csv"
