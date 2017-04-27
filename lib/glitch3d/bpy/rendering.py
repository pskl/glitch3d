# Rendering script
# Run by calling the blender executable with -b -P <script_name>
# Disclaimer: I never did Python before so this is mostly hacks
#
# process:
# 1) Load model given as a parameter
# 2) Create emitting surfaces to act as lamps
# 3) Create camera
# 4) Rotate model and shoot image at each step
#
# Use `debug()` to pry into the script
import os
exec(open(os.path.join(os.path.dirname(__file__), 'helpers.py')).read())

# Arguments parsing
args = get_args()
file = args.file
mode = args.mode
shots_number = int(args.shots_number)

FIXTURES_FOLDER_PATH = str(args.path) + '/../fixtures/'
TEXTURE_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'textures/'

# Scene
new_scene = bpy.data.scenes.new("Automated Render Scene")
bpy.ops.scene.delete() # Delete old scene
context.screen.scene = new_scene # selects the new scene as the current one

# Render settings
context.scene.render.resolution_x = 1920
context.scene.render.resolution_y = 1080
context.scene.render.engine = 'CYCLES'
context.scene.render.resolution_percentage = 25
# bpy.context.scene.cycles.device = 'GPU'
context.scene.render.image_settings.compression = 0
context.scene.cycles.samples = 25
context.scene.render.image_settings.color_mode ='RGBA'
context.scene.render.image_settings.file_format='PNG'

if mode == 'high':
    context.scene.render.image_settings.compression = 90
    context.scene.cycles.samples = 500
    context.scene.render.resolution_percentage = 200

# Add background to world
world = bpy.data.worlds.new('A Brave New World')
world.use_nodes = True
world_node_tree = world.node_tree
# Paint background with color
# world_node_tree.nodes['Background'].inputs[0].default_value = rand_color_vector()
context.scene.world = world

# Delete current objects
for index, obj in enumerate(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
model_object = bpy.data.objects[0]

# Load props
bpy.ops.import_scene.obj(filepath = os.path.join(FIXTURES_FOLDER_PATH + 'm4a1.obj'), use_edges=True)
m4a1 = bpy.data.objects['m4a1']

# Use center of mass to center object
model_object.select = True
bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
model_object.location = ORIGIN

# --------------
# Create camera
# --------------
camera_data = bpy.data.cameras.new('Camera')
bpy.data.objects.new('Camera', object_data=camera_data)
camera_object = bpy.data.objects['Camera']
new_scene.objects.link(camera_object)
camera_object.location = (8, 8, 1)

# Add reflectors
bpy.ops.mesh.primitive_plane_add(location=(0,8 + REFLECTOR_LOCATION_PADDING, 0))
bpy.ops.mesh.primitive_plane_add(location=(8 + REFLECTOR_LOCATION_PADDING,0,0))
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 8))

floor = bpy.data.objects['Plane']
reflector1 = bpy.data.objects['Plane.001']
reflector2 = bpy.data.objects['Plane.002']

# Adjust camera
context.scene.camera = camera_object
look_at(camera_object, model_object)
make_object_glossy(model_object, YELLOW)

floor.rotation_euler.x += math.radians(90)
reflector1.rotation_euler.x += math.radians(90)
reflector1.rotation_euler.z += math.radians(90)

make_object_reflector(reflector1)
make_object_reflector(reflector2)

# Make floor
bpy.ops.mesh.primitive_plane_add(calc_uvs=True, location=(0,0,-2))
floor = bpy.data.objects['Plane.003']
floor.scale = (20,20,20)
texture_object(floor)
subdivide(floor)
build_composite_cube(10,1)

for index in range(1, len(WORDS)):
    new_object = spawn_text()
    props.append(new_object)
    text_scale = random.uniform(0.75, 2)
    make_object_glossy(new_object, GREY)
    new_object.scale = (text_scale, text_scale, text_scale)
    new_object.location = rand_location()
    # pivot text to make it readable by camera
    new_object.rotation_euler.x += math.radians(90)
    new_object.rotation_euler.z += math.radians(90)

for model in bpy.data.objects:
    unwrap_model(model)
    if model.name.startswith('Cube'):
        wireframize(model)

# ------
# Shoot
# ------
print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))
for index in range(0, int(shots_number)):
    print("-------------------------- " + str(index) + " --------------------------")
    rotate(model_object, index)
    randomize_reflectors_colors()
    for prop in props:
        prop.location = rand_location()
    shoot(camera_object, model_object, output_name(index, model_path))

print('FINISHED ¯\_(ツ)_/¯')
