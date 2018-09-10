# Rendering script
# Run by calling the blender executable with -b -P <script_name>
# Use `pry()` to pry into the script
import sys, argparse, random, math, os, code, requests

def get_args():
  parser = argparse.ArgumentParser()
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]
  parser.add_argument('-f', '--file', help="obj file to render")
  parser.add_argument('-n', '--shots-number', help="number of shots desired")
  parser.add_argument('-m', '--mode', help="quality mode: low | high")
  parser.add_argument('-p', '--path', help="root path of gem assets")
  parser.add_argument('-a', '--animate', help="render animation") # bool
  parser.add_argument('-frames', '--frames', help="number of frames") # int
  parser.add_argument('-normals', '--normals', help="normal render") # bool
  parser.add_argument('-d', '--debug', help="render blank scene with subject for testing purposes") # bool
  parser.add_argument('-width', '--width', help="width of render") # int
  parser.add_argument('-eight', '--eight', help="height of render") # int
  parser.add_argument('-assets', '--assets', help="user assets path") # string
  parser.add_argument('-canvas', '--canvas', help="selection of canvas modules by name") # string
  parser.add_argument('-post', '--post-process', help="post-processing") # bool
  parser.add_argument('-webhook', '--webhook', help="webhook url") # string
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
post_process = (args.post_process == 'True')
assets = args.assets
webhook = args.webhook

# TODO: add proper args validation cycle
#####################################
#####################################
#####################################

