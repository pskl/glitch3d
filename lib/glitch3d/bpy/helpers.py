# DISCLAIMER: all of this could be done in a much more intelligent way (with more Python knowledge)
# This is just what works for now for the needs of my current project

REFLECTOR_SCALE = random.uniform(5, 8)
REFLECTOR_STRENGTH = random.uniform(10, 15)
REFLECTOR_LOCATION_PADDING = random.uniform(10, 12)
WIREFRAME_THICKNESS = random.uniform(0.006, 0.02)
DISPLACEMENT_AMPLITUDE = random.uniform(0.02, 0.1)
REPLACE_TARGET = str(random.uniform(0, 9))
REPLACEMENT = str(random.uniform(0, 9))
ORIGIN  = (0,0,2)
NUMBER_OF_FRAMES = 400
SCATTER_INTENSITY = 0.015
ABSORPTION_INTENSITY = 0.25
DISPLAY_SCALE = (2, 2, 2)
PRIMITIVES = ['PYRAMID', 'CUBE']
props = []
YELLOW = (1, 0.7, 0.1, 1)
GREY = (0.2, 0.2, 0.2 ,1)
BLUE = (0.1, 0.1, 0.8, 1)
PINK = (0.8, 0.2, 0.7, 1.0)
WORDS = string.ascii_lowercase
WIREFRAMES = []
VORONOIED = []

def debug():
    code.interact(local=dict(globals(), **locals()))
    sys.exit("Aborting execution")

# Helper methods
def look_at(object):
    location_camera = CAMERA.matrix_world.to_translation()
    location_object = object.matrix_world.to_translation()
    direction = location_object - location_camera
    rot_quat = direction.to_track_quat('-Z', 'Y')
    CAMERA.rotation_euler = rot_quat.to_euler()

def empty_materials():
    for material in bpy.data.materials.keys():
        bpy.data.materials.remove(object.data.materials[material])

def shoot(model_object, filepath):
    directory = os.path.dirname('./renders')
    if not os.path.exists(directory):
      os.makedirs(directory)
    look_at(model_object)
    print('Camera now at location: ' + camera_location_string(CAMERA) + ' / rotation: ' + camera_rotation_string(CAMERA))
    bpy.context.scene.render.filepath = filepath
    if animate:
        return bpy.ops.render.render(animation=animate)
    bpy.ops.render.render(write_still=True)

def output_name(index, model_path):
    if animate == True:
        return './renders/' + os.path.splitext(model_path)[0].split('/')[-1] + '_' + str(index) + '_' + str(datetime.date.today()) + '_' + str(mode) + '.avi'
    else:
        return './renders/' + os.path.splitext(model_path)[0].split('/')[-1] + '_' + str(index) + '_' + str(datetime.date.today()) + '_' + str(mode) + '.png'

def rotate(model_object, index):
    model_object.rotation_euler[2] = math.radians(index * (360.0 / shots_number))

# RGB 0 -> 1
def rand_color_value():
    return random.uniform(0, 255) / 255

def rand_location():
    return (rand_location_value(), rand_location_value(), rand_location_value())

def rand_rotation():
    return (rand_rotation_value(), rand_rotation_value(), rand_rotation_value())

def rand_rotation_value():
    return round(math.radians(random.uniform(0, 60), 10))

def rand_rotation():
    return (random.uniform(0, 20), random.uniform(0, 20), random.uniform(0, 20))

def rand_location_value():
    return round(random.uniform(-4, 4), 10)

def rand_color():
    return random.choice(COLORS)

def rand_scale():
    return round(random.uniform(0, 0.2), 10)

def rand_scale_vector():
    scale = rand_scale()
    return(scale, scale, scale)

def unwrap_model(obj):
    if obj.name.startswith('Camera') or obj.name.startswith('Text') or obj.name.startswith('Cube'):
        return False
    context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.unwrap()
    bpy.ops.object.mode_set(mode='OBJECT')

def camera_rotation_string(camera):
    return str(int(camera.rotation_euler.x)) + ' ' + str(int(camera.rotation_euler.y)) + ' ' + str(int(camera.rotation_euler.z))

def camera_location_string(camera):
    return str(int(camera.location.x)) + ' ' + str(int(camera.location.y)) + ' ' + str(int(camera.location.z))

