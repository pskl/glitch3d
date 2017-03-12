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
# Use `debug()` to pry into the script

import bpy
import os
import argparse
import datetime
import bmesh
import random
import code
import math
import mathutils
import random
import uuid
import sys

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
SHADERS = ['ShaderNodeBsdfGlossy', 'ShaderNodeBsdfDiffuse', 'ShaderNodeBsdfVelvet', 'ShaderNodeEmission']

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
    context.scene.cycles.samples = 100
    context.scene.render.resolution_percentage = 100


# Delete current objects
for index, object in enumerate(bpy.data.objects):
    bpy.data.objects.remove(object)

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
model_object = bpy.data.objects[0]

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
camera_object.location = (8, 8, 1)

empty_materials()

# Add reflectors
bpy.ops.mesh.primitive_plane_add(location=(0,8 + REFLECTOR_LOCATION_PADDING, 0))
bpy.ops.mesh.primitive_plane_add(location=(8 + REFLECTOR_LOCATION_PADDING,0,0))
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 8))

plane1 = bpy.data.objects['Plane']
plane2 = bpy.data.objects['Plane.001']
plane3 = bpy.data.objects['Plane.002']

# Adjust camera
context.scene.camera = camera_object
look_at(camera_object, model_object)
make_object_gold(model_object)

plane1.rotation_euler.x += math.radians(90)
plane2.rotation_euler.x += math.radians(90)
plane2.rotation_euler.z += math.radians(90)

for plane in [plane1, plane2, plane3]:
    make_object_reflector(plane)

# Make floor
bpy.ops.mesh.primitive_plane_add(location=(0,0,-2))
floor = bpy.data.objects['Plane.003']
floor.scale = (8,8,8)
floor_material = create_cycles_material()
assign_texture_to_material(floor_material, random_texture())
assign_material(floor, floor_material)

# Add props
props = []

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
    props.append(object)
    new_material = create_cycles_material()
    assign_texture_to_material(new_material, random_texture())
    assign_material(object, new_material)

for index in range(0, int(PROPS_NUMBER)):
    bpy.ops.mesh.primitive_torus_add(location=rand_location(), rotation=rand_rotation(), major_radius=rand_scale(), minor_radius=rand_scale())
    if index == 0:
        object_name = 'Torus'
    elif index > 9:
        object_name = 'Torus.0' + str(index)
    elif index > 99:
        object_name = 'Torus.' + str(index)
    else:
        object_name = 'Torus.00' + str(index)
    object = bpy.data.objects[object_name]
    props.append(object)
    new_material = create_cycles_material()
    assign_texture_to_material(new_material, random_texture())
    assign_material(object, new_material)

for index in range(0, int(PROPS_NUMBER)):
    bpy.ops.mesh.primitive_cone_add(location=rand_location(), depth=1.0, rotation=rand_rotation(), radius1=rand_scale(), radius2=rand_scale())
    if index == 0:
        object_name = 'Cone'
    elif index > 9:
        object_name = 'Cone.0' + str(index)
    elif index > 99:
        object_name = 'Cone.' + str(index)
    else:
        object_name = 'Cone.00' + str(index)
    object = bpy.data.objects[object_name]
    props.append(object)
    new_material = create_cycles_material()
    assign_texture_to_material(new_material, random_texture())
    assign_material(object, new_material)

# Import guns
for index in range(0, 5):
    model_path_m4a1 = os.path.join('fixtures/m4a1.obj')
    bpy.ops.import_scene.obj(filepath = model_path_m4a1, use_edges=True)
    if index == 0:
        object_name = 'm4a1'
    elif index > 9:
        object_name = 'm4a1.0' + str(index)
    elif index > 99:
        object_name = 'm4a1.' + str(index)
    else:
        object_name = 'm4a1.00' + str(index)
    object = bpy.data.objects[object_name]
    props.append(object)
    object.location = rand_location()
    object.scale = rand_scale_vector()
    object.rotation_euler = rand_rotation()
    new_material = create_cycles_material()
    assign_texture_to_material(new_material, random_texture())
    assign_material(object, new_material)

# Add background to world
world = bpy.data.worlds[0]
world.use_nodes = True
world_node_tree = world.node_tree
gradient_node = world_node_tree.nodes.new(type="ShaderNodeTexGradient")
texture_node = world_node_tree.nodes.new(type="ShaderNodeTexGradient")

output_node = world_node_tree.nodes['Background']
texture_node = world_node_tree.nodes.new('ShaderNodeTexture')
world_node_tree.links.new(texture_node.outputs[0], output_node.inputs[0])
texture_path = os.path.expanduser('fixtures/textures/25.jpg')
new_texture = bpy.data.textures.new('ColorTex', type = 'IMAGE')
new_texture.image = bpy.data.images.load(texture_path)
texture_node.texture = new_texture

background_node = world_node_tree.nodes['Background']
world_node_tree.links.new(gradient_node.outputs['Color'], background_node.inputs['Color'])
gradient_node.gradient_type = 'EASING'

bpy.ops.object.mode_set(mode='EDIT')
# UV unwrap objects
for model in bpy.data.objects:
    context.scene.objects.active = model
    bpy.ops.uv.unwrap()
bpy.ops.object.mode_set(mode = 'OBJECT')

# ------
# Shoot
# ------
print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))
for index in range(0, int(shots_number)):
    print("-------------------------- " + str(index) + " --------------------------")
    rotate(model_object, index)
    for prop in props:
        prop.rotation_euler = rand_rotation()
    shoot(camera_object, model_object, output_name(index, model_path))

print('FINISHED ¯\_(ツ)_/¯')
