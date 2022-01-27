bl_info = {
    "name": "UrdfDecimator",
    "description": "Batch decimate meshes associated with a URDF",
    "author": "Andy McEvoy",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add ",
    "warning": "Developmental",
    "wiki_url": "https://github.com/mcevoyandy/blender_urdf_visualizer",
    "tracker_url": "https://github.com/mcevoyandy/blender_urdf_visualizer/issues",
    "category": "Object",
    "support": "TESTING"
}

import bpy

from bpy.props import PointerProperty
from . batch_decimator import (URDF_PT_UrdfDecimatePanel,
                               UrdfDecimator,
                               UrdfDecimatorProperties)

classes = (
    URDF_PT_UrdfDecimatePanel,
    UrdfDecimatorProperties,
    UrdfDecimator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.urdf_decimator = PointerProperty(type=UrdfDecimatorProperties)
    print('Finished registering UrdfDecimator addon')

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.urdf_decimator

    print('Finished unregistering UrdfDecimator addon')

if __name__ == "__main__":
    register()
