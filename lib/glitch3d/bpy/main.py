# Rendering script
# Run by calling the blender executable with -b -P <script_name>
# Use `pry()` to pry into the script
import argparse, random, math, os, code

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
    parser.add_argument('-frames', '--frames', help="number of frames") # int
    parser.add_argument('-normals', '--normals', help="normal render") # bool
    parser.add_argument('-d', '--debug', help="render blank scene with subject for testing purposes") # bool
    parser.add_argument('-width', '--width', help="width of render") # bool
    parser.add_argument('-eight', '--eight', help="height of render") # bool
    parser.add_argument('-assets', '--assets', help="user assets path") # bool
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

args = get_args()
file = args.file
mode = args.mode
debug = (args.debug == 'True')
path = str(args.path)
animate = (args.animate == 'True')
shots_number = int(args.shots_number)
width = int(args.width)
height = int(args.eight)

# TODO: add proper args validation cycle
#####################################
#####################################
#####################################

NUMBER_OF_FRAMES = int(args.frames)
NORMALS_RENDERING = (args.normals == 'True')

# Randomize module usage at runtime
MODULES_AVAILABLE = []
canvas_path = os.path.dirname(__file__) + '/canvas'
for f in os.listdir(canvas_path):
    if os.path.isfile(os.path.join(canvas_path, f)) and f != 'canvas.py':
        MODULES_AVAILABLE.append(f[0:-3])
MODULES_ENABLED = MODULES_AVAILABLE if debug else random.sample(MODULES_AVAILABLE, int(random.uniform(0, len(MODULES_AVAILABLE)) + 1))
MODULES_ENABLED = ['fernandez', 'abstract']
print("modules enabled: " + str(list(MODULES_ENABLED)))

SCENE_NAME = "glitch3d"
BAKED = []
REFLECTOR_SCALE = random.uniform(9, 10)
REFLECTOR_STRENGTH = random.uniform(12, 15)
REFLECTOR_LOCATION_PADDING = random.uniform(10, 12)
REPLACE_TARGET = str(random.uniform(0, 9))
REPLACEMENT = str(random.uniform(0, 9))
OSL_ENABLED = True
ORIGIN  = (0,0,2)
SCATTER_INTENSITY = 0.015
ABSORPTION_INTENSITY = 0.25
DISPLAY_SCALE = (2, 2, 2)
PRIMITIVES = ['Pyramid', 'Cube']
props = []
YELLOW = (1, 0.7, 0.1, 1)
GREY = (0.2, 0.2, 0.2 ,1)
BLUE = (0.1, 0.1, 0.8, 0.4)
PINK = (0.8, 0.2, 0.7, 1.0)
RENDER_OUTPUT_PATHS = []
FIXED_CAMERA = False
FUNCTIONS = {
    (lambda x: math.sin(x) * math.cos(20*x)): 4,
    (lambda x: math.sin(x) * math.sin(20*x)): 3,
    (lambda x: INITIAL_CAMERA_LOCATION[2]): 2,
    (lambda x: x) : 2,
    math.sin : 1,
    math.cos : 1,
    (lambda x: 0.5 * math.sin(0.5*x) * math.cos(x)) : 1,
    (lambda x: random.uniform(1, 10) * math.cos(x) ** 3) : 1,
    (lambda x: random.uniform(1, 10)) : 1,
    (lambda x: random.uniform(1, 2) + random.uniform(0.75, 3) * math.sin(random.uniform(0.1, 1)*x) + math.cos(random.uniform(0.75, 5)*x)) : 1,
    (lambda x: math.sin(math.pi*x) + x + 3 * math.pi) : 1,
    (lambda x: x**3 + math.cos(x/2)) : 2,
    (lambda x: random.uniform(1, 10) * math.sin(x)): 3
}

import importlib.util, os, ntpath, bpy, datetime, math, random, mathutils, random, uuid, sys, logging, string, colorsys, code, numpy
from subprocess import call

def load_file(file_path):
    # load and define function and vars in global namespace, yolo
    exec(open(file_path).read(), globals())

def load_module_path(file_path):
    print("loading module " + file_path)
    sys.path.append(os.path.dirname(os.path.expanduser(file_path)))

# Create directory for renders
directory = os.path.dirname('./renders')
if not os.path.exists(directory):
    os.makedirs(directory)

load_file(os.path.join(path + '/glitch3d/bpy/helpers.py'))
load_file(os.path.join(path + '/glitch3d/bpy/render_settings.py'))
load_file(os.path.join(path + '/glitch3d/bpy/lighting.py'))

# Create groups
for s in ['texts', 'lines', 'displays', 'reflectors', 'neons']:
    bpy.data.groups.new(s)

LINES = bpy.data.groups['lines'].objects
for primitive in PRIMITIVES:
    bpy.data.groups.new(primitive.lower().title())

