# Rendering script
# Run by calling the blender executable with -b -P <script_name>
# Disclaimer: I never did Python before so this is mostly hacks
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
import random
import code
import math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import random

exec(open("lib/glitch3d/bpy/helpers.py").read())

# Arguments parsing
args = get_args()
file = args.file
mode = args.mode
shots_number = int(args.shots_number)

context = bpy.context

REFLECTOR_SCALE = 5
REFLECTOR_STRENGTH = 12
REFLECTOR_LOCATION_PADDING = 10
PROPS_NUMBER = 100
SHADERS = ['ShaderNodeBsdfGlossy', 'ShaderNodeBsdfDiffuse', 'ShaderNodeBsdfVelvet']

# Scene
new_scene = bpy.data.scenes.new("Automated Render Scene")
bpy.ops.scene.delete() # Delete old scene
context.screen.scene = new_scene # selects the new scene as the current one

# Render settings
context.scene.render.resolution_x = 1920
context.scene.render.resolution_y = 1080
context.scene.render.engine = 'CYCLES'
context.scene.render.resolution_percentage = 25
# bpy.context.scene.cycles.device = 'GPU'
context.scene.render.image_settings.compression = 0
context.scene.cycles.samples = 25
context.scene.render.image_settings.color_mode ='RGBA'
context.scene.render.image_settings.file_format='PNG'

if mode == 'high':
    context.scene.render.image_settings.compression = 90
    context.scene.cycles.samples = 500
    context.scene.render.resolution_percentage = 100

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
model_object = bpy.data.objects['Glitch3D']

# Use center of mass to center object
model_object.select = True
bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
model_object.location = (0, 0, 0)

# --------------
# Create camera
# --------------
camera_data = bpy.data.cameras.new('Render Camera')
bpy.data.objects.new('Render Camera', object_data=camera_data)
camera_object = bpy.data.objects['Render Camera']
new_scene.objects.link(camera_object)
camera_object.location = (8, 8, 0)

# Add reflectors
bpy.ops.mesh.primitive_plane_add(location=(0,8 + REFLECTOR_LOCATION_PADDING, 0))
bpy.ops.mesh.primitive_plane_add(location=(8 + REFLECTOR_LOCATION_PADDING,0,0))

plane1 = bpy.data.objects['Plane']
plane2 = bpy.data.objects['Plane.001']

# Adjust camera
context.scene.camera = camera_object
look_at(camera_object, model_object)
assign_material(model_object, create_cycles_material())

for index, plane in enumerate([plane1, plane2]):
    plane.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
    plane.rotation_euler.x += math.radians(90)
    emissive_material = bpy.data.materials.new('Emissive Material #' + str(index))
    emissive_material.use_nodes = True
    emission_node = emissive_material.node_tree.nodes.new('ShaderNodeEmission')
    # Set color
    emission_node.inputs[0].default_value = rand_color_vector()
    # Set strength
    emission_node.inputs[1].default_value = REFLECTOR_STRENGTH
    assign_node_to_output(emissive_material, emission_node)
    assign_material(plane, emissive_material)

# Tilt one of the reflectors
plane2.rotation_euler.z += math.radians(90)

# Add other elements
for index in range(0, int(PROPS_NUMBER)):
    bpy.ops.mesh.primitive_cube_add(location=rand_location(),radius=rand_scale(), rotation=rand_rotation())
    if index == 0:
        object_name = 'Cube'
    elif index > 9:
        object_name = 'Cube.0' + str(index)
    elif index > 99:
        object_name = 'Cube.' + str(index)
    else:
        object_name = 'Cube.00' + str(index)
    object = bpy.data.objects[object_name]
    new_material = create_cycles_material()
    assign_random_texture_to_material(new_material)
    assign_material(object, new_material)

# ------
# Shoot
# ------
print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))
for index in range(0, int(shots_number)):
    print("-------------------------- " + str(index) + " --------------------------")
    rotate(model_object, index)
    shoot(camera_object, model_object, output_name(index, model_path))

print('FINISHED ¯\_(ツ)_/¯')
