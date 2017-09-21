import bpy
import argparse
import datetime
import bmesh
import random
import code
import math
import mathutils
import random
import uuid
import sys
import logging
import string
import colorsys

REFLECTOR_SCALE = random.uniform(4, 6)
REFLECTOR_STRENGTH = random.uniform(8, 12)
REFLECTOR_LOCATION_PADDING = random.uniform(10, 12)
WIREFRAME_THICKNESS = random.uniform(0.008, 0.01)
DISPLACEMENT_AMPLITUDE = random.uniform(0.06, 0.08)
REPLACE_TARGET = '6'
REPLACEMENT = '2'
ORIGIN  = (0,0,0)
NUMBER_OF_FRAMES = 100

PRIMITIVES = ['PYRAMID', 'CUBE']
props = []
YELLOW = (1, 0.7, 0.1, 1)
GREY = (0.2, 0.2, 0.2 ,1)
BLUE = (0.1, 0.1, 0.8, 1)
PINK = (0.8, 0.2, 0.7, 1.0)
WORDS = string.ascii_lowercase
WIREFRAMES = []

context = bpy.context

def debug():
    code.interact(local=dict(globals(), **locals()))
    sys.exit("Aborting execution")

# Helper methods
def look_at(camera_object, point):
    location_camera = camera_object.matrix_world.to_translation()
    location_point = point.matrix_world.to_translation()
    direction = location_point - location_camera
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera_object.rotation_euler = rot_quat.to_euler()

def empty_materials():
    for material in bpy.data.materials.keys():
        bpy.data.materials.remove(object.data.materials[material])

def shoot(camera, model_object, filepath):
    directory = os.path.dirname('./renders')
    if not os.path.exists(directory):
      os.makedirs(directory)
    look_at(camera, model_object)
    print('Camera now at location: ' + camera_location_string(camera) + ' / rotation: ' + camera_rotation_string(camera))
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

def output_name(index, model_path):
    return './renders/' + os.path.splitext(model_path)[0].split('/')[-1] + '_' + str(index) + '_' + str(datetime.date.today()) + '.png'

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
    return round(random.uniform(0, 1), 10)

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

def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
    # add parser rules
    parser.add_argument('-f', '--file', help="obj file to render")
    parser.add_argument('-n', '--shots-number', help="number of shots desired")
    parser.add_argument('-m', '--mode', help="quality mode: low | high")
    parser.add_argument('-p', '--path', help="root path of assets")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

def camera_rotation_string(camera):
    return str(int(camera.rotation_euler.x)) + ' ' + str(int(camera.rotation_euler.y)) + ' ' + str(int(camera.rotation_euler.z))

def camera_location_string(camera):
    return str(int(camera.location.x)) + ' ' + str(int(camera.location.y)) + ' ' + str(int(camera.location.z))

def assign_material(model_object, material):
    model_object.data.materials.append(material)

def assign_node_to_output(material, new_node):
    assert material.use_nodes == True
    output_node = material.node_tree.nodes['Material Output']
    material.node_tree.links.new(new_node.outputs[0], output_node.inputs['Surface'])

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
    bsdf_node = material.node_tree.nodes['Diffuse BSDF']
    texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
    texture_node.image = texture
    material.node_tree.links.new(texture_node.outputs['Color'], bsdf_node.inputs['Color'])

def make_object_glossy(obj, color):
    material = bpy.data.materials.new('Glossy Material - ' + str(uuid.uuid1()))
    material.use_nodes = True
    glossy_node = material.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    glossy_node.inputs[0].default_value = color
    # roughness
    glossy_node.inputs[1].default_value = 0.2
    assign_node_to_output(material, glossy_node)
    assign_material(obj, material)

def make_object_reflector(obj):
    obj.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
    make_object_emitter(obj, REFLECTOR_STRENGTH)

def make_object_transparent(obj, color):
    material = bpy.data.materials.new('Transparent Material - ' + str(uuid.uuid1()))
    material.use_nodes = True
    node = material.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    node.inputs[0].default_value = color
    assign_node_to_output(material, node)
    assign_material(obj, material)

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

def randomize_reflectors_colors():
    reflector1.data.materials[-1].node_tree.nodes['Emission'].inputs[0].default_value = rand_color()
    reflector2.data.materials[-1].node_tree.nodes['Emission'].inputs[0].default_value = rand_color()

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
def displace(vector):
    return mathutils.Vector((vector.x + random.uniform(-DISPLACEMENT_AMPLITUDE, DISPLACEMENT_AMPLITUDE), vector.y + random.uniform(-DISPLACEMENT_AMPLITUDE, DISPLACEMENT_AMPLITUDE), vector.z + random.uniform(-DISPLACEMENT_AMPLITUDE, DISPLACEMENT_AMPLITUDE)))

# Replace vertex coordinate everywhere
def find_and_replace(vector):
    return mathutils.Vector((float(str(vector.x).replace(REPLACE_TARGET, REPLACEMENT)), float(str(vector.y).replace(REPLACE_TARGET, REPLACEMENT)), float(str(vector.z).replace(REPLACE_TARGET, REPLACEMENT))))

def glitch(object):
    bpy.ops.object.mode_set(mode='OBJECT')
    assert object.type == 'MESH'
    for vertex in object.data.vertices:
        vertex.co = find_and_replace(vertex.co)

def subdivide(object, cuts):
    if context.scene.objects.active != object:
        context.scene.objects.active = object
    assert context.scene.objects.active == object
    bpy.ops.object.mode_set(mode='EDIT')
    for index in range(0, cuts):
        bpy.ops.mesh.subdivide(cuts)

def add_ocean(spatial_size, resolution):
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, -1),radius=1)
    ocean = last_added_object('CUBE')
    context.scene.objects.active = ocean
    ocean.scale = (2,2,2)
    bpy.ops.object.modifier_add(type='OCEAN')
    ocean.modifiers["Ocean"].spatial_size = spatial_size
    ocean.modifiers["Ocean"].resolution = resolution
    make_object_glossy(ocean, rand_color())
    ocean.name = 'Ocean'
    return ocean

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

def build_pyramid(width=1.0, length=1.0, height=1.0, location=ORIGIN):
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
    id = str(uuid.uuid1())
    return create_mesh('Pyramid ' + id, verts, faces, location)

