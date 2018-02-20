def pry():
    code.interact(local=dict(globals(), **locals()))
    sys.exit("Aborting execution")

def fetch_material(material_name):
    assert material_name in MATERIALS_NAMES
    new_material = bpy.data.materials[material_name].copy()
    return new_material

def apply_displacement(obj, strength = 0.2, subdivisions = 2):
    subdivide(obj, subdivisions)
    subsurf = obj.modifiers.new(name='subsurf', type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    displace = obj.modifiers.new(name='displace', type='DISPLACE')
    new_texture = bpy.data.textures.new(name='texture', type='IMAGE')
    new_texture.image = random_height_map(low = True)
    displace.texture = new_texture
    displace.strength = strength

def look_at(obj):
    location_camera = CAMERA.matrix_world.to_translation()
    location_object = obj.matrix_world.to_translation()
    direction = location_object - location_camera
    rot_quat = direction.to_track_quat('-Z', 'Y')
    CAMERA.rotation_euler = rot_quat.to_euler()

def shoot(filepath):
    print('Camera now at location: ' + camera_location_string(CAMERA) + ' / rotation: ' + camera_rotation_string(CAMERA))
    SCENE.render.filepath = filepath
    if animate:
        bpy.ops.render.render(animation=animate, write_still=True)
    else:
        RENDER_OUTPUT_PATHS.append(filepath)
        bpy.ops.render.render(write_still=True)

def output_name(model_path, index = 0):
    return './renders/' + os.path.splitext(model_path)[0].split('/')[-1] + '_' + str(index) + '_' + str(datetime.date.today()) + '_' + str(mode) + ('.avi' if animate else '.png')

def rotate(model_object, index):
    model_object.rotation_euler.z = math.radians(index * (360.0 / shots_number))

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

def rand_scale_vector(scale = round(random.uniform(0, 0.2), 2)):
    return(scale, scale, scale)

def unwrap_model(obj):
    if obj.name.startswith('Camera') or obj.name.startswith('Text') or obj.name.startswith('Cube'):
        return False
    SCENE.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.unwrap()
    bpy.ops.object.mode_set(mode='OBJECT')

def camera_rotation_string(camera):
    return str(int(camera.rotation_euler.x)) + ' ' + str(int(camera.rotation_euler.y)) + ' ' + str(int(camera.rotation_euler.z))

def camera_location_string(camera):
    return str(int(camera.location.x)) + ' ' + str(int(camera.location.y)) + ' ' + str(int(camera.location.z))

#############
# <materials>
#############

def assign_material(obj, material):
    flush_materials(obj.data.materials)
    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material
    return material

# Returns a new Cycles material with default DiffuseBsdf node linked to output
def create_cycles_material(name = 'Object Material - ', clean=False):
    material = bpy.data.materials.new(name + str(uuid.uuid1()))
    material.use_nodes = True
    if clean:
        flush_nodes(material)
    return material

def random_texture():
    texture_path = TEXTURE_FOLDER_PATH + random.choice(os.listdir(TEXTURE_FOLDER_PATH))
    print("LOADING TEXTURE -> " + texture_path)
    return bpy.data.images.load(texture_path)

def random_height_map(low = False):
    if low:
        path = HEIGHT_MAP_FOLDER_PATH + 'low.png'
    else:
        path = HEIGHT_MAP_FOLDER_PATH + random.choice(os.listdir(HEIGHT_MAP_FOLDER_PATH))
    print("LOADING HEIGHT MAP -> " + path)
    return bpy.data.images.load(path)

def random_material(blacklist=[]):
    return fetch_material(random.choice(MATERIALS_NAMES))

def assign_texture_to_material(material, texture):
    assert material.use_nodes == True
    texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
    node = material.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    material.node_tree.links.new(texture_node.outputs['Color'], node.inputs['Color'])
    texture_node.image = texture
    assign_node_to_output(material, node)

def assign_node_to_output(material, new_node):
    assert material.use_nodes == True
    output_node = material.node_tree.nodes['Material Output']
    material.node_tree.links.new(new_node.outputs[0], output_node.inputs['Surface'])

def make_object_reflector(obj):
    obj.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
    make_object_emitter(obj, REFLECTOR_STRENGTH)

def make_object_emitter(obj, emission_strength = 1):
    emissive_material = assign_material(obj, fetch_material('emission'))
    emission_node = emissive_material.node_tree.nodes['Emission']
    emission_node.inputs[0].default_value = rand_color()
    emission_node.inputs[1].default_value = emission_strength
    return emission_node

def make_object_gradient_fabulous(obj, color1, color2):
    material = assign_material(obj, fetch_material('gradient_fabulous'))
    mixer_node = material.node_tree.nodes['Mix']
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

#############
# </material>
#############

def spawn_text(text = None):
    identifier = str(uuid.uuid1())
    new_curve = bpy.data.curves.new(type="FONT",name="text_curve_" + identifier)
    new_curve.extrude = 0.11
    content = text if text else random_text()
    new_text = bpy.data.objects.new("text_" + content, new_curve)
    new_text.data.body = content
    SCENE.objects.link(new_text)
    return new_text

def wireframize(obj, emission_strength = 1, thickness = random.uniform(0.0004, 0.001)):
    SCENE.objects.active = obj
    obj.modifiers.new(name = 'wireframe', type='WIREFRAME')
    obj.modifiers['wireframe'].thickness = thickness
    make_object_emitter(obj, emission_strength)
    return obj

def shuffle(obj):
    obj.location = rand_location()
    obj.scale = rand_scale_vector()
    obj.rotation_euler = rand_rotation()

def randomize_reflectors_colors():
    for r in bpy.data.groups['reflectors'].objects:
        r.data.materials[-1].node_tree.nodes['Emission'].inputs[0].default_value = rand_color()

def add_object(obj, x, y, z, radius):
    infer_primitive(obj, location=(x, y, z), radius=radius)
    WIREFRAMES.append(last_added_object(obj))
    group_add(obj, last_added_object(obj))
    return last_added_object(obj)

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

# Ugly af but no other way to retrieve the last added object by bpy.ops
def last_added_object(object_name_start):
    l = []
    for obj in bpy.data.objects:
        if obj.name.startswith(object_name_start.lower().title()):
            l.append(obj)
    return l[-1]

def last_object_group(group_name):
    return bpy.data.groups[group_name.lower().title()].objects[-1]

def build_composite_object(obj, size, radius):
    res = []
    res.append(build_grid_object(obj, size, -size, radius))
    for z in range(0, size):
        res.append(build_grid_object(obj, size, last_object_group(obj).location.z + 2 * radius, radius))
    return res

def build_grid_object(obj, size, z_index, radius):
    res = []
    res.append(build_object_line(obj, size, z_index, -size, radius))
    for y in range(0, size):
        res.append(build_object_line(obj, size, z_index, last_object_group(obj).location.y + 2 * radius, radius))
    return res

def build_object_line(obj, size, z_index, y_index, radius):
    res = []
    res.append(add_object(obj, -size, y_index, z_index, radius))
    for x in range(0, size):
        new_obj = duplicate_object(last_object_group(obj))
        group_add(obj, new_obj)
        res.append(new_obj)
        new_obj.location = ((last_object_group(obj).location.x + 2 * radius), y_index, z_index)
    return res

# Replace vertex coordinate everywhere
def find_and_replace(vector, target, replacement):
    return mathutils.Vector((float(str(vector.x).replace(target, replacement)), float(str(vector.y).replace(target, replacement)), float(str(vector.z).replace(target, replacement))))

def glitch(object):
    bpy.ops.object.mode_set(mode='OBJECT')
    assert object.type == 'MESH'
    ints = list(range(10))
    target = str(ints.pop(int(random.uniform(0, len(ints) - 1))))
    replacement = str(ints.pop(int(random.uniform(0, len(ints)))))
    for vertex in object.data.vertices:
        vertex.co = find_and_replace(vertex.co, target, replacement)

def displace(obj, max_amplitude = 0.06):
    bpy.ops.object.mode_set(mode='OBJECT')
    assert obj.type == 'MESH'
    for vertex in obj.data.vertices:
        vertex.co = mathutils.Vector((vertex.co.x + random.uniform(-max_amplitude, max_amplitude), vertex.co.y + random.uniform(-max_amplitude, max_amplitude), vertex.co.z + random.uniform(-max_amplitude, max_amplitude)))

def subdivide(object, cuts):
    if SCENE.objects.active != object:
        SCENE.objects.active = object
    assert SCENE.objects.active == object
    bpy.ops.object.mode_set(mode='EDIT')
    for index in range(0, cuts):
        bpy.ops.mesh.subdivide(cuts)
    bpy.ops.object.editmode_toggle()

def add_ocean(spatial_size, resolution, depth = 100, scale=(4,4,4), wave_scale = 0.5):
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.4),radius=1)
    ocean = last_added_object('CUBE')
    ocean.scale = scale
    ocean.modifiers.new(name='Ocean', type='OCEAN')
    ocean.modifiers["Ocean"].spatial_size = spatial_size
    ocean.modifiers["Ocean"].resolution = resolution
    ocean.modifiers["Ocean"].wave_scale = wave_scale
    ocean.modifiers["Ocean"].depth = depth
    assign_material(ocean, fetch_material("jello"))
    shadow = duplicate_object(ocean)
    shadow.location += mathutils.Vector((1,1,-0.4))
    wireframize(shadow)
    shadow.name = 'shadow'
    ocean.name = 'ocean'
    return [ocean, shadow]

