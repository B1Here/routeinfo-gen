import re

import bpy

from routeinfoeditor.blender.common import is_defined
from routeinfoeditor.nsmbw.routeinfodata import route_animations


class RouteInfoRoutesList(bpy.types.UIList):
    bl_idname = "ROUTEINFO_ROUTE_UL_routes_list"

    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_property,
        index,
        flt_flag,
    ) -> None:
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.label(text=item.name, icon="CON_TRACKTO")
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="")


class RouteInfoRouteDetailProperties(bpy.types.PropertyGroup):
    animation: bpy.props.EnumProperty(
        name="Animation",
        description="The animation this route should use",
        items=(list(map(lambda anim: (anim[0], anim[1], ""), route_animations))),
        default="道",
        options=set(),
    )
    flags: bpy.props.StringProperty(
        name="Flags",
        description="The flags for this route (comma-separated)",
        options=set(),
    )


class RouteInfoRouteSettings(bpy.types.PropertyGroup):
    routes: bpy.props.CollectionProperty(type=RouteInfoRouteDetailProperties)
    active_route_index: bpy.props.IntProperty()


class RouteInfoRoutePanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {"DEFAULT_CLOSED"}
    bl_idname = "ROUTEINFO_ROUTE_PT_armature_attrs"
    bl_label = "RouteInfo Route Data"
    bl_context = "data"

    @classmethod
    def poll(cls, context) -> bool:
        pattern = re.compile(r"^CS_W\d[ab]?$")
        if (
            not is_defined(context.object)
            or context.object.type != "ARMATURE"
            or not is_defined(context.armature)
        ):
            return False

        return (
            pattern.match(context.object.name) is not None
            and pattern.match(context.armature.name) is not None
            and context.armature.name == context.object.name
        )

    def draw(self, context) -> None:
        layout = self.layout
        if not is_defined(layout):
            return
        layout.use_property_split = True
        layout.use_property_decorate = False
        armature = context.armature
        if not is_defined(armature):
            return
        route_settings = armature.route_info_route_settings
        row = layout.row()
        row.template_list(
            RouteInfoRoutesList.bl_idname,
            "",
            route_settings,
            "routes",
            route_settings,
            "active_route_index",
        )
        column = row.column(align=True)
        column.operator("routeinfo.move_route_up", icon="TRIA_UP", text="")
        column.operator("routeinfo.move_route_down", icon="TRIA_DOWN", text="")
        row = layout.row()
        row.operator("routeinfo.refresh_routes", icon="FILE_REFRESH")

        column = row.column()
        column.enabled = ["EDIT", "POSE"].__contains__(context.active_object.mode)
        column.operator("routeinfo.route_select_bones", icon="GROUP_BONE")
        route_settings = armature.route_info_route_settings
        index = route_settings.active_route_index
        if index < 0 or index >= len(route_settings.routes):
            return
        route_details = route_settings.routes[index]
        layout.prop(route_details, "animation")
        layout.prop(route_details, "flags")
