import bpy

from bpy.props import FloatProperty
from bpy.types import PropertyGroup


class URDF_PT_JointControllerPanel(bpy.types.Panel):
    bl_label = 'Joint Label'
    bl_category = 'Joint Controller'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'joint angles')
        scene = context.scene
        joint_tool = scene.joint_tool

        layout.prop(joint_tool, 'joint0')
        layout.prop(joint_tool, 'joint1')

        layout.separator()
