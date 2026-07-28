import bpy

from routeinfoeditor.blender import csv, point, route, routeops

bl_info = {
    "name": "RouteInfo Editor",
    "author": "B1Here",
    "blender": (3, 3, 0),
    "version": (1, 1, 1),
    "category": "Interface",
    "description": "Allows editing and generating NSMBW RouteInfo CSV files from armatures directly.",
}

classes = (
    # data
    csv.RouteInfoCsvGenOperator,
    csv.RouteInfoDataCleanupOperator,
    csv.RouteInfoCsvSettings,
    csv.RouteInfoValidateOperator,
    point.RouteInfoPointSettings,
    route.RouteInfoRouteDetailProperties,
    route.RouteInfoRoutesList,
    route.RouteInfoRouteSettings,
    # ui
    route.RouteInfoRoutePanel,
    csv.RouteInfoCsvPanel,
    point.RouteInfoPointPanel,
    point.RouteInfoPointSecretPanel,
    # operators
    routeops.RouteInfoRouteMoveUpOperator,
    routeops.RouteInfoRouteMoveDownOperator,
    routeops.RouteInfoRouteRefreshOperator,
    routeops.RouteInfoRouteSelectBonesOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Armature.route_info_csv_settings = bpy.props.PointerProperty(
        type=csv.RouteInfoCsvSettings
    )
    bpy.types.Armature.route_info_route_settings = bpy.props.PointerProperty(
        type=route.RouteInfoRouteSettings
    )
    bpy.types.Bone.route_info_point_settings = bpy.props.PointerProperty(
        type=point.RouteInfoPointSettings
    )
    bpy.types.EditBone.route_info_point_settings = bpy.props.PointerProperty(
        type=point.RouteInfoPointSettings
    )
    bpy.types.PoseBone.route_info_point_settings = bpy.props.PointerProperty(
        type=point.RouteInfoPointSettings
    )


def unregister():
    del bpy.types.PoseBone.route_info_point_settings
    del bpy.types.EditBone.route_info_point_settings
    del bpy.types.Bone.route_info_point_settings
    del bpy.types.Armature.route_info_route_settings
    del bpy.types.Armature.route_info_csv_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
