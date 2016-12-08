# Rendering script
# Run by calling the blender executable with -b -P <script_name>

# bpy.data.objects -> is where the good shit is at

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
  parser.add_argument('-o', '--output', help="output png file")
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args

args = get_args()

context = bpy.context

models = [args.file]

first_camera_position = (-16.31218147277832, -15.556914329528809, 3.6613118648529053)
first_camera_rotation = (1.4517742395401, 0.0034271334297955036, 0.8768782019615173)
second_camera_position = (17.437292098999023, -14.494770050048828, 2.7116341590881348)
lamp_position_1 = (7.474725723266602, -7.22759485244751, 0.9717955589294434)
lamp_position_2 = (-7.632413864135742, -7.22759485244751, 0.9717955589294434)

scene = bpy.data.scenes.new("AutomatedRenderScene")

# camera
camera_data = bpy.data.cameras.new("Camera")
camera = bpy.data.objects.new("Camera", camera_data)
camera.location = first_camera_position
camera.rotation_euler = first_camera_rotation
scene.objects.link(camera)

# light
lamp_data = bpy.data.lamps.new(name="New Lamp", type='POINT')
lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
scene.objects.link(lamp_object)
lamp_object.location = lamp_position_1
lamp_object.select = True
scene.objects.active = lamp_object

scene.update()

for model_path in models:
    scene.camera = camera
    path = os.path.join(model_path)

    # make a new scene with cam and lights linked
    context.screen.scene = scene
    bpy.ops.scene.new(type='LINK_OBJECTS')
    context.scene.name = model_path
    cams = [c for c in context.scene.objects if c.type == 'CAMERA']

    #import model
    bpy.ops.import_scene.obj(filepath=path, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl")

    for c in cams:
        context.scene.camera = c
        print("Render ", model_path, context.scene.name, c.name)
        context.scene.render.filepath = args.output
        bpy.ops.render.render(write_still=True)