# Delete current objects
def flush_objects(objs = bpy.data.objects):
    for obj in objs:
        bpy.data.objects.remove(obj, do_unlink=True)

# Delete materials
def flush_materials(mats = bpy.data.materials):
    for mat in mats:
        if mat != None:
            bpy.data.materials.remove(mat, do_unlink=True)

def flush_nodes(material):
    for node in material.node_tree.nodes:
        material.node_tree.nodes.remove(node)

def delete_useless_materials():
    for mat in bpy.data.materials:
        if mat.name.startswith('Material'):
            bpy.data.materials.remove(mat, do_unlink=True)

# Rotate hue to generate a somewhat harmonious palette
def adjacent_colors(r, g, b, number):
    angle = (360 / number) / 360 # angles are in ?
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue_positions = []
    for i in range(number):
        hue_positions.append(angle * i)
    h = [(h + offset) % 1 for offset in hue_positions]
    return [colorsys.hls_to_rgb(hi, l, s) for hi in h]

# Use saturation increments to generate a color ramp palette
def color_ramp(r, g, b, number):
    saturation_increment = 100 / number
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    saturations = []
    for i in range(number):
        saturations.append(i * saturation_increment)
    s = [(s + offset) % 1 for offset in saturations]
    return [colorsys.hls_to_rgb(h, l, sat) for sat in s]