FISHEYE = True
COLORS = rand_color_palette(5)
CAMERA_OFFSET = 5
INITIAL_CAMERA_LOCATION = (CAMERA_OFFSET, CAMERA_OFFSET, random.uniform(0, 8))
FIXTURES_FOLDER_PATH = args.assets if arg.assets else path + '/../fixtures/'
TEXTURE_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'textures/'
HEIGHT_MAP_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'height_maps/'
TEXT_FILE_PATH = FIXTURES_FOLDER_PATH + 'text/strings.txt'

print("Loading materials...")
MATERIALS_NAMES = []
load_osl_materials(FIXTURES_FOLDER_PATH + 'osl-shaders/')
for mat in bpy.data.materials: # merge base scene materials + osl shaders
    if mat.name != 'emission':
      MATERIALS_NAMES.append(mat.name)
print("Detected " + str(len(MATERIALS_NAMES)) + " materials in base scene: " + str(MATERIALS_NAMES))

# Scene
context = bpy.context
new_scene = bpy.data.scenes[SCENE_NAME]
context.screen.scene = new_scene
SCENE = new_scene
SCENE.render.engine = 'CYCLES'

flush_objects()

camera_data = bpy.data.cameras.new(name = 'CAMERA')
bpy.data.objects.new('CAMERA', object_data=camera_data)
CAMERA = bpy.data.objects['CAMERA']
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

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
SUBJECT = bpy.data.objects['0_glitch3d_' + ntpath.basename(file).replace("_glitched.obj", '')]
SUBJECT.select = True
center(SUBJECT)
SUBJECT.location = ORIGIN
SUBJECT.modifiers.new(name='Subject Subsurf', type='SUBSURF')
let_there_be_light(SCENE)
random.shuffle(list(MODULES_ENABLED))

if debug == False:
    for module in MODULES_ENABLED:
        load_module_path(os.path.join(path + '/glitch3d/bpy/canvas', module + '.py'))
        mod = __import__(module)
        new_canvas = eval("mod." + module[:1].upper() + module[1:] + "(locals())")
        new_canvas.render()

    render_settings(animate, mode, NORMALS_RENDERING, width, height)
    print('Rendering images with resolution: ' + str(SCENE.render.resolution_x) + ' x ' + str(SCENE.render.resolution_y))

    CAMERA_PATH = camera_path(NUMBER_OF_FRAMES)
    # create_line('camera_path', CAMERA_PATH, random.choice(COLORS), 0.01, ORIGIN).name = "camera_path"
    assert len(CAMERA_PATH) >= NUMBER_OF_FRAMES

    SCENE.frame_start = 0
    SCENE.frame_end = NUMBER_OF_FRAMES
    for frame in range(0, NUMBER_OF_FRAMES):
        SCENE.frame_set(frame)
        animation_routine(frame, CAMERA_PATH, SUBJECT, MATERIALS_NAMES, COLORS)
        look_at(SUBJECT)
        add_frame(bpy.data.objects, set(BAKED))

    if animate:
        print('ANIMATION RENDERING BEGIN')
        output_path = output_name(model_path)
        print('AVI file -> ' + output_path)
        shoot(output_path)
    else:
        print('STILL RENDERING BEGIN')
        for index in range(0, shots_number):
            frame_cursor = int(index * (SCENE.frame_end / shots_number))
            print('>> FRAME #' + str(frame_cursor))
            SCENE.frame_set(int(SCENE.frame_end/(index+1)))
            output_path = output_name(model_path, index)
            print("-------------------------- " + str(index) + " --------------------------")
            print("PNG file -> " + output_path)
            shoot(output_path)
else:
    look_at(SUBJECT)
    shoot(output_name(model_path))

# Save scene as .blend file
bpy.ops.wm.save_as_mainfile(filepath=output_name(model_path) + '.blend')

print("Files rendered with " + str(NUMBER_OF_FRAMES) + " frames in simulation:")
for p in RENDER_OUTPUT_PATHS:
    print(p)

if animate == False and debug == False:
    call(["python3", os.path.join(path + '/glitch3d/bpy/post-processing/optimize.py')] + [ str(bpy.context.scene.render.resolution_x), str(bpy.context.scene.render.resolution_y) ] + RENDER_OUTPUT_PATHS)
    call(["python3", os.path.join(path + '/glitch3d/bpy/post-processing/palette.py')] + list(map(str, list(map(tuple, COLORS)))) + [os.path.join(path + '/../fixtures/fonts/helvetica_neue.ttf')])
    if shots_number > 1:
      call(["python3", os.path.join(path + '/glitch3d/bpy/post-processing/average.py')] + RENDER_OUTPUT_PATHS)
    if shots_number > 10:
        call(["python3", os.path.join(path + '/glitch3d/bpy/post-processing/mosaic.py')])
print('FINISHED ¯\_(ツ)_/¯')
sys.exit()