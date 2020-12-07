import bpy

from bpy.props import FloatProperty
from bpy.types import PropertyGroup


class URDF_PT_JointControllerPanel(bpy.types.Panel):
    bl_label = 'Joint Label'
    bl_category = 'Joint Controller'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    joint_names = []

    def __init__(self):
        print("Initialize JointController")


    @staticmethod
    def set_joint_names(joint_names):
        URDF_PT_JointControllerPanel.joint_names = joint_names


    def draw(self, context):
        layout = self.layout
        layout.label(text = 'joint angles')
        scene = context.scene
        joint_tool = scene.joint_tool

        print(URDF_PT_JointControllerPanel.joint_names)
        if (len(URDF_PT_JointControllerPanel.joint_names) > 0):
            for joint in URDF_PT_JointControllerPanel.joint_names:
                layout.prop(joint_tool, joint)

        layout.separator()