def assign_material(model_object, material):
    model_object.data.materials.append(material)

# Returns a new Cycles material with default DiffuseBsdf node linked to output
def create_cycles_material():
    material = bpy.data.materials.new('Object Material - ' + str(uuid.uuid1()))
    material.use_nodes = True
    return material

def random_texture():
    texture_path = TEXTURE_FOLDER_PATH + random.choice(os.listdir(TEXTURE_FOLDER_PATH))
    logging.info('---------')
    logging.info(TEXTURE_FOLDER_PATH)
    logging.info('---------')
    return bpy.data.images.load(texture_path)

def assign_texture_to_material(material, texture):
    assert material.use_nodes == True
    texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
    emission_node = material.node_tree.nodes.new('ShaderNodeEmission')
    material.node_tree.links.new(texture_node.outputs['Color'], emission_node.inputs['Color'])
    texture_node.image = texture
    assign_node_to_output(material, emission_node)

def assign_node_to_output(material, new_node):
    assert material.use_nodes == True
    output_node = material.node_tree.nodes['Material Output']
    material.node_tree.links.new(new_node.outputs[0], output_node.inputs['Surface'])

def mix_nodes(material, node1, node2):
    mix = material.node_tree.nodes.new('ShaderNodeMixShader')
    material.node_tree.links.new(mix.inputs[1], node1.outputs[0])
    material.node_tree.links.new(mix.inputs[2], node2.outputs[0])
    assign_node_to_output(material, mix)

def make_object_glossy(obj, color = (PINK), roughness = 0.2):
    material = bpy.data.materials.new('Glossy Material - ' + str(uuid.uuid1()))
    material.use_nodes = True
    glossy_node = material.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    glossy_node.inputs[0].default_value = color
    glossy_node.inputs[1].default_value = roughness
    assign_node_to_output(material, glossy_node)
    assign_material(obj, material)

def make_object_reflector(obj):
    obj.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
    make_object_emitter(obj, REFLECTOR_STRENGTH)

def make_texture_object_transparent(obj, color = (1,1,1,0.5), intensity = 0.25):
    material = obj.data.materials[-1]
    emission_node = material.node_tree.nodes['Emission']
    trans = material.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    add = material.node_tree.nodes.new('ShaderNodeMixShader')
    material.node_tree.links.new(emission_node.outputs[0], add.inputs[0])
    material.node_tree.links.new(trans.outputs[0], add.inputs[1])
    material.node_tree.links.new(emission_node.outputs[0], add.inputs[0])
    add.inputs[0].default_value = intensity
    trans.inputs[0].default_value = color

def make_object_emitter(obj, emission_strength):
    emissive_material = bpy.data.materials.new('Emissive Material #' + str(uuid.uuid1()))
    emissive_material.use_nodes = True
    emission_node = emissive_material.node_tree.nodes.new('ShaderNodeEmission')
    # Set color
    emission_node.inputs[0].default_value = rand_color()
    # Set strength
    emission_node.inputs[1].default_value = emission_strength
    assign_node_to_output(emissive_material, emission_node)
    assign_material(obj, emissive_material)
    return emission_node

def make_object_gradient_fabulous(obj, color1, color2):
    material = bpy.data.materials.new('Fabulous #' + str(uuid.uuid1()))
    material.use_nodes = True
    assign_material(obj, material)
    mixer_node = material.node_tree.nodes.new('ShaderNodeMixRGB')
    gradient_node = material.node_tree.nodes.new('ShaderNodeTexGradient')
    gradient_node.gradient_type = 'SPHERICAL'
    bsdf_node = material.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    material.node_tree.links.new(gradient_node.outputs['Fac'], mixer_node.inputs['Fac'])
    material.node_tree.links.new(mixer_node.outputs[0], bsdf_node.inputs['Color'])
    assign_node_to_output(material, bsdf_node)
    mixer_node.inputs['Color1'].default_value = color1
    mixer_node.inputs['Color2'].default_value = color2

def voronoize(obj, scale = 5.0):
    material = obj.data.materials[-1]
    texture_node = material.node_tree.nodes.new('ShaderNodeTexVoronoi')
    material.node_tree.links.new(texture_node.outputs['Color'], material.node_tree.nodes['Glossy BSDF'].inputs['Color'])
    texture_node.coloring = 'CELLS'
    texture_node.inputs[1].default_value = scale
    VORONOIED.append(obj)

