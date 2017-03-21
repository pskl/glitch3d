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

context = bpy.context
fixtures_folder_path = str(args.path) + '/../fixtures/'
texture_folder_path = fixtures_folder_path + 'textures/'

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
    context.scene.cycles.samples = 400
    context.scene.render.resolution_percentage = 100

# Add background to world
world = bpy.data.worlds.new('A Brave New World')
world.use_nodes = True
world_node_tree = world.node_tree
world_node_tree.nodes['Background'].inputs[0].default_value = rand_color_vector()
context.scene.world = world

# Delete current objects
for index, obj in enumerate(bpy.data.objects):
    bpy.data.objects.remove(obj)

# Load model
model_path = os.path.join(file)
bpy.ops.import_scene.obj(filepath = model_path, use_edges=True)
model_object = bpy.data.objects[0]

# Load props
bpy.ops.import_scene.obj(filepath = os.path.join(fixtures_folder_path + 'm4a1.obj'), use_edges=True)
m4a1 = bpy.data.objects['m4a1']
texture_object(m4a1)
m4a1.location = rand_location()
m4a1.scale = rand_scale_vector()
m4a1.rotation_euler = rand_rotation()

bpy.ops.mesh.primitive_cube_add(location=rand_location(),radius=rand_scale(), rotation=rand_rotation())
cube = bpy.data.objects['Cube']
texture_object(cube)

# Use center of mass to center object
model_object.select = True
bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
model_object.location = (0, 0, 0)

# --------------
# Create camera
# --------------
camera_data = bpy.data.cameras.new('Render Camera')
bpy.data.objects.new('Render Camera', object_data=camera_data)
camera_object = bpy.data.objects['Render Camera']
new_scene.objects.link(camera_object)
camera_object.location = (8, 8, 1)

# Add reflectors
bpy.ops.mesh.primitive_plane_add(location=(0,8 + REFLECTOR_LOCATION_PADDING, 0))
bpy.ops.mesh.primitive_plane_add(location=(8 + REFLECTOR_LOCATION_PADDING,0,0))
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 8))

plane1 = bpy.data.objects['Plane']
plane2 = bpy.data.objects['Plane.001']
plane3 = bpy.data.objects['Plane.002']

# Adjust camera
context.scene.camera = camera_object
look_at(camera_object, model_object)
make_object_gold(model_object)

plane1.rotation_euler.x += math.radians(90)
plane2.rotation_euler.x += math.radians(90)
plane2.rotation_euler.z += math.radians(90)

for plane in [plane1, plane2, plane3]:
    make_object_reflector(plane)

# Make floor
bpy.ops.mesh.primitive_plane_add(calc_uvs=True, location=(0,0,-2))
floor = bpy.data.objects['Plane.003']
floor.scale = (20,20,20)
texture_object(floor)

# Add more props
for index in range(1, int(PROPS_NUMBER)):
    new_object = duplicate_object(cube)
    props.append(new_object)
    new_object.location = rand_location()
    texture_object(new_object)

# Import guns
for index in range(1, 5):
    new_object = duplicate_object(m4a1)
    props.append(new_object)
    shuffle(new_object)
    texture_object(new_object)

for index in range(1, len(WORDS)):
    new_object = spawn_text()
    props.append(new_object)
    new_object.scale = (0.75, 0.75, 0.75)
    new_object.location = rand_location()
    new_object.rotation_euler = rand_rotation()

for model in bpy.data.objects:
    unwrap_model(model)

# ------
# Shoot
# ------
print('Rendering images with resolution: ' + str(context.scene.render.resolution_x) + ' x ' + str(context.scene.render.resolution_y))
for index in range(0, int(shots_number)):
    print("-------------------------- " + str(index) + " --------------------------")
    rotate(model_object, index)
    for prop in props:
        prop.rotation_euler = rand_rotation()
    shoot(camera_object, model_object, output_name(index, model_path))

print('FINISHED ¯\_(ツ)_/¯')
