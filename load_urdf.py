import bpy

from bpy.props import (FloatProperty,
                       PointerProperty,
                       StringProperty)
from bpy.types import (Operator,
                       PropertyGroup)
import os
import pprint
import xml.etree.ElementTree as ET

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

        robot = LoadUrdf(urdf_pkg_path, urdf_filename)

        joint_min = -3
        joint_max = 3

        # TODO: return this dictionary after parsing the URDF
        # Dynamically create the same class
        # JointControllerProperties = type(
        #     # Class name
        #     "JointControllerProperties",

        #     # Base class
        #     (bpy.types.PropertyGroup, ),

        #     # Dictionary of properties
        #     {
        #         '__annotations__':
        #         {
        #             'joint0':
        #             (
        #                 FloatProperty,
        #                 {
        #                     'name': 'j0',
        #                     'description': 'desc',
        #                     'default': 0,
        #                     'min': joint_min,
        #                     'max': joint_max,
        #                     'update': float_callback
        #                 }
        #             ),
        #             'joint1':
        #             (
        #                 FloatProperty,
        #                 {
        #                     'name': 'j1',
        #                     'description': 'desc',
        #                     'default': 1,
        #                     'min': joint_min,
        #                     'max': joint_max,
        #                     'update': float_callback
        #                 }
        #             )
        #         }
        #     }
        # )
        # bpy.utils.register_class(JointControllerProperties)
        # bpy.types.Scene.joint_tool = PointerProperty(type=JointControllerProperties)
        # bpy.utils.register_class(URDF_PT_JointControllerPanel)

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

    def __init__(self, pkg_path, urdf_filename):

        # Remove last dir in pkg_path, conflicts with 'package://package_name' in mesh filename
        self.pkg_path = os.path.split(pkg_path[0:-1])[0]
        self.urdf_filename = urdf_filename

        # Initialize variables
        self.links = {}
        self.joints = {}

        self.ParseUrdf()

    def ParseUrdf(self):
        # Open the URDF and get root node:
        try:
            tree = ET.parse(self.urdf_filename)
        except ET.ParseError:
            print('ERROR: Could not parse urdf file.')

        urdf_root = tree.getroot()

        # First parse for all links with meshes and load mesh
        for child in urdf_root:
            if child.tag == 'link':
                print('INFO: found link = ', child.get('name'))
                self.ProcessLink(child)
            if child.tag == 'joint':
                print('INFO: found joint = ', child.get('name'))
                self.ProcessJoint(child)

        pprint.pprint(self.links)
        pprint.pprint(self.joints)

    def ProcessLink(self, link):
        # Create empty object to attach to joint object and hold stl
        link_name = link.get('name')
        new_link = bpy.data.objects.new(link_name, None)
        bpy.context.scene.collection.objects.link(new_link)
        self.links[link_name] = {
            'mesh_path': None,
            'xyz': [0, 0, 0],
            'rpy': [0, 0, 0]
        }

        visual = link.find('visual')
        if None == visual:
            print('INFO: Link has no visual info')
            return

        origin = visual.find('origin')
        if None == origin:
            print('INFO: origin not found, setting to Identity.')
        else:
            xyz = [float(i) for i in origin.get('xyz').split()]
            rpy = [float(i) for i in origin.get('rpy').split()]
            self.links[link_name]['xyz'] = xyz
            self.links[link_name]['rpy'] = rpy

        geom = visual.find('geometry')
        if None == geom:
            print('WARN: ', link.get('name'), ' has no <geometry> tag.')
            return

        mesh = geom.find('mesh')
        if None == mesh:
            print('WARN: Primitive geometry not supported.')
            return

        mesh_path = mesh.get('filename')
        if None == mesh_path:
            print('WARN: No mesh found.')
            return

        # Replace ROS convention and get abs path to mesh file
        if 'package://' in mesh_path:
            mesh_path = os.path.join(self.pkg_path, mesh_path.replace('package://', ''))
            self.links[link_name]['mesh_path'] = mesh_path
            return

        print('ERROR: Expected ROS package syntax.')

        # TODO: Load STLs once parents and xyz rpy has been found from joints.
        # Import STL and change name to match link name
        # bpy.ops.import_mesh.stl(filepath=mesh_path)
        # stl = bpy.context.selected_objects[0]
        # stl.name = link.get('name')

    def ProcessJoint(self, joint):
        joint_name = joint.get('name')
        new_joint = bpy.data.objects.new(joint_name, None)
        bpy.context.scene.collection.objects.link(new_joint)
        self.joints[joint_name] = {
            'type': 'fixed',
            'parent': None,
            'child': None,
            'axis': [0, 0, 0],
            'limit': [0, 0]
        }

        joint_type = joint.get('type')
        if None == joint_type:
            print('ERROR: joint has no type.')
        else:
            self.joints[joint_name]['type'] = joint_type

        parent = joint.find('parent').get('link')
        if None == parent:
            print('ERROR: joint has no parent')
        else:
            self.joints[joint_name]['parent'] = parent

        child = joint.find('child').get('link')
        if None == child:
            print('ERROR: joint has no child')
        else:
            self.joints[joint_name]['child'] = child

        axis = joint.find('axis')
        if None != axis:
            self.joints[joint_name]['axis'] = [float(i) for i in axis.get('xyz').split()]

        limit = joint.find('limit')
        if None != limit:
            lower = limit.get('lower')
            upper = limit.get('upper')
            if None == lower or None == upper:
                print('ERROR: upper or lower limit not defined')
            else:
                self.joints[joint_name]['limit'] = [float(lower), float(upper)]


        return
