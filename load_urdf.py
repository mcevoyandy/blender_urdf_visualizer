import bpy

from bpy.props import (FloatProperty,
                       PointerProperty,
                       StringProperty)
from bpy.types import (Operator,
                       PropertyGroup)

from . joint_controller import URDF_PT_JointControllerPanel

class UrdfLoadProperties(PropertyGroup):
    urdf_package: StringProperty(
        name = 'ROS pkg:',
        description = 'desc',
        subtype = 'DIR_PATH',
        default = '',
        maxlen = 1024,
    )

    urdf_filename: StringProperty(
        name = 'URDF:',
        description = 'desc',
        subtype = 'FILE_PATH',
        default = '',
        maxlen = 1024,
    )

def float_callback(self, context):
    print('\nfloat callback')
    jt = context.scene.joint_tool
    print('jt.items  = ', jt.items())
    print('jt.keys   = ', jt.keys())
    print('jt.values = ', jt.values())
    print('jt.__annotations__.keys()   = ', jt.__annotations__.keys())
    print('jt.__annotations__.values() = ', jt.__annotations__.values())


class UrdfLoadStart(Operator):
    bl_label = 'Load URDF'
    bl_idname = 'urdf.printout'

    def execute(self, context):
        scene = context.scene
        urdf_tool = scene.urdf_tool

        urdf_pkg_path = bpy.path.abspath(urdf_tool.urdf_package)
        print('urdf_pkg_path = ', urdf_pkg_path)

        urdf_filename = bpy.path.abspath(urdf_tool.urdf_filename)
        print('urdf_filename = ', urdf_filename)

        print('execute LoadUrdf')
        test = LoadUrdf()

        joint_min = -3
        joint_max = 3

        # TODO: return this dictionary after parsing the URDF
        # Dynamically create the same class
        JointControllerProperties = type(
            # Class name
            "JointControllerProperties",

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
                            'update': float_callback
                        }
                    ),
                    'joint1':
                    (
                        FloatProperty,
                        {
                            'name': 'j1',
                            'description': 'desc',
                            'default': 1,
                            'min': joint_min,
                            'max': joint_max,
                            'update': float_callback
                        }
                    )
                }
            }
        )
        bpy.utils.register_class(JointControllerProperties)
        bpy.types.Scene.joint_tool = PointerProperty(type=JointControllerProperties)
        bpy.utils.register_class(URDF_PT_JointControllerPanel)

        return {'FINISHED'}


class URDF_PT_UrdfLoadPanel(bpy.types.Panel):
    """Load a URDF into Blender."""
    bl_label = 'URDF label'
    bl_category = 'Load URDF'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Select URDF package & file:')
        scene = context.scene
        urdf_tool = scene.urdf_tool

        layout.prop(urdf_tool, 'urdf_package')
        layout.prop(urdf_tool, 'urdf_filename')
        layout.operator('urdf.printout')
        layout.separator()

class LoadUrdf():

    def __init__(self):
        print('__init__ LoadUrdf')
        self.ParseUrdf()

    def ParseUrdf(self):
        print('ParseUrdf')
