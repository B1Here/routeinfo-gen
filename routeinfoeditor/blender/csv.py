import re
from typing import Literal

import bpy

from routeinfoeditor.blender.armatureutils import get_bones
from routeinfoeditor.blender.common import is_defined, split_if_contains
from routeinfoeditor.csvgen.abstractcsvgen import AbstractCsvGen
from routeinfoeditor.csvgen.pointgen import PointCsvGen
from routeinfoeditor.csvgen.routegen import RouteCsvGen
from routeinfoeditor.nsmbw.routeinfodata import point_flags
from routeinfoeditor.nsmbw.routeinfoutils import (
    is_flag_point,
    is_level_point,
)


class RouteInfoCsvGenOperator(bpy.types.Operator):
    """Generate RouteInfo CSV files"""

    bl_idname = "routeinfo.generate"
    bl_label = "Generate RouteInfo CSV files"

    def execute(
        self, context: bpy.types.Context
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        classes: list[type[AbstractCsvGen]] = [RouteCsvGen, PointCsvGen]

        # Run each generator for each armature
        for cls in classes:
            generator = cls(context)
            file_name = generator.exec()
            if not file_name:
                self.report(
                    {"ERROR"},
                    f"Failed to generate CSV file for {cls.__name__}.",
                )
                continue
            self.report({"INFO"}, f"Successfully generated CSV file {file_name}")

        self.report({"INFO"}, "Finished generating CSV files.")
        return {"FINISHED"}


class RouteInfoDataCleanupOperator(bpy.types.Operator):
    """Clean up csv column data that is not supposed to be present on specific bones,
    points and routes"""

    bl_idname = "routeinfo.cleanup"
    bl_label = "Cleanup Non-Point Data"

    def execute(
        self, context: bpy.types.Context
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        for bone in get_bones(context):
            point_settings = bone.route_info_point_settings
            if not is_level_point(bone.name):
                point_settings.unlocked_levels = ""
                point_settings.unlocked_bones = ""
                point_settings.unlocked_levels_secret_exit = ""
                point_settings.unlocked_bones_secret_exit = ""
                if not is_flag_point(bone.name):
                    point_settings.flags = ""

        self.report({"INFO"}, "Finished cleaning up RouteInfo data.")
        return {"FINISHED"}


class RouteInfoValidateOperator(bpy.types.Operator):
    """Validate RouteInfo data and report any issues"""

    bl_idname = "routeinfo.validate"
    bl_label = "Validate RouteInfo Data"

    def execute(
        self, context: bpy.types.Context
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        warnings = self.__validate_point_data(context)

        if warnings > 0:
            self.report(
                {"WARNING"},
                f"Finished validating RouteInfo data with {warnings} warning(s).",
            )
        else:
            self.report(
                {"INFO"}, "Finished validating RouteInfo data with no issues found."
            )
        return {"FINISHED"}

    def __validate_point_data(self, context: bpy.types.Context) -> int:
        bones = get_bones(context)
        bone_names = [b.name for b in bones]

        warnings = 0
        # Check that all flags on flag points and level points are valid point flags
        for bone in filter(
            lambda b: is_flag_point(b.name) or is_level_point(b.name),
            bones,
        ):
            point_settings = bone.route_info_point_settings
            for flag in split_if_contains(point_settings.flags, ","):
                if flag and flag not in point_flags:
                    self.report(
                        {"WARNING"},
                        f'Bone {bone.name} has a flag "{flag}" that is not a valid'
                        + "point flag.",
                    )
                    warnings += 1

        # Check that all unlocked levels and bones on level points reference
        #  existing bones
        for bone in filter(lambda b: is_level_point(b.name), bones):
            point_settings = bone.route_info_point_settings
            for level in split_if_contains(point_settings.unlocked_levels, ","):
                if level and level not in bone_names:
                    self.report(
                        {"WARNING"},
                        f"Bone {bone.name} has an unlocked level {level} that does"
                        + "not exist.",
                    )
                    warnings += 1

            for bone_name in split_if_contains(point_settings.unlocked_bones, ","):
                if bone_name and bone_name not in bone_names:
                    self.report(
                        {"WARNING"},
                        f"Bone {bone.name} has an unlocked bone {bone_name} that does"
                        + "not exist.",
                    )
                    warnings += 1

            for level in split_if_contains(
                point_settings.unlocked_levels_secret_exit, ","
            ):
                if level and level not in bone_names:
                    self.report(
                        {"WARNING"},
                        f"Bone {bone.name} has an unlocked secret exit level {level}"
                        + "that does not exist.",
                    )
                    warnings += 1

            for bone_name in split_if_contains(
                point_settings.unlocked_bones_secret_exit, ","
            ):
                if bone_name and bone_name not in bone_names:
                    self.report(
                        {"WARNING"},
                        f"Bone {bone.name} has an unlocked secret exit bone {bone_name}"
                        + " that does not exist.",
                    )
                    warnings += 1

        return warnings


class RouteInfoCsvSettings(bpy.types.PropertyGroup):
    file_path: bpy.props.StringProperty(
        name="File Path",
        description="The directory to save generated CSV files in",
        default="//",
        subtype="DIR_PATH",
        options=set(),
    )


class RouteInfoCsvPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {"DEFAULT_CLOSED"}
    bl_idname = "ROUTEINFO_PT_armature_attrs"
    bl_label = "RouteInfo CSV Configuration"
    bl_context = "data"

    @classmethod
    def poll(cls, context) -> bool:
        pattern = re.compile(r"^CS_W\d[ab]?$")
        if context.object and context.object.type == "ARMATURE" and context.armature:
            return (
                pattern.match(context.object.name) is not None
                and pattern.match(context.armature.name) is not None
                and context.armature.name == context.object.name
            )
        return False

    def draw(self, context) -> None:
        layout = self.layout
        if not is_defined(layout):
            return
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(context.armature.route_info_csv_settings, "file_path")
        layout.operator(
            RouteInfoCsvGenOperator.bl_idname,
            text="Generate RouteInfo CSVs",
            icon="TEXT",
        )
        layout.separator()
        layout.operator(
            RouteInfoDataCleanupOperator.bl_idname,
            text="Cleanup Non-Point Data",
            icon="BRUSH_DATA",
        )
        layout.operator(
            RouteInfoValidateOperator.bl_idname,
            text="Validate RouteInfo Data",
            icon="CHECKMARK",
        )
