# Load props
bpy.ops.import_scene.obj(filepath = os.path.join(FIXTURES_FOLDER_PATH + 'm4a1.obj'), use_edges=True)
bpy.ops.import_scene.obj(filepath = os.path.join(FIXTURES_FOLDER_PATH + 'lightning.obj'), use_edges=True)
m4a1 = bpy.data.objects['m4a1']
logo = bpy.data.objects["0_glitch3d_lightning"]
logo.name = 'logo'
logo.location = rand_location()
m4a1.location = rand_location()
m4a1.scale = (0.5, 0.5, 0.5)
props.append(m4a1)
props.append(logo)

# Add props
rand_primitive = random.choice(PRIMITIVES)
# elements = build_composite_object(rand_primitive, 4, 1)

# for l1 in elements:
#     for l2 in l1:
#         for obj in l2:
#             WIREFRAMES.append(obj)

# Set up virtual displays
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(0, 6, 2))
display1 = last_added_object('Grid')
display1.name = 'display_1'
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(6, 0, 2))
display2 = last_added_object('Grid')
display2.name = 'display_2'

bpy.data.groups['displays'].objects.link(display1)
bpy.data.groups['displays'].objects.link(display2)

display1.rotation_euler.x += math.radians(90)
display1.rotation_euler.z -= math.radians(90)
display2.rotation_euler.x += math.radians(90)
display2.rotation_euler.y += math.radians(90)
display2.rotation_euler.z += math.radians(120)

for display in bpy.data.groups['displays'].objects:
    display.rotation_euler.x += math.radians(90)
    display.scale = DISPLAY_SCALE
    # subdivide(display, 1)
    texture_object(display)
    unwrap_model(display)

for prop in props:
    assign_material(prop, random_material())

# Make floor
bpy.ops.mesh.primitive_plane_add(location=(0, 0, -2))
floor = last_added_object('Plane')
floor.name = 'floor'
floor.scale = (20,20,20)
subdivide(floor, int(random.uniform(1, 5)))
displace(floor)

OCEAN = add_ocean(10, 20)

# Create lines as backdrop
LINES = bpy.data.groups['lines']
for j in range(0,10):
    for i in range(0, 10):
        new_line = create_line('line' + str(uuid.uuid1()), series(30, random.choice(FUNCTIONS), 0.3), 0.003, (j, -10, 2))
        bpy.data.groups['lines'].objects.link(new_line)
        new_line.location.z += i / 3
        props.append(new_line)

# branding
spawn_text("PSKL")

# Add flying letters, lmao
for index in range(1, 5):
    new_object = spawn_text()
    bpy.data.groups['texts'].objects.link(new_object)
    props.append(new_object)
    text_scale = random.uniform(0.75, 3)
    make_object_glossy(new_object, rand_color(), 0.0)
    new_object.scale = (text_scale, text_scale, text_scale)
    new_object.location = rand_location()

for obj in WIREFRAMES:
    wireframize(obj)