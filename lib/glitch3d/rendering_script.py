# Rendering script
# Run by calling the blender executable with -b -P <script_name>

# bpy.data.objects ->

import bpy
import os
import argparse

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

lamps =[(7.47, -7.22, 0.97), (-7.63, -7.22, 0.97)]
cams = [[(-16.31, -15.55, 3.66), (1.45, 0.00, 0.87)], [(17.43, -14.49, 2.71), (1.45, 0.00, 0.87)]]
scene = bpy.data.scenes.new("Automated Render Scene")

# Add cameras
for cam in cams:
    camera_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", camera_data)
    camera.location = cam[0]
    camera.rotation_euler = cam[1]
    scene.objects.link(camera)

# Add lamps
for lamp in lamps:
    lamp_data = bpy.data.lamps.new(name="New Lamp", type='POINT')
    lamp_data.energy = 5.0
    lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
    scene.objects.link(lamp_object)
    lamp_object.location = lamp
    lamp_object.select = True
    scene.objects.active = lamp_object

scene.update()

for model_path in models:
    scene.camera = camera
    path = os.path.join(model_path)

    # Create new scene
    context.screen.scene = scene
    bpy.ops.scene.new(type='LINK_OBJECTS')
    context.scene.name = model_path
    cams = [c for c in context.scene.objects if c.type == 'CAMERA']

    # Load model
    bpy.ops.import_scene.obj(filepath=path, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl")

    for index, cam in enumerate(cams):
        context.scene.render.filepath = 'renders/' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '.png'
        context.scene.camera = cam
        scene.update()
        bpy.ops.render.render(write_still=True, use_viewport=True)
