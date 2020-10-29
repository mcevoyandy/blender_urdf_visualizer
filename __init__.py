bl_info = {
    "name": "URDF",
    "description": "Visualize a URDF and its meshes",
    "author": "Andy McEvoy",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add ",
    "warning": "Developmental",
    "wiki_url": "https://www.google.com",
    "tracker_url": "https://www.google.com",
    "category": "Object",
    "support": "TESTING"
}

import bpy

from bpy.props import (PointerProperty,
                       StringProperty)
from bpy.types import (Operator,
                       PropertyGroup)

from . load_urdf import UrdfLoader

class UrdfProperties(PropertyGroup):
    urdf_package: StringProperty(
        name = 'URDF package',
        description = 'desc',
        default = '',
        maxlen = 1024,
    )

class AddUrdf(Operator):
    bl_label = 'Add URDF'
    bl_idname = 'urdf.printout'

    def execute(self, context):
        scene = context.scene
        urdf_tool = scene.urdf_tool

        test = UrdfLoader()
        print('execute AddUrdf')

        return {'FINISHED'}


class OBJECT_PT_UrdfPanel(bpy.types.Panel):
    """Load a URDF into Blender."""
    bl_label = 'URDF label'
    bl_category = 'Load URDF'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.label(text="layout label")
        scene = context.scene
        urdf_tool = scene.urdf_tool

        layout.prop(urdf_tool, "urdf_package")
        layout.operator("urdf.printout")
        layout.separator()

classes = (
    UrdfProperties,
    AddUrdf,
    OBJECT_PT_UrdfPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.urdf_tool = PointerProperty(type=UrdfProperties)
    # bpy.types.VIEW3D_MT_add.append(menu_func)
    print('Finished registering URDF addon')

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.urdf_tool
    # bpy.types.VIEW3D_MT_add.remove(menu_func)
    print('Finished unregistering URDF addon')

if __name__ == "__main__":
    register()
