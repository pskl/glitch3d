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
path = str(args.path)
animate = args.animate
shots_number = int(args.shots_number)
FIXTURES_FOLDER_PATH = path + '/../fixtures/'

DEBUG = False
FISHEYE = True
COLORS = rand_color_palette(5)
INITIAL_CAMERA_LOCATION = (4, 4, 1)
ANIMATE = (animate == 'True')

# DEBUG = True
if DEBUG:
    shots_number = 2
    import os
    mode = 'low'
    file = "/Users/pascal/dev/glitch3d/fixtures/skull.obj"
    FIXTURES_FOLDER_PATH = "/Users/pascal/dev/glitch3d/fixtures/"

TEXTURE_FOLDER_PATH = FIXTURES_FOLDER_PATH + 'textures/'

# Scene
new_scene = bpy.data.scenes.new("Automated Render Scene")
bpy.ops.scene.delete() # Delete old scene
context.screen.scene = new_scene # selects the new scene as the current one

# Initialize groups
for primitive in PRIMITIVES:
    bpy.data.groups.new(primitive.lower().title())

# Render settings
context.scene.render.resolution_x = 2000
context.scene.render.resolution_y = 2000
context.scene.render.engine = 'CYCLES'
context.scene.render.resolution_percentage = 25
# uncomment if GPU
# bpy.context.scene.cycles.device = 'GPU'
context.scene.render.image_settings.compression = 0
context.scene.cycles.samples = 25
context.scene.render.image_settings.color_mode ='RGBA'

if ANIMATE:
    context.scene.render.image_settings.file_format='H264'
else:
    context.scene.render.image_settings.file_format='PNG'

if mode == 'high':
    context.scene.render.image_settings.compression = 90
    context.scene.cycles.samples = 400
    context.scene.render.resolution_percentage = 100

# Add background to world

# This shit doesnt work in v 2.76
# bpy.data.worlds.remove(bpy.data.worlds[0])
world = bpy.data.worlds.new('A Brave New World')
world.use_nodes = True
make_world_volumetric(world)
context.scene.world = world

# Clean slate
flush_all_objects()

# Load model
model_path = os.path.join(file)

bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
model_object = bpy.data.objects[0]

# Load props
bpy.ops.import_scene.obj(filepath = os.path.join(FIXTURES_FOLDER_PATH + 'm4a1.obj'), use_edges=True)
m4a1 = bpy.data.objects['m4a1']
m4a1.location = rand_location()
m4a1.scale = (0.5, 0.5, 0.5)
props.append(m4a1)

# Use center of mass to center object
model_object.select = True
bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
model_object.location = ORIGIN
make_object_glossy(model_object, YELLOW)

# Add props
rand_primitive = random.choice(PRIMITIVES)
build_composite_object(rand_primitive, 4, 1)

# --------------
# Create camera
# --------------
camera_data = bpy.data.cameras.new('Camera')
bpy.data.objects.new('Camera', object_data=camera_data)
camera_object = bpy.data.objects['Camera']
new_scene.objects.link(camera_object)
camera_object.location = INITIAL_CAMERA_LOCATION

if FISHEYE:
    camera_object.data.type = 'PANO'
    camera_object.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
    camera_object.data.cycles.fisheye_lens = 12
    camera_object.data.cycles.fisheye_fov = 2.5
    camera_object.data.sensor_width = 20
    camera_object.data.sensor_height = 20

# LIGTHING
add_spotlight(15000, math.radians(60))

# Add reflectors
bpy.ops.mesh.primitive_plane_add(location=(0,8 + REFLECTOR_LOCATION_PADDING, 0))
bpy.ops.mesh.primitive_plane_add(location=(8 + REFLECTOR_LOCATION_PADDING,0,0))
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 30))
bpy.ops.mesh.primitive_plane_add(location=(0, 0, -2))

reflector1 = bpy.data.objects['Plane']
reflector2 = bpy.data.objects['Plane.001']
reflector3 = bpy.data.objects['Plane.002']

bpy.data.groups.new('Plane')
bpy.data.groups['Plane'].objects.link(reflector1)
bpy.data.groups['Plane'].objects.link(reflector2)
bpy.data.groups['Plane'].objects.link(reflector3)

reflector2.rotation_euler.x += math.radians(90)
reflector1.rotation_euler.x += math.radians(90)
reflector2.rotation_euler.z += math.radians(90)

make_object_reflector(reflector1)
make_object_reflector(reflector2)
make_object_reflector(reflector3)

# Set up virtual displays
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(0, 6, 2))
display1 = bpy.data.objects['Grid']
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(6, 0, 2))
display2 = bpy.data.objects['Grid.001']

bpy.data.groups.new('Displays')
bpy.data.groups['Displays'].objects.link(display1)
bpy.data.groups['Displays'].objects.link(display2)

display1.rotation_euler.x += math.radians(90)
display1.rotation_euler.z -= math.radians(90)
display2.rotation_euler.x += math.radians(90)
display2.rotation_euler.y += math.radians(90)
display2.rotation_euler.z += math.radians(120)

for display in bpy.data.groups['Displays'].objects:
    display.rotation_euler.x += math.radians(90)
    display.scale = (3,3,3)
    texture_object(display)
    unwrap_model(display)
    glitch(display)

glitch(m4a1)
make_object_gradient_fabulous(m4a1, rand_color(), rand_color())

# Adjust camera
context.scene.camera = camera_object
look_at(camera_object, model_object)

# Make floor
floor = bpy.data.objects['Plane.003']
bpy.data.groups['Plane'].objects.link(floor)
floor.scale = (20,20,20)
subdivide(floor, 8)
displace(floor)
texture_object(floor)

OCEAN = add_ocean(10, 20)

# Create lines
bpy.data.groups.new('Lines')
for i in range(0, 20):
    new_line = create_line('line' + str(uuid.uuid1()), series(30))
    new_line.location.z += i / 6

for i in range(0, 20):
    new_line = create_line('line' + str(uuid.uuid1()), series(30), 0.003, (0, 5, 2))
    new_line.location.z += i / 3
    new_line.rotation_euler.x += math.radians(90)

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

for plane in bpy.data.groups['Plane'].objects:
    unwrap_model(plane)

for obj in WIREFRAMES:
    wireframize(obj)

look_at(camera_object, model_object)
model_object.location.z += 2

# ------
# Shoot
# ------
print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))

if ANIMATE == True:
    print('ANIMATION RENDERING BEGIN')
    context.scene.frame_start = 0
    context.scene.frame_end   = NUMBER_OF_FRAMES
    bpy.ops.screen.frame_jump(end=False)

    for frame in range(1, NUMBER_OF_FRAMES):
        bpy.context.scene.frame_set(frame)

        dance_routine()

        for ob in context.scene.objects:
            ob.keyframe_insert(data_path="location", index=-1)

    bpy.ops.screen.frame_jump(end=False)
    shoot(camera_object, model_object, output_name(index, model_path))
else:
    print('STILL RENDERING BEGIN')
    for index in range(0, int(shots_number)):
        print("-------------------------- " + str(index) + " --------------------------")
        shoot(camera_object, model_object, output_name(index, model_path))
        dance_routine()


print('FINISHED ¯\_(ツ)_/¯')
