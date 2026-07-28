from typing import Literal

import bpy

from routeinfoeditor.blender.armatureutils import get_bones
from routeinfoeditor.blender.common import is_defined
from routeinfoeditor.nsmbw.routeinfoutils import is_point


class RouteInfoRouteMoveUpOperator(bpy.types.Operator):
    bl_idname = "routeinfo.move_route_up"
    bl_label = "Move Route Up"

    def execute(
        self, context: bpy.types.Context
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        armature = context.armature
        if not is_defined(armature):
            self.report({"ERROR"}, "No armature found")
            return {"CANCELLED"}
        route_settings = armature.route_info_route_settings
        index = route_settings.active_route_index
        if index > 0 and index < len(route_settings.routes):
            route_settings.routes.move(index, index - 1)
            route_settings.active_route_index = index - 1
        return {"FINISHED"}


class RouteInfoRouteMoveDownOperator(bpy.types.Operator):
    bl_idname = "routeinfo.move_route_down"
    bl_label = "Move Route Down"

    def execute(
        self, context: bpy.types.Context
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        armature = context.armature
        if not is_defined(armature):
            self.report({"ERROR"}, "No armature found")
            return {"CANCELLED"}
        route_settings = armature.route_info_route_settings
        index = route_settings.active_route_index
        if index >= 0 and index < len(route_settings.routes) - 1:
            route_settings.routes.move(index, index + 1)
            route_settings.active_route_index = index + 1
        return {"FINISHED"}


class RouteInfoRouteRefreshOperator(bpy.types.Operator):
    bl_idname = "routeinfo.refresh_routes"
    bl_label = "Refresh"

    def execute(
        self, context: bpy.types.Context
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        armature = context.armature
        if not is_defined(armature):
            self.report({"ERROR"}, "No armature found")
            return {"CANCELLED"}
        route_settings = armature.route_info_route_settings

        bones = get_bones(context)
        new_route_names = self._fetch_names(bones)

        # Keep routes where both bones still exist, remove routes where either bone
        # doesn't exist, and add routes for new bone pairs
        idicies_to_remove = []
        for i in range(len(route_settings.routes)):
            route = route_settings.routes[i]
            if route.name not in new_route_names:
                idicies_to_remove.append(i)

        for i in reversed(idicies_to_remove):
            route_settings.routes.remove(i)
        bones = get_bones(context)
        existing_route_names = {route.name for route in route_settings.routes}

        if bones:
            for bone_name in new_route_names:
                if bone_name not in existing_route_names:
                    route_settings.routes.add().name = bone_name

        self.report(
            {"INFO"},
            f"Routes refreshed, {len(idicies_to_remove)} removed, {len(route_settings.routes) - len(existing_route_names)} added.",
        )
        return {"FINISHED"}

    def _fetch_names(self, bones) -> list[str]:
        route_bones: list[bpy.types.Bone] = []
        for bone in bones:
            if (
                bone.name.startswith("R")
                and is_point(bone.name[1:5])
                and is_point(bone.name[5:9])
            ):
                route_bones.append(bone)

        result: list[str] = []
        for bone in route_bones:
            self.__add_route_for_bone(bone, result)

        return result

    def __add_route_for_bone(
        self, bone: bpy.types.Bone, route_names: list[str]
    ) -> None:
        if (
            is_defined(bone.children)
            and len(bone.children) > 0
            and filter(lambda child: is_point(child.name), bone.children)
        ):
            self.__add_route_via_child(bone, route_names)
            return
        route_names.append(bone.name)

    def __add_route_via_child(
        self, bone: bpy.types.Bone, route_names: list[str]
    ) -> None:
        if not is_defined(bone.children) or len(bone.children) == 0:
            return
        bone_name = bone.name
        if bone_name.startswith("R"):
            bone_name = bone_name[1:5]
        route_names.append(f"R{bone_name}{bone.children[0].name}")
        self.__add_route_via_child(bone.children[0], route_names)

        if bone.name.startswith("R"):
            last_child: bpy.types.Bone = self.__get_last_point_child(bone)
            if (
                bone.name[1:5] != bone.children[0].name
                and bone.name[5:9] != last_child.name
            ):
                route_names.append(f"R{last_child.name}{bone.name[5:9]}")

    def __get_last_point_child(self, bone: bpy.types.Bone) -> bpy.types.Bone:
        if not is_defined(bone.children) or len(bone.children) == 0:
            return bone
        return self.__get_last_point_child(bone.children[0])


class RouteInfoRouteSelectBonesOperator(bpy.types.Operator):
    bl_idname = "routeinfo.route_select_bones"
    bl_label = "Select Bones"

    def execute(
        self, context: bpy.types.Context
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        armature = context.armature
        if not is_defined(armature) or not is_defined(context.object):
            self.report({"ERROR"}, "No armature found")
            return {"CANCELLED"}
        route_settings = armature.route_info_route_settings
        index = route_settings.active_route_index
        if index < 0 or index >= len(route_settings.routes):
            self.report({"ERROR"}, "No route selected")
            return {"CANCELLED"}
        route_name: str = route_settings.routes[index].name
        bones_to_select: list[bpy.types.Bone] = [
            bone for bone in armature.bones if route_name.__contains__(bone.name)
        ]

        if context.object.mode == "POSE":
            for bone in context.object.pose.bones:
                selectable = (
                    len(list(filter(lambda b: b.name == bone.name, bones_to_select)))
                    > 0
                )
                bone.bone.select = selectable
            if (
                len(list(filter(lambda b: b.bone.select, context.object.pose.bones)))
                < 2
            ):
                self.report(
                    {"WARNING"},
                    "Not all bones were selected. Make sure to refresh the list.",
                )
        elif context.object.mode == "EDIT":
            for bone in armature.edit_bones:
                selectable = (
                    len(list(filter(lambda b: b.name == bone.name, bones_to_select)))
                    > 0
                )
                bone.select = selectable
                bone.select_head = selectable
                bone.select_tail = selectable
            if len(list(filter(lambda b: b.select, armature.edit_bones))) < 2:
                self.report(
                    {"WARNING"},
                    "Not all bones were selected. Make sure to refresh the list.",
                )

        return {"FINISHED"}
