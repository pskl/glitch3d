# Rendering script
# Run by calling the blender executable with -b -P <script_name>
#
# process:
# 1) Load model given as a parameter
# 2) Create lamps
# 3) Create camera
# 4) Rotate model and shoot image at each step

import bpy
import os
import argparse
import datetime
import bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from random import randint

exec(open("lib/glitch3d/helpers.py").read())

# Arguments parsing
args = get_args()
file = args.file
shots_number = args.shots_number
furthest_vertex = int(args.furthest_vertex)

context = bpy.context

# shots_number = 4
# furthest_vertex = 9
# context.scene.render.filepath = '/Users/pascal/dev/glitch3d/renders/test.png'
# file = '/Users/pascal/dev/glitch3d/fixtures/skull_glitched.obj'

LIGHT_INTENSITY = 1.0
LAMP_NUMBER = 10
SHOTS_NUMBER = 10
FURTHEST_VERTEX_OFFSET = 1

# Scene
new_scene = bpy.data.scenes.new("Automated Render Scene")
bpy.ops.scene.delete() # Delete old scene
context.screen.scene = new_scene # selects the new scene as the current one

# Render settings
# context.scene.render.engine = 'CYCLES'
context.scene.render.resolution_x = 1920
context.scene.render.resolution_y = 1080
context.scene.render.resolution_percentage = 50

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
lamp_data = bpy.data.lamps.new(name="Lamp", type='SUN')
lamp_data.energy = LIGHT_INTENSITY
lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
new_scene.objects.link(lamp_object)

for index in range(0, int(LAMP_NUMBER)):
    lamp_data = bpy.data.lamps.new(name="Lamp", type='POINT')
    lamp_data.energy = LIGHT_INTENSITY
    lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
    lamp_object.location = (furthest_vertex + randint(-10,2), furthest_vertex + randint(-10,2), randint(0,3))
    new_scene.objects.link(lamp_object)

# --------------
# Create camera
# --------------
camera_data = bpy.data.cameras.new('Render Camera')
bpy.data.objects.new('Render Camera', object_data=camera_data)
camera_object = bpy.data.objects['Render Camera']
new_scene.objects.link(camera_object)
camera_object.location = (0, model_object.location.y, model_object.location.z)
reposition(camera_object, model_object)
camera_object.rotation_euler = (1, 0, 0)
context.scene.camera = camera_object
look_at(camera_object, model_object)
shoot(camera_object, model_object, 'renders/dump.png')

# ------
# Shoot
# ------
print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))
for index in range(0, int(SHOTS_NUMBER)):
    print("-------------------------- " + str(index) + " --------------------------")
    randomize_material(model_object)
    shoot(camera_object, model_object, output_name(index, model_path))
    rotate(model_object)

print('FINISHED ¯\_(ツ)_/¯')
