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
from random import randint

# Helper methods
def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()
    direction = point - loc_camera
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj_camera.rotation_euler = rot_quat.to_euler()

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

# Live debugging (uncomment and paste in blender console for easier debugging)
# shots_number = 4
# furthest_vertex = 9
# context.scene.render.filepath = '/Users/pascal/dev/glitch3d/renders/test.png'
# file = '/Users/pascal/dev/glitch3d/fixtures/skull_glitched.obj'

LIGHT_INTENSITY = 1.5
LAMP_NUMBER = 2
SHOTS_NUMBER = 4
FURTHEST_VERTEX_OFFSET = 4

# Scene
new_scene = bpy.data.scenes.new("Automated Render Scene")
bpy.ops.scene.delete() # Delete old scene
context.screen.scene = new_scene # selects the new scene as the current one

# Render settings
context.scene.render.engine = 'CYCLES'
context.scene.render.resolution_x = 1920
context.scene.render.resolution_y = 1080

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath=model_path, use_edges=True)
model_object = bpy.data.objects['Glitch3D']

# -----------------------------------------
# Create camera with constraint on rotation
# -----------------------------------------
camera_data = bpy.data.cameras.new('Render Camera')
camera_data.type = 'PANO'
camera_data.cycles.fisheye_lens = 2.7
camera_data.cycles.fisheye_fov = 3.14159
camera_data.sensor_width = 8.8
camera_data.sensor_height = 6.6
bpy.data.objects.new('Render Camera', object_data=camera_data)
camera_object = bpy.data.objects['Render Camera']
camera_constraint = camera_object.constraints.new(type='TRACK_TO')
camera_constraint.target = model_object
new_scene.objects.link(camera_object)
context.scene.camera = camera_object
context.scene.camera.location = (furthest_vertex + FURTHEST_VERTEX_OFFSET, furthest_vertex + FURTHEST_VERTEX_OFFSET, 1.5)
look_at(camera_object, model_object.matrix_world.to_translation())

# ---------
# Add lamps
# ---------
for index in range(0, int(LAMP_NUMBER)):
    lamp_data = bpy.data.lamps.new(name="Lamp", type='POINT')
    lamp_data.energy = LIGHT_INTENSITY
    lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
    lamp_object.location = (furthest_vertex + 1, furthest_vertex + 1, randint(0,3))
    lamp_object.select = True
    new_scene.objects.link(lamp_object)

# ------
# Shoot
# ------

for index in range(0, int(shots_number)):
    # context.scene.camera.position =
    print('Camera now at position: ' + camera_location_string(camera_object) + ' / rotation: ' + camera_rotation_string(camera_object))
    context.scene.render.filepath = 'renders/' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '.png'

    bpy.context.scene.update()
    print('Rendering image with resolution : ' + str(bpy.context.scene.render.resolution_x) + ' x ' + str(bpy.context.scene.render.resolution_y))
    bpy.ops.render.render(write_still=True)
