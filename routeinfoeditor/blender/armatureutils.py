import bpy

from routeinfoeditor.blender.common import is_defined


def get_bone(
    context: bpy.types.Context,
) -> bpy.types.EditBone | bpy.types.Bone | bpy.types.PoseBone | None:
    if not is_defined(context.object):
        return context.bone

    if context.object.mode == "EDIT":
        return context.active_bone
    if context.object.mode == "POSE":
        return context.active_pose_bone
    return context.active_bone


def get_bones(
    context: bpy.types.Context,
) -> (
    bpy.types.ArmatureBones
    | bpy.types.ArmatureEditBones
    # | bpy.types.ArmaturePoseBones if that would exist.
    # "bpy.types.bpy_prop_collection[bpy.types.PoseBone]" does not work even though
    # that's what Blender itself uses.
    | list
):
    if not is_defined(context.object) or not is_defined(context.armature):
        return []

    if context.object.mode == "EDIT":
        return context.armature.edit_bones
    if context.object.mode == "POSE":
        return context.armature.pose.bones
    return context.armature.bones
