import bpy
from bpy.props import (FloatProperty,
                       StringProperty)
from bpy.types import (Operator,
                       PropertyGroup)

import os
from os import listdir, path
from pathlib import Path
import shutil

HEADER_SIZE = 84  # Binary STLs have (up to) an 80 byte header
TRIANGLE_SIZE = 50  # Binary STLs store each triangle using 50 bytes

class UrdfDecimatorProperties(PropertyGroup):
    mesh_dir: StringProperty(
        name = 'Mesh dir:',
        description = 'Path to the meshes you want to decimate.',
        subtype = 'DIR_PATH',
        default = '',
        maxlen = 1024,
    )

    max_size: FloatProperty(
        name = 'Max mesh size',
        description = 'Max size in MB of the decimated mesh.',
        default = 1.0,
        min = 0.1,
        max = 10.0,
        step = 0.05,
    )

class UrdfDecimator(Operator):
    bl_label = 'Decimate meshes'
    bl_description = 'Decimate meshes'
    bl_idname = 'urdf.decimate'

    def execute(self, context):
        scene = context.scene
        urdf_decimator = scene.urdf_decimator

        mesh_path = bpy.path.abspath(urdf_decimator.mesh_dir)
        print(f'INFO: urdf_pkg_path = {mesh_path}')

        mesh_size = urdf_decimator.max_size
        print(f'INFO: mesh_size = {mesh_size}')

        decimate_meshes(mesh_path, mesh_size)

        return {'FINISHED'}


class URDF_PT_UrdfDecimatePanel(bpy.types.Panel):
    """Decimate the STLs of a URDF."""
    bl_label = 'URDF Mesh Decimator'
    bl_category = 'URDF Decimator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Select dir of meshes to decimate:')
        scene = context.scene
        urdf_decimator = scene.urdf_decimator

        layout.prop(urdf_decimator, 'mesh_dir')
        layout.prop(urdf_decimator, 'max_size')
        layout.operator('urdf.decimate')
        layout.separator()


def decimate_meshes(mesh_path: str, mesh_size: float):
    """Search mesh_path for STLs and decimated them to have max mesh_size.

    Args:
      mesh_path (string): path to the mesh directory
      mesh_size (float): maximum size in MB for the decimated mesh.

    """

    mesh_files = listdir(mesh_path)

    print('INFO: Processing ', len(mesh_files), ' items...')
    index = 0
    for mesh_file in mesh_files:
        print('\nItem: ', mesh_file)
        index = index + 1
        if mesh_file.lower().endswith('.stl'):
            reduce_mesh_size(mesh_path, mesh_file, mesh_size)
        else:
            print('  not an STL. Skipping...')

        print('  finished ', index, '/', len(mesh_files))

    print('Finished')


def get_num_triangles():
    """Extracts the number of triangles in the currently active mesh.

    Args:
        None

    Returns:
        num_triangles (int): the number of triangles in the mesh.
    """
    current_object = bpy.context.active_object
    mesh = current_object.data
    num_triangles = len(mesh.polygons)
    return num_triangles


def reduce_mesh_size(mesh_path: str, mesh_file: str, mesh_size: float):
    """Reduces the mesh size so that the file is < 1MB.

    Args:
        mesh_path (string): path the mesh directory
        mesh_file (string): the mesh's file name

    Returns:
        None
    """
    current_mesh_path = os.path.join(mesh_path, mesh_file)

    # Create backup of mesh
    file_id = 0
    backup_created = False
    while not backup_created:
        file_id = file_id + 1
        backup_filename = current_mesh_path + '.' + str(file_id)
        if not path.exists(backup_filename):
            shutil.copyfile(current_mesh_path, backup_filename)
            backup_created = True
            print('  backup created: ', backup_filename)

    print('  size =  ', Path(current_mesh_path).stat().st_size)
    bpy.ops.import_mesh.stl(filepath=current_mesh_path)
    print('  tris =  ', get_num_triangles())

    max_triangles = (mesh_size * 1.0e6 - HEADER_SIZE) / TRIANGLE_SIZE

    ratio = max_triangles / get_num_triangles()
    print('  ratio = ', ratio)

    # TODO(andymcevoy): Possibly add a confirmation to accept/reject decimation
    if ratio < 1.0:
        print('  Reducing size of mesh...')
        modifier = bpy.context.active_object.modifiers.new('DecimateMod', 'DECIMATE')
        modifier.ratio = ratio
        modifier.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier='DecimateMod')

    # Assume file is from SolidWorks and always export to remove SOLID warning in Rviz
    bpy.ops.export_mesh.stl(filepath=current_mesh_path)

    print('  tris =  ', get_num_triangles())
    print('  size =  ', Path(current_mesh_path).stat().st_size)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
