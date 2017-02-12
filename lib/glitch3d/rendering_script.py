# Rendering script
# Run by calling the blender executable with -b -P <script_name>
#
# process:
# 1) Load model given as a parameter
# 2) Create lamps
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
shots_number = args.shots_number
furthest_vertex = int(args.furthest_vertex)

context = bpy.context

# context.scene.render.filepath = '/Users/pascal/dev/glitch3d/renders/test.png'
# file = '/Users/pascal/dev/glitch3d/fixtures/skull_glitched.obj'

LIGHT_INTENSITY = 0.8
LAMP_NUMBER = 10
SHOTS_NUMBER = 2
FURTHEST_VERTEX_OFFSET = 1
REFLECTOR_SCALE = 3

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

# ---------
# Add lamps
# ---------
# lamp_data = bpy.data.lamps.new(name="Lamp", type='SUN')
# lamp_data.energy = LIGHT_INTENSITY
# lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
# new_scene.objects.link(lamp_object)

# for index in range(0, int(LAMP_NUMBER)):
#     lamp_data = bpy.data.lamps.new(name="Lamp", type='POINT')
#     lamp_data.energy = LIGHT_INTENSITY
#     lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
#     lamp_object.location = (randint(-furthest_vertex, furthest_vertex), randint(-furthest_vertex, furthest_vertex), randint(-furthest_vertex, furthest_vertex))
#     new_scene.objects.link(lamp_object)

# Add reflectors
bpy.ops.mesh.primitive_plane_add(location=(furthest_vertex + 3, furthest_vertex + 3, model_object.location.z))
bpy.ops.mesh.primitive_plane_add(location=(- furthest_vertex - 3, - furthest_vertex - 3, model_object.location.z))

# Rotate reflectors
plane1 = bpy.data.objects['Plane']
plane1.rotation_euler.x += 30
plane2 = bpy.data.objects['Plane.001']
plane2.rotation_euler.x -= 30
plane1.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
plane2.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
emissive_material = bpy.data.materials.new('Emissive Material')
emissive_material.use_nodes = True
new_node = emissive_material.node_tree.nodes.new('ShaderNodeEmission')
assign_node_to_output(emissive_material, new_node)
assign_material(plane1, emissive_material)
assign_material(plane2, emissive_material)

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
for index in range(0, int(SHOTS_NUMBER)):
    print("-------------------------- " + str(index) + " --------------------------")
    shoot(camera_object, model_object, output_name(index, model_path))
    rotate(model_object, index)

print('FINISHED ¯\_(ツ)_/¯')
