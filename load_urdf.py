import bpy

from bpy.props import (FloatProperty,
                       PointerProperty,
                       StringProperty)
from bpy.types import (Operator,
                       PropertyGroup)

from . joint_controller import (JointControllerProperties,
                                URDF_PT_JointControllerPanel)

class UrdfLoadProperties(PropertyGroup):
    urdf_package: StringProperty(
        name = 'URDF package',
        description = 'desc',
        default = '',
        maxlen = 1024,
    )

class UrdfLoadStart(Operator):
    bl_label = 'Load URDF'
    bl_idname = 'urdf.printout'

    def execute(self, context):
        scene = context.scene
        urdf_tool = scene.urdf_tool

        print('execute LoadUrdf')
        test = LoadUrdf()
        print('num_joints = ', URDF_PT_JointControllerPanel.num_joints)
        URDF_PT_JointControllerPanel.num_joints = 1
        print('num_joints = ', URDF_PT_JointControllerPanel.num_joints)
        URDF_PT_JointControllerPanel.joint_min_limits[0] = -3.14159
        print(JointControllerProperties)

        bpy.types.Scene.joint_tool = PointerProperty(type=JointControllerProperties)
        bpy.utils.register_class(URDF_PT_JointControllerPanel)

        joint_min = -3
        joint_max = 3

        # Try to dynamically create the same class
        JointProps = type(
            # Class name
            "JointProps",

            # Base class
            (bpy.types.PropertyGroup, ),

            # Dictionary of properties
            {
                '__annotations__':
                {
                    'joint0':
                    (
                        FloatProperty,
                        {
                            'name': 'j0',
                            'description': 'desc',
                            'default': 0,
                            'min': joint_min,
                            'max': joint_max,
                        }
                    )
                }
            }
        )
        print(JointProps)
        bpy.utils.register_class(JointProps)
        bpy.types.Scene.other_joint_tool = PointerProperty(type=JointProps)

        return {'FINISHED'}

class URDF_PT_UrdfLoadPanel(bpy.types.Panel):
    """Load a URDF into Blender."""
    bl_label = 'URDF label'
    bl_category = 'Load URDF'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'layout label')
        scene = context.scene
        urdf_tool = scene.urdf_tool

        layout.prop(urdf_tool, "urdf_package")
        layout.operator("urdf.printout")
        layout.separator()

class LoadUrdf():

    def __init__(self):
        print('__init__ LoadUrdf')
        self.ParseUrdf()

    def ParseUrdf(self):
        print('ParseUrdf')
