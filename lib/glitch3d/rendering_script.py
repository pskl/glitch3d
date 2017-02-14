# Rendering script
# Run by calling the blender executable with -b -P <script_name>
#
# process:
# 1) Load model given as a parameter
# 2) Create emitting surfaces to act as lamps
# 3) Create camera
# 4) Rotate model and shoot image at each step
#
# Use `code.interact(local=dict(globals(), **locals()))` to pry into the script

import bpy
import os
import argparse
import datetime
import bmesh
import code
import math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from random import randint

exec(open("lib/glitch3d/helpers.py").read())

# Arguments parsing
args = get_args()
file = args.file
mode = args.mode
shots_number = int(args.shots_number)
x_boundary = int(args.x_boundary)
y_boundary = int(args.y_boundary)
z_boundary = int(args.z_boundary)
context = bpy.context
max_boundary = max([x_boundary, y_boundary, z_boundary])

REFLECTOR_SCALE = 5
REFLECTOR_STRENGTH = 8
PINK = [0.8, 0.2, 0.7, 1.0]
BLUE = [0.1, 0.4, 0.8, 1.0]

# Scene
new_scene = bpy.data.scenes.new("Automated Render Scene")
bpy.ops.scene.delete() # Delete old scene
context.screen.scene = new_scene # selects the new scene as the current one

# Render settings
context.scene.render.resolution_x = 1920
context.scene.render.resolution_y = 1080
if mode == 'high':
    context.scene.render.resolution_percentage = 100
    context.scene.render.engine = 'CYCLES'

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
model_object = bpy.data.objects['Glitch3D']

# Use center of mass to center object
model_object.select = True
bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
model_object.location = (0, 0, 0)

# Add reflectors
bpy.ops.mesh.primitive_plane_add(location=(max_boundary + 3, 0, 0))
bpy.ops.mesh.primitive_plane_add(location=(- max_boundary - 3, 0, 0))

plane1 = bpy.data.objects['Plane']
plane1.rotation_euler.z += 30
plane2 = bpy.data.objects['Plane.001']
plane2.rotation_euler.z += 30
plane1.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
plane2.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
emissive_material1 = bpy.data.materials.new('Emissive Material #1')
emissive_material2 = bpy.data.materials.new('Emissive Material #2')
emissive_material1.use_nodes = True
emissive_material2.use_nodes = True
emission_node1 = emissive_material1.node_tree.nodes.new('ShaderNodeEmission')
emission_node2 = emissive_material2.node_tree.nodes.new('ShaderNodeEmission')

# Set color
emission_node1.inputs[0].default_value = PINK
emission_node2.inputs[0].default_value = BLUE
# Set strength
emission_node1.inputs[1].default_value = REFLECTOR_STRENGTH
emission_node2.inputs[1].default_value = REFLECTOR_STRENGTH

assign_node_to_output(emissive_material1, emission_node1)
assign_node_to_output(emissive_material2, emission_node2)
assign_material(plane1, emissive_material1)
assign_material(plane2, emissive_material2)

# --------------
# Create camera
# --------------
camera_data = bpy.data.cameras.new('Render Camera')
bpy.data.objects.new('Render Camera', object_data=camera_data)
camera_object = bpy.data.objects['Render Camera']
new_scene.objects.link(camera_object)
camera_object.location = (0, 15, 0)

bpy.context.scene.objects.active = model_object
bpy.ops.object.mode_set(mode = 'EDIT')

# reposition(camera_object, model_object)
context.scene.camera = camera_object
look_at(camera_object, model_object)
assign_material(model_object, create_cycles_material())

# ------
# Shoot
# ------
print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))
for index in range(0, int(shots_number)):
    print("-------------------------- " + str(index) + " --------------------------")
    rotate(model_object, index)
    shoot(camera_object, model_object, output_name(index, model_path))

print('FINISHED ¯\_(ツ)_/¯')
