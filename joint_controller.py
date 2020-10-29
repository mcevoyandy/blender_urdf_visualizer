import bpy

from bpy.props import FloatProperty
from bpy.types import PropertyGroup


class JointControllerProperties(PropertyGroup):
    joint0: FloatProperty(
        name = 'j0',
        description = 'desc',
        default = 0.0,
        min = 0.0,
        max = 3.14159
    )
    joint1: FloatProperty(
        name = 'j1',
        description = 'desc',
        default = 0.0,
        min = 0.0,
        max = 3.14159
    )
    joint2: FloatProperty(
        name = 'j2',
        description = 'desc',
        default = 0.0,
        min = 0.0,
        max = 3.14159
    )
    joint3: FloatProperty(
        name = 'j3',
        description = 'desc',
        default = 0.0,
        min = 0.0,
        max = 3.14159
    )
    joint4: FloatProperty(
        name = 'j4',
        description = 'desc',
        default = 0.0,
        min = 0.0,
        max = 3.14159
    )
    joint5: FloatProperty(
        name = 'j5',
        description = 'desc',
        default = 0.0,
        min = 0.0,
        max = 3.14159
    )
    joint6: FloatProperty(
        name = 'j6',
        description = 'desc',
        default = 0.0,
        min = 0.0,
        max = 3.14159
    )

class URDF_PT_JointControllerPanel(bpy.types.Panel):
    bl_label = 'Joint Label'
    bl_category = 'Joint Controller'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    joint_names = [
        'joint0',
        'joint1',
        'joint2',
        'joint3',
        'joint4',
        'joint5',
        'joint6'
    ]

    num_joints = 2

    joint_min_limits = [0, 0, 0, 0, 0, 0, 0]
    joint_max_limits = [1, 1, 1, 1, 1, 1, 1]

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'joint angles')
        scene = context.scene
        joint_tool = scene.joint_tool

        for i in range(0, self.num_joints):
            layout.prop(joint_tool, self.joint_names[i])

        layout.separator()
