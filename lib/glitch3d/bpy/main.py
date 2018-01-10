# Rendering script
# Run by calling the blender executable with -b -P <script_name>
# Use `pry()` to pry into the script

import argparse

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
    parser.add_argument('-d', '--debug', help="render blank scene") # bool
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

args = get_args()
file = args.file
mode = args.mode
debug = (args.debug == 'True')
path = str(args.path)
animate = (args.animate == 'True')
shots_number = int(args.shots_number)

#####################################
#####################################
#####################################

import os, bpy, datetime, random, math, mathutils, random, uuid, sys, logging, string, colorsys, code
from subprocess import call

def load_file(file_path):
    # load and define function and vars in global namespace, yolo
    exec(open(file_path).read(), globals())

# Create directory for renders
directory = os.path.dirname('./renders')
if not os.path.exists(directory):
    os.makedirs(directory)

load_file(os.path.join(path + '/glitch3d/bpy/helpers.py'))
load_file(os.path.join(path + '/glitch3d/bpy/render_settings.py'))
load_file(os.path.join(path + '/glitch3d/bpy/lighting.py'))

# Fill base materials list
for mat in bpy.data.materials:
    MATERIALS_NAMES.append(mat.name)
print("Detected " + str(len(MATERIALS_NAMES)) + " materials in base scene: " + str(MATERIALS_NAMES))

# Create groups
WIREFRAMES = []
VORONOIED = []
OCEAN = []

for s in ['Texts', 'Lines', 'Displays', 'Reflectors']:
    bpy.data.groups.new(s)

LINES = bpy.data.groups['Lines'].objects
for primitive in PRIMITIVES:
    bpy.data.groups.new(primitive.lower().title())

FISHEYE = True
COLORS = rand_color_palette(5)
CAMERA_OFFSET = 1
INITIAL_CAMERA_LOCATION = (CAMERA_OFFSET, CAMERA_OFFSET, 1)
FIXTURES_FOLDER_PATH = path + '/../fixtures/'
TEXTURE_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'textures/'

# Scene
context = bpy.context
new_scene = bpy.data.scenes.new("Automated Render Scene")
context.screen.scene = new_scene
SCENE = new_scene

flush_objects()

camera_data = bpy.data.cameras.new(name = 'Camera')
bpy.data.objects.new('Camera', object_data=camera_data)
CAMERA = bpy.data.objects['Camera']
new_scene.objects.link(CAMERA)
SCENE.camera = CAMERA
CAMERA.location = INITIAL_CAMERA_LOCATION

if FISHEYE:
    CAMERA.data.type = 'PANO'
    CAMERA.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
    CAMERA.data.cycles.fisheye_lens = 12
    CAMERA.data.cycles.fisheye_fov = 2.5
    CAMERA.data.sensor_width = 20
    CAMERA.data.sensor_height = 20

render_settings(animate, mode, NORMALS_RENDERING)

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
SUBJECT = bpy.data.objects['0_glitch3d']
SUBJECT.select = True
bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
SUBJECT.location = ORIGIN

# make_object_glossy(SUBJECT, YELLOW, 0.01)
assign_material(SUBJECT, fetch_material('magma'))
SUBJECT.modifiers.new(name='Subject Subsurf', type='SUBSURF')

look_at(SUBJECT)
let_there_be_light(SCENE)

if debug == False:
    load_file(os.path.join(path + '/glitch3d/bpy/canvas', 'particles.py'))
    load_file (os.path.join(path + '/glitch3d/bpy/canvas', 'aether.py'))
    # load_file(os.path.join(path + '/glitch3d/bpy/canvas', 'lyfe.py'))
    # load_file(os.path.join(path + '/glitch3d/bpy/canvas', 'dreamatorium.py'))

    print('Rendering images with resolution: ' + str(SCENE.render.resolution_x) + ' x ' + str(SCENE.render.resolution_y))

    if animate:
        print('ANIMATION RENDERING BEGIN')
        SCENE.frame_start = 0
        SCENE.frame_end = NUMBER_OF_FRAMES

        x = 0.08
        while len(camera_path(x)) <= NUMBER_OF_FRAMES:
            x -= 0.01
        CAMERA_PATH = camera_path(x)

        for frame in range(0, NUMBER_OF_FRAMES):
            SCENE.frame_set(frame)
            animation_routine(frame)
            add_frame()
        shoot(output_name(model_path))

    else:
        print('STILL RENDERING BEGIN')
        for index in range(0, int(shots_number)):
            print("-------------------------- " + str(index) + " --------------------------")
            look_at(SUBJECT)
            still_routine(index)
            SCENE.frame_set(int(SCENE.frame_end/(index+1)))
            shoot(output_name(model_path, index))
else:
    look_at(SUBJECT)
    shoot(output_name(model_path))

# Save scene as .blend file
bpy.ops.wm.save_as_mainfile(filepath=output_name(model_path) + '.blend')

print("Files rendered:")
for p in RENDER_OUTPUT_PATHS:
    print(p)

if animate == False and debug == False:
    call(["python", os.path.join(path + '/glitch3d/bpy/post-processing/optimize.py')])
    call(["python", os.path.join(path + '/glitch3d/bpy/post-processing/mosaic.py')])

print('FINISHED ¯\_(ツ)_/¯')