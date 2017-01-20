# Rendering script
# Run by calling the blender executable with -b -P <script_name>
#
# process:
# 1) Load model given as a parameter
# 2) Create lamps
# 3) Create camera with constraint on rotation
# 4) Move camera around object and render shot at each step

import bpy
import os
import argparse

LIGHT_INTENSITY = 1.5
SHOTS_NUMBER = 4

# TODO: generic lamp positions according to mesh size
LAMP_POSITIONS = [(7.47, -7.22, 0.97), (-7.63, -7.22, 0.97)]
# cams = [[(-16.31, -15.55, 10), (1.26, 0.009, -0.81)], [(17.43, -14.49, 5.0), (1.45, 0.00, 0.87)]]

def camera_location_string(camera):
    return str(camera.rotation_euler.x) + ' ' + str(camera.rotation_euler.y) + ' ' + str(camera.rotation_euler.z)

def camera_rotation_string(camera):
    return str(camera.location.x) + ' ' + str(camera.location.y) + ' ' + str(camera.location.z)

def get_args():
  parser = argparse.ArgumentParser()

  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]

  # add parser rules
  parser.add_argument('-f', '--file', help="obj file to render")
  parser.add_argument('-u', '--furthest_vertice', help="furthest vertice")
  parser.add_argument('-n', '--shots_number', help="number of shots")
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args

args = get_args()
context = bpy.context

new_scene = bpy.data.scenes.new("Automated Render Scene")

# Load model
model_path = os.path.join(args.file)
bpy.ops.import_scene.obj(filepath=model_path, use_edges=True)

# -----------------------------------------
# Create camera with constraint on rotation
# -----------------------------------------

camera_data = bpy.data.cameras.new('Camera')
camera_object = bpy.data.objects.new('Camera', camera_data)
camera_constraint = camera_object.constraints.new(type='TRACK_TO')
# camera_constraint.target =
new_scene.objects.link(camera_object)
context.scene.camera = camera_object

# ---------
# Add lamps
# ---------

for lamp_position in LAMP_POSITIONS:
    lamp_data = bpy.data.lamps.new(name="Lamp", type='POINT')
    lamp_data.energy = LIGHT_INTENSITY
    lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
    lamp_object.location = lamp_position
    lamp_object.select = True
    new_scene.objects.link(lamp_object)

context.screen.scene = new_scene

# ------
# Shoot
# ------

for index in range(0, int(args.shots_number)):
    # context.scene.camera.position =
    print('Camera now at position: ' + camera_location_string(camera_object) + ' / rotation: ' + camera_rotation_string(camera_object))
    context.scene.render.filepath = 'renders/' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '.png'

    context.scene.render.resolution_x = 1920
    context.scene.render.resolution_y = 1080

    bpy.context.scene.update()
    print('Rendering image with resolution : ' + str(bpy.context.scene.render.resolution_x) + ' x ' + str(bpy.context.scene.render.resolution_y))
    bpy.ops.render.render(write_still=True, use_viewport=True)
