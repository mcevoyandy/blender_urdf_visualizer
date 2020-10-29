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

class UrdfLoader(bpy.types.Operator):
    """Load a URDF into Blender."""
    bl_idname = "object.urdf_loader"
    bl_label = "URDF"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print('Load URDF.')

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(UrdfLoader.bl_idname)

addon_keymaps = []

def register():
    bpy.utils.register_class(UrdfLoader)

    # Add
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(UrdfLoader)
    bpy.types.VIEW3D_MT_add.remove(menu_func)

if __name__ == "__main__":
    register()
