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
from random import randint

# Helper methods
def look_at(camera_object, point):
    location_camera = camera_object.matrix_world.to_translation()
    location_point = point.matrix_world.to_translation()
    direction = location_point - location_camera
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera_object.rotation_euler = rot_quat.to_euler()

def shoot(camera, object, filepath):
    look_at(camera, object.matrix_world.to_translation())
    print('Camera now at position: ' + camera_location_string(camera) + ' / rotation: ' + camera_rotation_string(camera_object))
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

def output_name(index, model_path):
    return str('renders/' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '.png')

def randomize_material(model_object):
    model_material = bpy.data.materials.new('Model Material')
    model_material.use_shadeless = True
    model_material.emit = 1
    model_material.diffuse_color = (randint(0,1), randint(0,1), randint(0,1))
    model_material.diffuse_shader = 'TOON'
    model_object.data.materials.append(model_material)

def get_args():
  parser = argparse.ArgumentParser()

  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]

  # add parser rules
  parser.add_argument('-f', '--file', help="obj file to render")
  parser.add_argument('-u', '--furthest_vertex', help="furthest vertice")
  parser.add_argument('-n', '--shots_number', help="number of shots")
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args

def camera_location_string(camera):
    return str(camera.rotation_euler.x) + ' ' + str(camera.rotation_euler.y) + ' ' + str(camera.rotation_euler.z)

def camera_rotation_string(camera):
    return str(camera.location.x) + ' ' + str(camera.location.y) + ' ' + str(camera.location.z)

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

LIGHT_INTENSITY = 1.5
LAMP_NUMBER = 5
SHOTS_NUMBER = 4
FURTHEST_VERTEX_OFFSET = 1

# Scene
new_scene = bpy.data.scenes.new("Automated Render Scene")
bpy.ops.scene.delete() # Delete old scene
context.screen.scene = new_scene # selects the new scene as the current one

# Render settings
context.scene.render.engine = 'CYCLES'
context.scene.render.resolution_x = 1920
context.scene.render.resolution_y = 1080
context.scene.render.resolution_percentage = 100

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath=model_path, use_edges=True)
model_object = bpy.data.objects['Glitch3D']

# --------------
# Create camera
# --------------
camera_data = bpy.data.cameras.new('Render Camera')
bpy.data.objects.new('Render Camera', object_data=camera_data)
camera_object = bpy.data.objects['Render Camera']
new_scene.objects.link(camera_object)
context.scene.camera = camera_object
context.scene.camera.location = (model_object.location.x + 3, model_object.location.y + 3, model_object.location.z + 1)
look_at(camera_object, model_object)

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
    lamp_object.select = True
    new_scene.objects.link(lamp_object)

# ------
# Shoot
# ------
print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))
for index in range(0, int(SHOTS_NUMBER)):
    rotate(model_object)
    randomize_material(model_object)
    model_object.rotation_euler.z = model_object.rotation_euler.z + 0.5
    shoot(camera_object, model_object, output_name(index, model_path))

print('FINISHED ¯\_(ツ)_/¯')
