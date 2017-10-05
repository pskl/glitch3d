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

# Render settings
exec(open(os.path.join(os.path.dirname(__file__), 'render_settings.py')).read())

# Initialize groups
for primitive in PRIMITIVES:
    bpy.data.groups.new(primitive.lower().title())

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
make_object_glossy(model_object, YELLOW, 0.1)

# Add props
rand_primitive = random.choice(PRIMITIVES)
build_composite_object(rand_primitive, 4, 1)

# --------------
# Create camera
# --------------
camera_data = bpy.data.cameras.new('Camera')
bpy.data.objects.new('Camera', object_data=camera_data)
CAMERA = bpy.data.objects['Camera']
new_scene.objects.link(CAMERA)
CAMERA.location = INITIAL_CAMERA_LOCATION

if FISHEYE:
    CAMERA.data.type = 'PANO'
    CAMERA.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
    CAMERA.data.cycles.fisheye_lens = 12
    CAMERA.data.cycles.fisheye_fov = 2.5
    CAMERA.data.sensor_width = 20
    CAMERA.data.sensor_height = 20

exec(open(os.path.join(os.path.dirname(__file__), 'lighting.py')).read())

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
    display.scale = DISPLAY_SCALE
    texture_object(display)
    make_texture_object_transparent(display)
    unwrap_model(display)
    glitch(display)

glitch(m4a1)
make_object_gradient_fabulous(m4a1, rand_color(), rand_color())

# Adjust camera
context.scene.camera = CAMERA
look_at(model_object)

# Make floor
floor = bpy.data.objects['Plane.003']
bpy.data.groups['Plane'].objects.link(floor)
floor.scale = (20,20,20)
subdivide(floor, 8)
displace(floor)
texture_object(floor)

OCEAN = add_ocean(10, 20)

# Create lines as backdrop
bpy.data.groups.new('Lines')
for j in range(0,20):
    for i in range(0, 20):
        new_line = create_line('line' + str(uuid.uuid1()), series(30), 0.003, (j, -10, 2))
        new_line.location.z += i / 3

# Add flying letters, lmao
for index in range(1, len(WORDS)):
    new_object = spawn_text()
    props.append(new_object)
    text_scale = random.uniform(0.75, 3)
    make_object_glossy(new_object, rand_color(), 0.0)
    new_object.scale = (text_scale, text_scale, text_scale)
    new_object.location = rand_location()
    # pivot text to make it readable by camera
    new_object.rotation_euler.x += math.radians(90)
    new_object.rotation_euler.z += math.radians(90)

for plane in bpy.data.groups['Plane'].objects:
    unwrap_model(plane)

for obj in WIREFRAMES:
    wireframize(obj)

look_at(model_object)
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
    camera_path = camera_path(0.08)

    for frame in range(0, NUMBER_OF_FRAMES):
        bpy.context.scene.frame_set(frame)
        animation_routine(frame - 1)
        for ob in context.scene.objects:
            ob.keyframe_insert(data_path="location", index=-1)
    bpy.ops.screen.frame_jump(end=False)
    shoot(model_object, output_name(index, model_path))

else:
    print('STILL RENDERING BEGIN')
    for index in range(0, int(shots_number)):
        print("-------------------------- " + str(index) + " --------------------------")
        still_routine()
        shoot(camera_object, model_object, output_name(index, model_path))


print('FINISHED ¯\_(ツ)_/¯')
