# Rendering script
# Run by calling the blender executable with -b -P <script_name>
# Use `debug()` to pry into the script

import argparse

DEBUG=False

def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
    # add parser rules
    parser.add_argument('-f', '--file', help="obj file to render")
    parser.add_argument('-n', '--shots-number', help="number of shots desired")
    parser.add_argument('-m', '--mode', help="quality mode: low | high")
    parser.add_argument('-p', '--path', help="root path of assets")
    parser.add_argument('-a', '--animate', help="render animation") # bool
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

args = get_args()
file = args.file
mode = args.mode
path = str(args.path)
animate = (args.animate == 'True')
shots_number = int(args.shots_number)

import os, bpy, datetime, bmesh, random, math, mathutils, random, uuid, sys, logging, string, colorsys, code

# Create directory for renders
directory = os.path.dirname('./renders')
if not os.path.exists(directory):
    os.makedirs(directory)

exec(open(os.path.join(path + '/glitch3d/bpy', 'helpers.py')).read())
exec(open(os.path.join(path + '/glitch3d/bpy', 'render_settings.py')).read())
exec(open(os.path.join(path + '/glitch3d/bpy', 'lighting.py')).read())

FISHEYE = True
COLORS = rand_color_palette(5)
INITIAL_CAMERA_LOCATION = (3, 3, 1)
FIXTURES_FOLDER_PATH = path + '/../fixtures/'
TEXTURE_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'textures/'

# Scene
context = bpy.context
new_scene = bpy.data.scenes.new("Automated Render Scene")
bpy.ops.scene.delete() # Delete old scene
context.screen.scene = new_scene # selects the new scene as the current one

flush_all_objects()

camera_data = bpy.data.cameras['Camera']
bpy.data.objects.new('Camera', object_data=camera_data)
CAMERA = bpy.data.objects['Camera']
new_scene.objects.link(CAMERA)
context.scene.camera = CAMERA
CAMERA.location = INITIAL_CAMERA_LOCATION

if FISHEYE:
    CAMERA.data.type = 'PANO'
    CAMERA.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
    CAMERA.data.cycles.fisheye_lens = 12
    CAMERA.data.cycles.fisheye_fov = 2.5
    CAMERA.data.sensor_width = 20
    CAMERA.data.sensor_height = 20

render_settings(context.scene, animate, mode)

# Initialize groups
for primitive in PRIMITIVES:
    bpy.data.groups.new(primitive.lower().title())

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
SUBJECT = bpy.data.objects['glitch3d']
SUBJECT.select = True
bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
SUBJECT.location = ORIGIN
make_object_glossy(SUBJECT, YELLOW, 0.1)
voronoize(SUBJECT)

let_there_be_light(context.scene)

exec(open(os.path.join(path + '/glitch3d/bpy/canvas', 'dreamatorium.py')).read())

print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))

if animate:
    print('ANIMATION RENDERING BEGIN')
    context.scene.frame_start = 0
    context.scene.frame_end   = NUMBER_OF_FRAMES
    bpy.ops.screen.frame_jump(end=False)
    camera_path = camera_path(0.08)

    for frame in range(0, NUMBER_OF_FRAMES):
        bpy.context.scene.frame_set(frame)
        animation_routine(frame - 1)
        for ob in context.scene.objects:
            ob.keyframe_insert(data_path="location", index=-1)
    bpy.ops.screen.frame_jump(end=False)
    shoot(output_name(index, model_path))

else:
    print('STILL RENDERING BEGIN')
    for index in range(0, int(shots_number)):
        print("-------------------------- " + str(index) + " --------------------------")
        still_routine()
        look_at(SUBJECT)
        shoot(output_name(index, model_path))


print('FINISHED ¯\_(ツ)_/¯')
