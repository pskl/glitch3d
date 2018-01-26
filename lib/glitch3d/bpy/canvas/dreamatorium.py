# Load props
bpy.ops.import_scene.obj(filepath = os.path.join(FIXTURES_FOLDER_PATH + 'm4a1.obj'), use_edges=True)
m4a1 = bpy.data.objects['m4a1']
m4a1.location = rand_location()
m4a1.scale = (0.5, 0.5, 0.5)
props.append(m4a1)

# Add props
rand_primitive = random.choice(PRIMITIVES)
elements = build_composite_object(rand_primitive, 4, 1)

for l1 in elements:
    for l2 in l1:
        for obj in l2:
            WIREFRAMES.append(obj)

# Set up virtual displays
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(0, 6, 2))
display1 = last_added_object('Grid')
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, location=(6, 0, 2))
display2 = last_added_object('Grid')

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
    unwrap_model(display)

glitch(m4a1)
make_object_gradient_fabulous(m4a1, rand_color(), rand_color())

# Make floor
bpy.ops.mesh.primitive_plane_add(location=(0, 0, -2))
floor = last_added_object('Plane')
floor.name = 'Floor'
floor.scale = (20,20,20)
subdivide(floor, int(random.uniform(3, 7)))
displace(floor)

OCEAN = add_ocean(10, 20)

# Create lines as backdrop
# LINES = bpy.data.groups['Lines']
# for j in range(0,20):
#     for i in range(0, 20):
#         new_line = create_line('line' + str(uuid.uuid1()), series(30), 0.003, (j, -10, 2))
#         bpy.data.groups['Lines'].objects.link(new_line)
#         new_line.location.z += i / 3

# Add flying letters, lmao
for index in range(1, 5):
    new_object = spawn_text()
    bpy.data.groups['Texts'].objects.link(new_object)
    props.append(new_object)
    text_scale = random.uniform(0.75, 3)
    make_object_glossy(new_object, rand_color(), 0.0)
    new_object.scale = (text_scale, text_scale, text_scale)
    new_object.location = rand_location()

for obj in WIREFRAMES:
    wireframize(obj)