def texture_object(obj):
    new_material = create_cycles_material()
    assign_texture_to_material(new_material, random_texture())
    assign_material(obj, new_material)

def duplicate_object(obj):
    new_object = obj.copy()
    new_object.data = obj.data.copy()
    context.scene.objects.link(new_object)
    return new_object

def random_text():
    global WORDS
    chosen_word = random.choice(WORDS)
    return chosen_word

def create_mesh(name, verts, faces, location):
    mesh_data = bpy.data.meshes.new("cube_mesh_data")
    mesh_data.from_pydata(verts, [], faces)
    mesh_data.update()
    obj = bpy.data.objects.new(name, mesh_data)
    obj.location = location
    context.scene.objects.link(obj)
    return obj

def spawn_text():
    identifier = str(uuid.uuid1())
    new_curve = bpy.data.curves.new(type="FONT",name="Curve - " + identifier)
    new_curve.extrude = 0.12
    new_text = bpy.data.objects.new("Text - " + identifier, new_curve)
    new_text.data.body = random_text()
    context.scene.objects.link(new_text)
    return new_text

def wireframize(obj):
    context.scene.objects.active = obj
    bpy.ops.object.modifier_add(type='WIREFRAME')
    obj.modifiers['Wireframe'].thickness = WIREFRAME_THICKNESS
    make_object_emitter(obj, 2)

def shuffle(obj):
    obj.location = rand_location()
    obj.scale = rand_scale_vector()
    obj.rotation_euler = rand_rotation()

def series(length):
    return list(map(lambda x: (0, x, math.cos(x)), numpy.arange(0.0, length, 0.1)))

def randomize_reflectors_colors():
    for r in bpy.data.groups['Plane'].objects:
        r.data.materials[-1].node_tree.nodes['Emission'].inputs[0].default_value = rand_color()

def add_object(obj, x, y, z, radius):
    infer_primitive(obj, location=(x, y, z), radius=radius)
    WIREFRAMES.append(last_added_object(obj))
    group_add(obj, last_added_object(obj))

def infer_primitive(obj, **kwargs):
    if obj == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(radius = kwargs['radius'], location = kwargs['location'])
    elif obj == 'ICO':
        bpy.ops.mesh.primitive_ico_sphere_add(location = kwargs['location'])
    elif obj == 'CONE':
        bpy.ops.mesh.primitive_cone_add(location = kwargs['location'], radius1 = kwargs['radius'])
    elif obj == 'PYRAMID':
        build_pyramid(location = kwargs['location'])
    elif obj == 'PLANE':
        bpy.ops.mesh.primitive_plane_add(location = kwargs['location'], radius = kwargs['radius'])

def group_add(group_name, obj):
    bpy.data.groups[group_name.lower().title()].objects.link(obj)

def last_added_object(object_name_start):
    l = []
    for obj in bpy.data.objects:
        if obj.name.startswith(object_name_start.lower().title()):
            l.append(obj)
    return l[-1]

def last_object_group(group_name):
    return bpy.data.groups[group_name.lower().title()].objects[-1]

def build_composite_object(obj, size, radius):
    build_grid_object(obj, size, -size, radius)
    for z in range(0, size):
        build_grid_object(obj, size, last_object_group(obj).location.z + 2 * radius, radius)

def build_grid_object(obj, size, z_index, radius):
    build_object_line(obj, size, z_index, -size, radius)
    for y in range(0, size):
        build_object_line(obj, size, z_index, last_object_group(obj).location.y + 2 * radius, radius)

def build_object_line(obj, size, z_index, y_index, radius):
    add_object(obj, -size, y_index, z_index, radius)
    for x in range(0, size):
        new_obj = duplicate_object(last_object_group(obj))
        WIREFRAMES.append(new_obj)
        group_add(obj, new_obj)
        new_obj.location = ((last_object_group(obj).location.x + 2 * radius), y_index, z_index)