def rand_color_palette(number):
    function = random.choice([color_ramp, adjacent_colors])
    res = list(map(lambda x: list(x), function(rand_color_value(), rand_color_value(), rand_color_value(), number)))
    # add alpha component
    for i in res:
        i.append(1)
    print("palette: " + str(res))
    return res

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
    return create_mesh('pyramid_' + str(uuid.uuid1()), verts, faces, location)

def cut(obj, slices, thiccness = 3):
    center(obj)
    print("Slicing " + obj.name + " in " + str(slices) + "parts")
    for i in range(0,slices):
        dup = duplicate_object(obj)
        bpy.ops.object.select_all(action='DESELECT')
        SCENE.objects.active = dup
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(0,0,0),plane_no=(0,0,1),clear_outer=False,clear_inner=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(0,0,thiccness*(1+i)),plane_no=(0,0,1),clear_outer=True,clear_inner=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        dup.location.z += thiccness

def duplicate_object(obj):
    print("Cloning -> " + obj.name)
    new_object = obj.copy()
    new_object.data = obj.data.copy()
    new_object.animation_data_clear()
    SCENE.objects.link(new_object)
    return new_object

def random_text():
    lines = open(FIXTURES_FOLDER_PATH + 'text/strings.txt').readlines()
    return lines[random.randrange(len(lines))]

def create_mesh(name, verts, faces, location, edges=[]):
    mesh_data = bpy.data.meshes.new("mesh_data")
    faces = faces if faces else random_faces(verts)
    mesh_data.from_pydata(verts, edges, faces)
    mesh_data.update()
    obj = bpy.data.objects.new(name, mesh_data)
    obj.location = location
    SCENE.objects.link(obj)
    SCENE.objects.active = obj
    center(obj)
    return obj

def add_faces(obj):
    vertices = []
    for v in obj.data.vertices:
        vertices.append(v.co)
    new_obj = create_mesh(obj.name, vertices, random_faces(vertices), obj.location)
    bpy.data.objects.remove(obj, do_unlink=True)
    return new_obj

