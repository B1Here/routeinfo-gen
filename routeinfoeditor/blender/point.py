import bpy

from routeinfoeditor.blender.armatureutils import get_bone
from routeinfoeditor.blender.common import is_defined
from routeinfoeditor.nsmbw.routeinfoutils import (
    is_flag_point,
    is_level_point,
)


class RouteInfoPointSettings(bpy.types.PropertyGroup):
    flags: bpy.props.StringProperty(
        name="Flags",
        description="Flags this point should have (comma-separated)",
        default="",
        options=set(),
    )

    unlocked_levels: bpy.props.StringProperty(
        name="Unlocked Levels",
        description="Levels this level unlocks (comma-separated)",
        default="",
        options=set(),
    )

    unlocked_bones: bpy.props.StringProperty(
        name="Unlocked Bones",
        description="Bones this level unlocks (comma-separated)",
        default="",
        options=set(),
    )

    unlocked_levels_secret_exit: bpy.props.StringProperty(
        name="Unlocked Levels",
        description="Secret levels this level unlocks (comma-separated)",
        default="",
        options=set(),
    )

    unlocked_bones_secret_exit: bpy.props.StringProperty(
        name="Unlocked Bones",
        description="Secret bones this level unlocks (comma-separated)",
        default="",
        options=set(),
    )


class RouteInfoPointPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {"DEFAULT_CLOSED"}
    bl_idname = "ROUTEINFO_POINT_PT_bone_attrs"
    bl_label = "RouteInfo Point Data"
    bl_context = "bone"

    @classmethod
    def poll(cls, context) -> bool:
        bone = get_bone(context)
        if not is_defined(bone):
            return False

        return is_level_point(bone.name) or is_flag_point(bone.name)

    def draw(self, context) -> None:
        layout = self.layout
        if not is_defined(layout):
            return

        bone = get_bone(context)
        if not is_defined(bone):
            return

        layout.use_property_split = True
        layout.use_property_decorate = False

        point_settings = bone.route_info_point_settings
        layout.prop(bone, "name")
        layout.prop(point_settings, "flags")
        if is_level_point(bone.name):
            layout.prop(point_settings, "unlocked_levels")
            layout.prop(point_settings, "unlocked_bones")


class RouteInfoPointSecretPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {"DEFAULT_CLOSED"}
    bl_idname = "ROUTEINFO_POINT_PT_bone_secret_attrs"
    bl_label = "Secret Exit"
    bl_parent_id = "ROUTEINFO_POINT_PT_bone_attrs"
    bl_context = "bone"

    @classmethod
    def poll(cls, context) -> bool:
        bone = get_bone(context)
        if not is_defined(bone):
            return False

        return is_level_point(bone.name)

    def draw(self, context) -> None:
        layout = self.layout
        if not is_defined(layout):
            return

        bone = get_bone(context)
        if not is_defined(bone):
            return

        layout.use_property_split = True
        layout.use_property_decorate = False

        point_settings = bone.route_info_point_settings
        layout.prop(point_settings, "unlocked_levels_secret_exit")
        layout.prop(point_settings, "unlocked_bones_secret_exit")