# Displace vertex by random offset
def displace_vector(vector):
    return mathutils.Vector((vector.x + random.uniform(-DISPLACEMENT_AMPLITUDE, DISPLACEMENT_AMPLITUDE), vector.y + random.uniform(-DISPLACEMENT_AMPLITUDE, DISPLACEMENT_AMPLITUDE), vector.z + random.uniform(-DISPLACEMENT_AMPLITUDE, DISPLACEMENT_AMPLITUDE)))

# Replace vertex coordinate everywhere
def find_and_replace(vector, target = random.uniform(0,9), replacement = random.uniform(0,9)):
    return mathutils.Vector((float(str(vector.x).replace(target, replacement)), float(str(vector.y).replace(target, replacement)), float(str(vector.z).replace(target, replacement))))

def glitch(object):
    bpy.ops.object.mode_set(mode='OBJECT')
    assert object.type == 'MESH'
    for vertex in object.data.vertices:
        vertex.co = find_and_replace(vertex.co)

def displace(object):
    bpy.ops.object.mode_set(mode='OBJECT')
    assert object.type == 'MESH'
    for vertex in object.data.vertices:
        vertex.co = displace_vector(vertex.co)

def subdivide(object, cuts):
    if context.scene.objects.active != object:
        context.scene.objects.active = object
    assert context.scene.objects.active == object
    bpy.ops.object.mode_set(mode='EDIT')
    for index in range(0, cuts):
        bpy.ops.mesh.subdivide(cuts)

def clone(obj):
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    new_obj.animation_data_clear()
    context.scene.objects.link(new_obj)
    return new_obj

def add_ocean(spatial_size, resolution):
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, -1),radius=1)
    ocean = last_added_object('CUBE')
    context.scene.objects.active = ocean
    ocean.scale = (2,2,2)
    bpy.ops.object.modifier_add(type='OCEAN')
    ocean.modifiers["Ocean"].spatial_size = spatial_size
    ocean.modifiers["Ocean"].resolution = resolution
    make_object_glossy(ocean, rand_color())
    make_object_gradient_fabulous(ocean, rand_color(), rand_color())
    mix_nodes(ocean.data.materials[0], ocean.data.materials[0].node_tree.nodes['Diffuse BSDF'], ocean.data.materials[0].node_tree.nodes['Glossy BSDF'])
    shadow = clone(ocean)
    shadow.location.x += 3
    wireframize(shadow)
    shadow.name = 'ocean'
    ocean.name = 'ocean'
    return [ocean, shadow]

# Delete current objects
def flush_all_objects():
    for index, obj in enumerate(bpy.data.objects):
        bpy.data.objects.remove(obj)

# Rotate hue to generate palette
def adjacent_colors(r, g, b, number):
    angle = (360 / 5) / 360
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue_positions = []
    for i in range(number):
        hue_positions.append(angle * i)
    h = [(h + offset) % 1 for offset in hue_positions]
    adjacent = [colorsys.hls_to_rgb(hi, l, s) for hi in h]
    # add alpha component
    res = list(map(lambda x: list(x), adjacent))
    for i in res:
        i.append(1)
    return res

def rand_color_palette(number):
    return adjacent_colors(rand_color_value(), rand_color_value(), rand_color_value(), number)

def build_pyramid(width=random.uniform(1,3), length=random.uniform(1,3), height=random.uniform(1,3), location=ORIGIN):
    verts=[]
    faces=[]
    verts.append([-(width/2),(length/2),0.0])
    verts.append([-(width/2),-(length/2),0.0])
    verts.append([(width/2),-(length/2),0.0])
    verts.append([(width/2),(length/2),0.0])
    verts.append([0.0,0.0,(height/2)])
    faces.append([0,1,2,3])
    faces.append([0,1,4])
    faces.append([1,2,4])
    faces.append([2,3,4])
    faces.append([3,0,4])
    return create_mesh('Pyramid ' + str(uuid.uuid1()), verts, faces, location)

def move_ocean(ocean):
    ocean.modifiers['Ocean'].time += 1.5
    ocean.modifiers['Ocean'].random_seed = round(random.uniform(0, 100))
    ocean.modifers['Ocean'].choppiness += 0.3

