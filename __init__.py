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

from bpy.props import PointerProperty

from . load_urdf import (URDF_PT_UrdfLoadPanel,
                         UrdfLoadProperties,
                         UrdfLoadStart)
from . joint_controller import URDF_PT_JointControllerPanel


classes = (
    URDF_PT_UrdfLoadPanel,
    UrdfLoadProperties,
    UrdfLoadStart,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.urdf_tool = PointerProperty(type=UrdfLoadProperties)
    print('Finished registering URDF addon')

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    try:
        bpy.utils.unregister_class(URDF_PT_JointControllerPanel)
    except:
        pass

    try:
        bpy.utils.unregister_class(JointControllerProperties)
    except:
        pass

    del bpy.types.Scene.urdf_tool

    try:
        del bpy.types.Scene.joint_tool
    except:
        pass

    print('Finished unregistering URDF addon')

if __name__ == "__main__":
    register()