try:
  NUMBER_OF_FRAMES = int(args.frames)
  NORMALS_RENDERING = (args.normals == 'True')

  # Randomize module usage at runtime or pick selection from arguments
  canvas_path = os.path.dirname(__file__) + '/canvas'
  MODULES_AVAILABLE = args.canvas.split(",") if args.canvas else [ f[0:-3] for f in os.listdir(canvas_path) if os.path.isfile(os.path.join(canvas_path, f)) and f != 'canvas.py']
  MODULES_ENABLED = MODULES_AVAILABLE if debug or args.canvas else random.sample(MODULES_AVAILABLE, int(random.uniform(0, len(MODULES_AVAILABLE)) + 1))
  print("modules enabled: " + str(list(MODULES_ENABLED)))

  FIXTURES_FOLDER_PATH = assets if assets else path + '/../fixtures/'
  TEXTURE_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'textures/'
  MODELS_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'models/'
  HEIGHT_MAP_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'height_maps/'
  FONT_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'fonts/'
  SCENE_NAME = "glitch3d"
  REFLECTOR_SCALE = random.uniform(9, 10)
  REFLECTOR_STRENGTH = random.uniform(12, 15)
  REFLECTOR_LOCATION_PADDING = random.uniform(10, 12)
  REPLACE_TARGET = str(random.uniform(0, 9))
  REPLACEMENT = str(random.uniform(0, 9))
  OSL_ENABLED = True
  ORIGIN  = (0,0,2)
  CANVAS_BOUNDARY = 6
  SCATTER_INTENSITY = 0.015
  ABSORPTION_INTENSITY = 0.25
  DISPLAY_SCALE = (2, 2, 2)
  PRIMITIVES = ['Pyramid', 'Cube']
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

  sys.path.append(os.environ['PYTHON_MODULES_PATH'])

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
  for primitive in PRIMITIVES:
      bpy.data.groups.new(primitive.lower().title())

  FISHEYE = True
  COLORS = rand_color_palette(5)
  CAMERA_OFFSET = 5
  INITIAL_CAMERA_LOCATION = (CAMERA_OFFSET, CAMERA_OFFSET, random.uniform(0, 8))
  TEXT_FILE_PATH = FIXTURES_FOLDER_PATH + 'text/strings.txt'

  print("Loading materials...")
  MATERIALS_NAMES = []
  load_osl_materials(FIXTURES_FOLDER_PATH + 'osl-shaders/')
  for mat in bpy.data.materials: # merge base scene materials + osl shaders
      if mat.name != 'emission':
        MATERIALS_NAMES.append(mat.name)
  print("Detected " + str(len(MATERIALS_NAMES)) + " materials in base scene: " + str(MATERIALS_NAMES))

  # Scene
  new_scene = bpy.data.scenes[SCENE_NAME]
  bpy.context.screen.scene = new_scene
  SCENE = new_scene
  SCENE.render.engine = 'CYCLES'

  flush_objects()

  camera_data = bpy.data.cameras.new(name = 'CAMERA')
  bpy.data.objects.new('CAMERA', object_data=camera_data)
  CAMERA = bpy.data.objects['CAMERA']
  new_scene.objects.link(CAMERA)
  SCENE.camera = CAMERA
  CAMERA.location = INITIAL_CAMERA_LOCATION
  SCENE.frame_start = 0
  SCENE.frame_end = NUMBER_OF_FRAMES

  if FISHEYE:
      CAMERA.data.type = 'PANO'
      CAMERA.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
      CAMERA.data.cycles.fisheye_lens = 12
      CAMERA.data.cycles.fisheye_fov = 2.5
      CAMERA.data.sensor_width = 20
      CAMERA.data.sensor_height = 20

  #####################################
  #####################################
  #####################################

  # Load model
  model_path = os.path.join(file)
  bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
  SUBJECT = bpy.data.objects['0_glitch3d_' + ntpath.basename(file).replace("_glitched.obj", '')]
  SUBJECT.select = True
  center(SUBJECT)
  SUBJECT.location = ORIGIN
  let_there_be_light(SCENE)
  random.shuffle(list(MODULES_ENABLED))

  for module in MODULES_ENABLED:
      load_module_path(os.path.join(path + '/glitch3d/bpy/canvas', module + '.py'))
      mod = __import__(module)
      new_canvas = eval("mod." + module[:1].upper() + module[1:] + "(locals())")
      new_canvas.render()

  render_settings(animate, mode, NORMALS_RENDERING, width, height, debug)
  print('Rendering images with resolution: ' + str(SCENE.render.resolution_x) + ' x ' + str(SCENE.render.resolution_y))

  if bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.bake_to_keyframes(frame_start=0, frame_end=NUMBER_OF_FRAMES)

  CAMERA_PATH = camera_path(NUMBER_OF_FRAMES)

  for frame in range(0, NUMBER_OF_FRAMES):
      bpy.context.scene.frame_set(frame)
      bpy.context.scene.camera.location = CAMERA_PATH[frame]
      SUBJECT.rotation_euler.z += math.radians(1)
      look_at(SUBJECT)
      add_frame([bpy.context.scene.camera], ["location", "rotation_euler"])

  if animate:
      print('ANIMATION RENDERING BEGIN')
      output_path = output_name(model_path)
      print('AVI file -> ' + output_path)
      shoot(output_path)
  else:
      print('STILL RENDERING BEGIN')
      for index in range(0, shots_number):
          frame_cursor = int(index * (bpy.context.scene.frame_end / shots_number))
          print('>> FRAME #' + str(frame_cursor))
          bpy.context.scene.frame_set(int(bpy.context.scene.frame_end/(index+1)))
          SUBJECT.rotation_euler.z = math.radians(index * (360.0 / shots_number))
          output_path = output_name(model_path, index)
          print("-------------------------- " + str(index) + " --------------------------")
          print("PNG file -> " + output_path)
          shoot(output_path)

  # Save scene as .blend file
  bpy.ops.wm.save_as_mainfile(filepath=output_name(model_path) + '.blend')

  print("Files rendered with " + str(NUMBER_OF_FRAMES) + " frames in simulation:")
  for p in RENDER_OUTPUT_PATHS:
      print(p)

  if post_process:
      load_file(os.path.join(path + '/glitch3d/bpy/post-processing/optimize.py'))
      if shots_number > 1:
        load_file(os.path.join(path + '/glitch3d/bpy/post-processing/average.py'))
        if shots_number > 10:
          load_file(os.path.join(path + '/glitch3d/bpy/post-processing/mosaic.py'))
      load_file(os.path.join(path + '/glitch3d/bpy/post-processing/palette.py'))
  print('FINISHED ¯\_(ツ)_/¯')
  sys.exit(0)

except Exception as e:
  if webhook:
    requests.post(webhook, data={'error': str(e)})
  if debug:
    raise e # See error
  sys.exit(1) # Just return 1 error code in production
