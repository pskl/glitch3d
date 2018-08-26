import sys, code, random, os, math, bpy, numpy, uuid, mathutils, subprocess

def pry(globs=globals(), locs=locals()):
    code.interact(local=dict(globs, **locs))
    sys.exit("Aborting execution")

def chunk_it(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def add_frame(collection, data_paths):
    for obj in collection:
        for path in data_paths:
          obj.keyframe_insert(data_path=path, index=-1)

# Hashmap with proba in values
def rand_proba(hashmap):
    return numpy.random.choice(
        list(hashmap.keys()),
        1,
        p=list(map(lambda x: x/sum(hashmap.values()), hashmap.values()))
    )[0]

def apply_displacement(obj, height_map_folder, strength = 0.2, subdivisions = 2):
    subdivide(obj, subdivisions)
    subsurf = obj.modifiers.new(name='subsurf', type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2
    displace = obj.modifiers.new(name='displace', type='DISPLACE')
    new_texture = bpy.data.textures.new(name='texture', type='IMAGE')
    new_texture.image = random_height_map(height_map_folder, low = True)
    displace.texture = new_texture
    displace.strength = strength

def decimate(obj):
  modifier = obj.modifiers.new(name='decimate', type='DECIMATE')
  modifier.decimate_type = 'DISSOLVE'
  bpy.context.scene.objects.active = obj
  bpy.ops.object.modifier_apply(modifier="decimate")

def look_at(obj):
    location_camera = CAMERA.matrix_world.to_translation()
    location_object = obj.matrix_world.to_translation()
    direction = location_object - location_camera
    rot_quat = direction.to_track_quat('-Z', 'Y')
    CAMERA.rotation_euler = rot_quat.to_euler()

def shoot(filepath):
    print('Camera now at location: ' + str(CAMERA.location) + ' / rotation: ' + str(CAMERA.rotation_euler))
    bpy.context.scene.render.filepath = filepath
    if animate:
        bpy.ops.render.render(animation=animate, write_still=True)
    else:
        RENDER_OUTPUT_PATHS.append(filepath)
        bpy.ops.render.render(write_still=True)

def output_name(model_path, index = 0):
    return './renders/' + os.path.splitext(model_path)[0].split('/')[-1] + '_' + str(index) + '_' + str(datetime.date.today()) + '_' + str(mode) + ('.avi' if animate else '.png')

# RGB 0 -> 1
def rand_color_value():
    return random.uniform(0, 255) / 255

def rand_location(boundary, positive = False):
    if positive:
      return (random.uniform(0, boundary), random.uniform(0, boundary), random.uniform(0, boundary))
    return (random.uniform(-boundary, boundary), random.uniform(-boundary, boundary), random.uniform(-boundary, boundary))

def rand_rotation():
    return (math.radians(random.uniform(0, 360)), math.radians(random.uniform(0, 360)), math.radians(random.uniform(0, 360)))

def unwrap_model(obj):
    if obj.name.startswith('Camera') or obj.name.startswith('Text') or obj.name.startswith('Cube'):
        return False
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.unwrap()
    bpy.ops.object.mode_set(mode='OBJECT')

#############
# <materials>
#############

# create material and load .osl file from fixtures
def load_osl_materials(osl_path):
    for f in os.listdir(osl_path):
      if f.endswith('.osl'):
        material = create_cycles_material('osl_' + f[0:-4] + '_', True)
        script_node = material.node_tree.nodes.new('ShaderNodeScript')
        material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        script_node.mode = 'EXTERNAL'
        script_node.filepath = osl_path + f
        assign_node_to_output(material, script_node)

def fetch_material(material_name):
    new_material = bpy.data.materials[material_name].copy()
    return new_material

def assign_material(obj, material):
    flush_materials(obj.data.materials)
    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material
    return material

def random_material(materials_list):
    return fetch_material(random.choice(materials_list))

# Returns a new Cycles material with default DiffuseBsdf node linked to output
def create_cycles_material(name = 'object_material_', clean=False):
    material = bpy.data.materials.new(name + str(uuid.uuid1()))
    material.use_nodes = True
    if clean:
        flush_nodes(material)
    return material

def random_texture(texture_folder_path):
    texture_path = texture_folder_path + random.choice(os.listdir(texture_folder_path))
    print("LOADING TEXTURE -> " + texture_path)
    return bpy.data.images.load(texture_path)

def random_height_map(height_map_folder, low = False):
    if low:
        path = height_map_folder + 'low.png'
    else:
        path = height_map_folder + random.choice(os.listdir(height_map_folder))
    print("LOADING HEIGHT MAP -> " + path)
    return bpy.data.images.load(path)

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

def make_object_reflector(obj, color, reflector_scale, reflector_strength):
    obj.scale = (reflector_scale, reflector_scale, reflector_scale)
    make_object_emitter(obj, color, reflector_strength)

def make_object_emitter(obj, color, emission_strength = 1):
    emissive_material = assign_material(obj, fetch_material('emission'))
    emission_node = emissive_material.node_tree.nodes['Emission']
    emission_node.inputs[0].default_value = color
    emission_node.inputs[1].default_value = emission_strength
    return emission_node

def make_object_gradient_fabulous(obj, color1, color2):
    material = assign_material(obj, fetch_material('gradient_fabulous'))
    mixer_node = material.node_tree.nodes['Mix']
    mixer_node.inputs['Color1'].default_value = color1
    mixer_node.inputs['Color2'].default_value = color2

def texture_object(obj, texture_folder_path):
    new_material = create_cycles_material()
    assign_texture_to_material(new_material, random_texture(texture_folder_path))
    assign_material(obj, new_material)

#############
# </material>
#############

def spawn_text(text_file_path, text = None):
    identifier = str(uuid.uuid1())
    new_curve = bpy.data.curves.new(type="FONT",name="text_curve_" + identifier)
    new_curve.extrude = 0.11
    content = text if text else random_text(text_file_path)
    new_text = bpy.data.objects.new("text_" + content, new_curve)
    new_text.data.body = content
    bpy.context.scene.objects.link(new_text)
    return new_text

def wireframize(obj, color, emission_strength = 1, thickness = random.uniform(0.0004, 0.001)):
    bpy.context.scene.objects.active = obj
    assert obj.type == 'MESH'
    obj.modifiers.new(name = 'wireframe', type='WIREFRAME')
    obj.modifiers['wireframe'].thickness = thickness
    make_object_emitter(obj, color, emission_strength)
    return obj

# randomize location and rotation of an object
def shuffle(obj, boundary):
    obj.location = rand_location(boundary)
    obj.rotation_euler = rand_rotation()

def add_object(obj, x, y, z, radius):
    new_obj = infer_primitive(obj, location=(x, y, z), radius=radius)
    bpy.data.groups['neons'].objects.link(new_obj)
    group_add(obj, new_obj)
    return new_obj

def infer_primitive(obj, **kwargs):
    if obj == 'Cube':
        bpy.ops.mesh.primitive_cube_add(radius = kwargs['radius'], location = kwargs['location'])
    elif obj == 'Ico':
        bpy.ops.mesh.primitive_ico_sphere_add(location = kwargs['location'])
    elif obj == 'Cone':
        bpy.ops.mesh.primitive_cone_add(location = kwargs['location'], radius1 = kwargs['radius'])
    elif obj == 'Pyramid':
        return build_pyramid(location = kwargs['location'])
    elif obj == 'Plane':
        bpy.ops.mesh.primitive_plane_add(location = kwargs['location'], radius = kwargs['radius'])
    return bpy.context.object

def group_add(group_name, obj):
    bpy.data.groups[group_name.lower().title()].objects.link(obj)

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

def glitch(obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    if obj.type == 'MESH':
        ints = list(range(10))
        target = str(ints.pop(int(random.uniform(0, len(ints) - 1))))
        replacement = str(ints.pop(int(random.uniform(0, len(ints)))))
        for vertex in obj.data.vertices:
            vertex.co = find_and_replace(vertex.co, target, replacement)
    elif obj.type == 'CURVE':
        for p in obj.data.splines.active.points:
            max_amplitude = 0.5
            p.co.z += random.uniform(-max_amplitude, max_amplitude)
    else:
        raise TypeError("object cannot be glitched")

def displace(obj, max_amplitude = 0.06):
    bpy.ops.object.mode_set(mode='OBJECT')
    assert obj.type == 'MESH'
    for vertex in obj.data.vertices:
        vertex.co = mathutils.Vector((vertex.co.x + random.uniform(-max_amplitude, max_amplitude), vertex.co.y + random.uniform(-max_amplitude, max_amplitude), vertex.co.z + random.uniform(-max_amplitude, max_amplitude)))

def subdivide(obj, cuts):
    if bpy.context.scene.objects.active != obj:
        bpy.context.scene.objects.active = obj
    assert bpy.context.scene.objects.active == obj
    bpy.ops.object.mode_set(mode='EDIT')
    for index in range(0, cuts):
        bpy.ops.mesh.subdivide(cuts)
    bpy.ops.object.editmode_toggle()

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
    print("Color scheme: adjacent colors")
    angle = (360 / number) / 360 # angles are in ?
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue_positions = []
    for i in range(number):
        hue_positions.append(angle * i)
    h = [(h + offset) % 1 for offset in hue_positions]
    return [colorsys.hls_to_rgb(hi, l, s) for hi in h]

# Use saturation increments to generate a color ramp palette
def color_ramp(r, g, b, number):
    print("Color scheme: color ramp")
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    res = []
    for i in range(number):
        saturation = ( s + i * random.uniform(-0.1, 0.1))
        lightness = (l + i * random.uniform(-0.1, 0.1) )
        hue = (h + i * random.uniform(-0.1, 0.1))
        res.append(colorsys.hls_to_rgb(h, lightness, saturation))
    return res

def rand_color_palette(number):
    function = random.choice([color_ramp, adjacent_colors])
    res = list(map(lambda x: list(x), function(rand_color_value(), rand_color_value(), rand_color_value(), number)))
    # add alpha component
    for i in res:
        i.append(1)
    print("palette: " + str(res))
    return res

def build_pyramid(width=random.uniform(1,3), length=random.uniform(1,3), height=random.uniform(1,3), location=(0,0,0)):
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

# Cuts a model horizontally into sub models like a scanner
def cut(obj, slices = 10):
    thiccness = obj.dimensions.z / slices
    gap = 0.01 * obj.dimensions.z
    center(obj)
    print("Slicing " + obj.name + " in " + str(slices) + " parts " + str(thiccness) + " thicc, gap: " + str(gap))
    base = obj.location.z - (obj.dimensions.z / 2)
    for i in range(0,slices - 1):
        dup = duplicate_object(obj)
        dup.name = 'subcut_' + obj.name + '_' + str(i)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = dup
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(0,0,base),plane_no=(0,0,1),clear_outer=False,clear_inner=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(0,0,base + thiccness),plane_no=(0,0,1),clear_outer=True,clear_inner=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        base += thiccness
        dup.location.z += i * gap
        dup.location.x += random.uniform(-0.2,0.2)
        dup.location.y += random.uniform(-0.2,0.2)
    obj.cycles_visibility.camera = False

def duplicate_object(obj):
    print("Cloning -> " + obj.name)
    new_object = obj.copy()
    new_object.data = obj.data.copy()
    new_object.animation_data_clear()
    new_object.cycles_visibility.camera = True
    bpy.context.scene.objects.link(new_object)
    return new_object

def load_random_obj(path):
    objs = [f for f in os.listdir(path) if f.endswith('.obj') and not f.endswith('_glitched.obj')]
    bpy.ops.import_scene.obj(filepath = path + random.choice(objs), use_edges=True)
    return bpy.context.selected_objects[0]

def random_text(file_path):
    lines = open(file_path).readlines()
    return lines[random.randrange(len(lines))]

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
  bpy.context.scene.objects.active = obj
  bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
  bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
  local_bounding_box_center = 0.125 * sum((mathutils.Vector(b) for b in obj.bound_box), mathutils.Vector())
  obj.location -= local_bounding_box_center
  obj.location = (0, 0, 0)
  return obj

def resize(obj, minimum = 4.0, maximum = 8.0):
  print("Resizing: " + obj.name)
  init_scale = obj.scale
  assert minimum < maximum
  scale_multiplier =init_scale.x / (max(obj.dimensions) / (maximum - minimum))
  if max(obj.dimensions) > maximum:
    print("Downscaling by:" + str(scale_multiplier))
    while max(obj.dimensions) > maximum:
      obj.scale = init_scale + mathutils.Vector((- scale_multiplier, - scale_multiplier, - scale_multiplier))
      bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
  elif max(obj.dimensions) < minimum:
    print("Upscaling by:" + str(scale_multiplier))
    while max(obj.dimensions) < minimum:
      obj.scale = obj.scale + mathutils.Vector((scale_multiplier, scale_multiplier, scale_multiplier))
      bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

def extrude(obj, thickness=0.05):
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(thickness, 0, 0), "constraint_orientation":'GLOBAL', "mirror":True, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    bpy.ops.object.mode_set(mode='OBJECT')

def create_line(name, point_list, color, thickness = 0.002, location = (0,0,0)):
    line_data = bpy.data.curves.new(name=name,type='CURVE')
    line_data.dimensions = '3D'
    line_data.fill_mode = 'FULL'
    # line_data.resolution_u = 4
    line_data.bevel_depth = thickness
    polyline = line_data.splines.new('POLY')
    # polyline = line_data.splines.new('BEZIER')
    polyline.points.add(len(point_list)-1) # splines.new return already 1 point
    # polyline.bezier_points.add(len(point_list)-1) # splines.new return already 1 point
    for idx, coord in enumerate(point_list):
        x,y,z = coord
        polyline.points[idx].co = (x, y, z, 1) # add weight
        # polyline.bezier_points[idx].co = (x, y, z)
    polyline.order_u = len(polyline.points)-1
    # polyline.use_endpoint_u = True
    line = bpy.data.objects.new(name, line_data)
    bpy.context.scene.objects.link(line)
    line.location = location
    make_object_emitter(line, color, 1.1)
    return line

def build_segment(location, function, length = 2, pitch = 0.5, name = None):
    verts = series(length, function, pitch)
    edges = []
    for v in range(0, (len(verts) - 1)):
        edges.append([v, v+1])
    name = name if name else 'segment_' + str(uuid.uuid1())
    return create_mesh(name, verts, [], location, edges)

def series(length, function, pitch):
    return list(map(lambda x: (0, x, function(x)), pitched_array(0.0, length, pitch)))

def pitched_array(minimum, maximum, pitch):
    return list(map(lambda x: (minimum + pitch * x), range(int((maximum - minimum) / pitch))))

def create_mesh(name, verts, faces, location, edges=[]):
    mesh_data = bpy.data.meshes.new("mesh_data")
    faces = faces if len(faces) == 0 else random_faces(verts)
    mesh_data.from_pydata(verts, edges, faces)
    mesh_data.update()
    obj = bpy.data.objects.new(name, mesh_data)
    obj.location = location
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.objects.active = obj
    center(obj)
    return obj

def camera_path(frame_number, radius = 5):
    fx = lambda x: radius * math.cos(x)
    fy = lambda y: radius * math.sin(y)
    factor = (2 * math.pi / NUMBER_OF_FRAMES)
    return list(map( lambda t: (fx(t * factor), fy(t * factor),  INITIAL_CAMERA_LOCATION[2]), range(0, NUMBER_OF_FRAMES)))

# Rotate vector
def rotate_vector(angle, axis, vin):
    # Assume axis is a unit vector.
    # Find squares of each axis component.
    xsq = axis.x * axis.x
    ysq = axis.y * axis.y
    zsq = axis.z * axis.z
    cosa = math.cos(angle)
    sina = math.sin(angle)
    complcos = 1.0 - cosa
    complxy = complcos * axis.x * axis.y
    complxz = complcos * axis.x * axis.z
    complyz = complcos * axis.y * axis.z
    sinx = sina * axis.x
    siny = sina * axis.y
    sinz = sina * axis.z
    # Construct the x-axis (i).
    ix = complcos * xsq + cosa
    iy = complxy + sinz
    iz = complxz - siny
    # Construct the y-axis (j).
    jx = complxy - sinz
    jy = complcos * ysq + cosa
    jz = complyz + sinx
    # Construct the z-axis (k).
    kx = complxz + siny
    ky = complyz - sinx
    kz = complcos * zsq + cosa
    vout = mathutils.Vector((0.0, 0.0, 0.0))
    vout.x = ix * vin.x + jx * vin.y + kx * vin.z
    vout.y = iy * vin.x + jy * vin.y + ky * vin.z
    vout.z = iz * vin.x + jz * vin.y + kz * vin.z
    return vout

#############
# </geometry>
#############


#############
# <physics>
#############

def add_rigid_body(objs=[], type = 'ACTIVE', mass=2.0):
  for obj in objs:
    obj.select = True
  bpy.ops.rigidbody.objects_add(type='ACTIVE')
  for obj in objs:
    if type == 'ACTIVE':
      obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = 'MESH'

#############
# </physics>
#############