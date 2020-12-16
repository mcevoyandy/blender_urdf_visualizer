import bpy
import mathutils

from bpy.props import (FloatProperty,
                       PointerProperty,
                       StringProperty)
from bpy.types import (Operator,
                       PropertyGroup)
import os
import pprint
import xml.etree.ElementTree as ET

from . joint_controller import URDF_PT_JointControllerPanel

blender_links = {}

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
    # Callback for sliders. Find each object in the links dictionary and set its rotation.
    jt = context.scene.joint_tool
    for item in jt.items():
        name = item[0]
        value = item[1]
        # TODO: Check rotations of links, for some, proper axis of rotation is Y as I've brought it
        # into blender...
        blender_links[name].rotation_euler[2] = value


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

        # Dynamically create the same class
        JointControllerProperties = type(
            # Class name
            "JointControllerProperties",

            # Base class
            (bpy.types.PropertyGroup, ),

            # Annotations
            robot.annotations
        )
        URDF_PT_JointControllerPanel.set_joint_names(robot.joint_names)
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

    def __init__(self, pkg_path, urdf_filename):

        # Remove last dir in pkg_path, conflicts with 'package://package_name' in mesh filename
        self.pkg_path = os.path.split(pkg_path[0:-1])[0]
        self.urdf_filename = urdf_filename

        # Initialize variables
        self.links = {}
        self.joints = {}
        self.annotations = {}
        self.joint_names = []
        self.ParseUrdf()
        pprint.pprint(blender_links)

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

        self.GenerateJointAnnotations()
        pprint.pprint(self.annotations)

        self.ProcessLists()
        self.HideAxes()

    def GenerateJointAnnotations(self):
        # Generate annotations for dynamically creating the joint sliders.
        # Form should be (dictionary of tuples):
        # annotations: {
        #   'joint0': (
        #        FloatProperty, {
        #            'name': 'j0',
        #            'description': 'desc',
        #            'default': 0,
        #            'min': joint_min,
        #            'max': joint_max,
        #            'update': float_callback}),
        #    <repeated for each joint>
        self.annotations = {}
        for joint in self.joints:
            if self.joints[joint]['type'] == 'fixed':
                print('Fixed joint. Skipping ', joint)
                continue

            self.joint_names.append(joint)
            self.annotations[joint] = (FloatProperty,
            {
                'name': joint,
                'description': joint,
                'default': 0,
                'min': self.joints[joint]['limit'][0],
                'max': self.joints[joint]['limit'][1],
                'update': float_callback
            })
        return


    def ProcessLink(self, link):
        # Create empty link object to hold stl
        link_name = link.get('name')
        new_link = bpy.data.objects.new(link_name, None)
        new_link.empty_display_type = 'ARROWS'
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
            # Import STL
            bpy.ops.import_mesh.stl(filepath=mesh_path)
            stl_obj = bpy.context.selected_objects[0]
            stl_obj.parent = new_link
            return

        print('ERROR: Expected ROS package syntax.')


    def ProcessJoint(self, joint):
        joint_name = joint.get('name')

        # Create empty joint object
        new_joint = bpy.data.objects.new(joint_name, None)
        new_joint.empty_display_type = 'ARROWS'
        bpy.context.scene.collection.objects.link(new_joint)

        self.joints[joint_name] = {
            'type': 'fixed',
            'parent': None,
            'child': None,
            'xyz': None,
            'rpy': None,
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

        origin = joint.find('origin')
        xyz = [0, 0, 0]
        rpy = [0, 0, 0]
        if None != origin:
            xyz = [float(i) for i in origin.get('xyz').split()]
            rpy = [float(i) for i in origin.get('rpy').split()]
        self.joints[joint_name]['xyz'] = xyz
        self.joints[joint_name]['rpy'] = rpy

        axis = joint.find('axis')
        if None != axis:
            self.joints[joint_name]['axis'] = [float(i) for i in axis.get('xyz').split()]

        limit = joint.find('limit')
        if None != limit:
            lower = limit.get('lower')
            upper = limit.get('upper')
            if joint_type == 'continuous':
                self.joints[joint_name]['limit'] = [-6.28319, 6.28319]
            elif None == lower or None == upper:
                print('ERROR: upper or lower limit not defined')
            else:
                self.joints[joint_name]['limit'] = [float(lower), float(upper)]
        return


    def HideAxes(self):
        for joint_name in self.joints:
            bpy.context.scene.objects[joint_name].hide_set(True)

        for link_name in self.links:
            bpy.context.scene.objects[link_name].hide_set(True)


    def ProcessLists(self):
        for joint_name, joint_props in self.joints.items():
            # Joint object connects parent link to child link
            parent_link = bpy.context.scene.objects[joint_props['parent']]
            child_link = bpy.context.scene.objects[joint_props['child']]
            joint = bpy.context.scene.objects[joint_name]

            joint.parent = parent_link
            joint.location = joint_props['xyz']
            joint.rotation_euler = joint_props['rpy']

            child_link.parent = joint

            blender_links[joint_name] = child_link
        return