def camera_path(pitch):
    res = []
    initial_z = INITIAL_CAMERA_LOCATION[2]
    initial_x = INITIAL_CAMERA_LOCATION[0]
    for y in numpy.arange(initial_x, -initial_x, pitch):
        res.append((initial_x, y, initial_z))
    for x in numpy.arange(initial_x, -initial_x, pitch):
        res.append((x,-initial_x, initial_z))
    for y in numpy.arange(-initial_x, initial_x, pitch):
        res.append((-initial_x, y, initial_z))
    for x in numpy.arange(-initial_x, initial_x, pitch):
        res.append((x, initial_x, initial_z))
    return res

def still_routine():
    CAMERA.location.x = INITIAL_CAMERA_LOCATION[0] + round(random.uniform(-2, 2), 10)
    CAMERA.location.y = INITIAL_CAMERA_LOCATION[1] + round(random.uniform(-2, 2), 10)
    randomize_reflectors_colors()
    map(move_ocean, OCEAN)
    map(make_object_glossy, OCEAN)
    rotate(model_object, index)
    for l in bpy.data.groups['Lines'].objects:
        rotation = rand_rotation()
        l.rotation_euler = rotation
    for prop in props:
        prop.location = rand_location()
        prop.rotation_euler = rand_rotation()
    for obj in WIREFRAMES:
        obj.location = rand_location()
        obj.rotation_euler = rand_rotation()
    for display in bpy.data.groups['Displays'].objects:
        display.location = rand_location()
        rotate(display, index)

def animation_routine(frame):
    assert len(camera_path) >= NUMBER_OF_FRAMES
    CAMERA.location = camera_path[frame]
    randomize_reflectors_colors()
    map(move_ocean, OCEAN)
    map(make_object_glossy, OCEAN)
    glitch(model_object)
    model_object.rotation_euler.z += math.radians(4)
    for l in bpy.data.groups['Lines'].objects:
        l.rotation_euler.x += math.radians(5)
        l.rotation_euler.z += math.radians(5)
    for prop in props:
        prop.rotation_euler.x += math.radians(5)
    for obj in WIREFRAMES:
        obj.location.z += 0.1
        obj.rotation_euler.z += math.radians(5)
    for display in bpy.data.groups['Displays'].objects:
        display.rotation_euler.x += math.radians(3)

def create_line(name, point_list, thickness = 0.002, location = (0, -10, 0)):
    # setup basic line data
    line_data = bpy.data.curves.new(name=name,type='CURVE')
    line_data.dimensions = '3D'
    line_data.fill_mode = 'FULL'
    line_data.bevel_depth = thickness
    # define points that make the line
    polyline = line_data.splines.new('POLY')
    polyline.points.add(len(point_list)-1)
    for idx in range(len(point_list)):
        polyline.points[idx].co = (point_list[idx])+(1.0,)
    # create an object that uses the linedata
    line = bpy.data.objects.new('line' + str(uuid.uuid1()), line_data)
    bpy.context.scene.objects.link(line)
    line.location = location
    make_object_emitter(line, 0.8)
    return line

def add_spotlight(location, intensity, radians):
    bpy.ops.object.lamp_add(type='SPOT', radius=1.0, view_align=False, location=location)
    spot = last_added_object('Spot')
    spot.data.node_tree.nodes['Emission'].inputs[1].default_value = intensity
    spot.data.spot_size = radians
    return spot

def make_world_volumetric(world, scatter_intensity = SCATTER_INTENSITY, absorption_intensity = ABSORPTION_INTENSITY):
    assert world.use_nodes == True
    output = world.node_tree.nodes['World Output']
    bg_node = world.node_tree.nodes.new('ShaderNodeBackground')
    absorption_node = world.node_tree.nodes.new('ShaderNodeVolumeAbsorption')
    scatter_node = world.node_tree.nodes.new('ShaderNodeVolumeScatter')
    add_shader = world.node_tree.nodes.new('ShaderNodeAddShader')
    world.node_tree.links.new(add_shader.outputs[0], output.inputs['Volume'])
    world.node_tree.links.new(bg_node.outputs['Background'], output.inputs['Surface'])
    world.node_tree.links.new(scatter_node.outputs[0], add_shader.inputs[0])
    world.node_tree.links.new(absorption_node.outputs[0], add_shader.inputs[1])
    scatter_node.inputs['Density'].default_value = SCATTER_INTENSITY
    absorption_node.inputs['Density'].default_value = ABSORPTION_INTENSITY
    bg_node.inputs[0].default_value = rand_color()
