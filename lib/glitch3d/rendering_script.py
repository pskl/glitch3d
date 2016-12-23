# Rendering script
# Run by calling the blender executable with -b -P <script_name>

import bpy
import os
import argparse

LIGHT_INTENSITY = 4.0
lamps =[(7.47, -7.22, 0.97), (-7.63, -7.22, 0.97)]
cams = [[(-16.31, -15.55, 3.66), (1.45, 0.00, 0.87)], [(17.43, -14.49, 5.0), (1.45, 0.00, 0.87)]]

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
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args

args = get_args()

context = bpy.context

models = [args.file]

scene = bpy.data.scenes.new("Automated Render Scene")

camera_objects = []

# Add cameras
for index, cam in enumerate(cams):
    camera_data = bpy.data.cameras.new('Camera' + str(index))
    camera = bpy.data.objects.new('Camera' + str(index), camera_data)
    camera_objects.append(camera)
    camera.location = cam[0]
    camera.rotation_euler = cam[1]
    scene.objects.link(camera)

# Add lamps
for lamp in lamps:
    lamp_data = bpy.data.lamps.new(name="Lamp", type='POINT')
    lamp_data.energy = LIGHT_INTENSITY
    lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
    lamp_object.location = lamp
    lamp_object.select = True
    scene.objects.link(lamp_object)

context.screen.scene = scene
bpy.ops.scene.new(type='LINK_OBJECTS')
context.scene.name = 'Automated Render Scene'

for model_path in models:
    path = os.path.join(model_path)

    # cams = [c for c in context.scene.objects if c.type == 'CAMERA']

    # Load model
    bpy.ops.import_scene.obj(filepath=path, use_edges=True)

    for index, cam in enumerate(camera_objects):
        # Loop through cameras and take shots
        print('Camera now at position:' + camera_location_string(cam) + ' / rotation:' + camera_rotation_string(cam))
        context.scene.camera = cam
        context.scene.render.filepath = 'renders/' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '.png'
        scene.update()
        bpy.ops.render.render(write_still=True, use_viewport=True)