def random_faces(vertices):
    faces = []
    for i in range(int(len(vertices)/100)):
        target = vertices[random.choice((range(len(vertices))))]
        if (random.randint(0, 1) == 1):
            faces.append(((target + 2), int(target / 6), int(target - 1), target))
        else:
            faces.append((int(target / 6), int(target - 1), target))
    return faces

############
# <geometry>
############

def center(obj):
    SCENE.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
    local_bounding_box_center = 0.125 * sum((mathutils.Vector(b) for b in obj.bound_box), mathutils.Vector())
    obj.location -= local_bounding_box_center
    return obj

def create_line(name, point_list, thickness = 0.002, location = ORIGIN):
    line_data = bpy.data.curves.new(name=name,type='CURVE')
    line_data.dimensions = '3D'
    line_data.fill_mode = 'FULL'
    line_data.bevel_depth = thickness
    polyline = line_data.splines.new('POLY')
    polyline.points.add(len(point_list)-1)
    for idx in range(len(point_list)):
        polyline.points[idx].co = (point_list[idx])+(1.0,)
    line = bpy.data.objects.new('line_' + str(uuid.uuid1()), line_data)
    SCENE.objects.link(line)
    line.location = location
    make_object_emitter(line, 0.8)
    return line

def series(length, function, pitch):
    return list(map(lambda x: (0, x, function(x)), pitched_array(0.0, length, pitch)))

def parametric_curve(fx, fy, fz, length):
    fx = lambda x: math.cos(x)
    fy = lambda y: math.sin(y) + 15
    fz = lambda z: math.tan(z)
    name = 'curve_' + str(uuid.uuid1())
    vertices = []
    for t in pitched_array(-length, length, 1):
        vertices.append((fx(t), fy(t), fz(t)))
    return build_segment(ORIGIN, None, None, None, vertices, name)

def build_segment(location, function, length = 2, pitch = 0.5, verts = None, name = None):
    verts = verts if verts else series(length, function, pitch)
    edges = []
    for v in range(0, (len(verts) - 1)):
        edges.append([v, v+1])
    name = name if name else 'segment_' + str(uuid.uuid1())
    return create_mesh(name, verts, [], location, edges)

def camera_path():
    res = []
    radius = 5
    fx = lambda x: radius * math.cos(x)
    fy = lambda y: radius * math.sin(y)
    fz = lambda z: INITIAL_CAMERA_LOCATION[2]
    factor = (2 * math.pi / NUMBER_OF_FRAMES)
    return list(map( lambda t: (fx(t * factor), fy(t * factor), fz(t * factor)), range(0, NUMBER_OF_FRAMES)))

def pitched_array(minimum, maximum, pitch):
    return list(map(lambda x: (minimum + pitch * x), range(int((maximum - minimum) / pitch))))

#############
# </geometry>
#############

def animation_routine(frame):
    CAMERA.location = CAMERA_PATH[frame] if not FIXED_CAMERA else CAMERA
    look_at(random.choice(bpy.data.objects))
    assign_material(SUBJECT, random_material())
    randomize_reflectors_colors()
    SUBJECT.rotation_euler.z += math.radians(1)
    for ocean in OCEAN:
        ocean.modifiers['Ocean'].choppiness += random.uniform(0, 0.001)
        ocean.modifiers['Ocean'].time += 0.5
        assign_material(ocean, random_material())
    for particle_system in bpy.data.particles:
        particle_system.phase_factor_random += 0.01
    for prop in props:
        prop.location += mathutils.Vector((random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)))
        prop.rotation_euler.x += math.radians(5)
    for obj in WIREFRAMES:
        obj.rotation_euler.rotate(mathutils.Euler((math.radians(1), math.radians(1), math.radians(1)), 'XYZ'))
    for display in bpy.data.groups['displays'].objects:
        display.rotation_euler.x += math.radians(2)
        display.location += mathutils.Vector((random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)))

def add_frame(collection = bpy.data.objects, blacklist = set(BAKED)):
    for obj in set(collection) - blacklist:
        obj.keyframe_insert(data_path="rotation_euler", index=-1)
        obj.keyframe_insert(data_path="location", index=-1)
        obj.keyframe_insert(data_path="scale", index=-1)