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

REFLECTOR_SCALE = 5
REFLECTOR_STRENGTH = 12
REFLECTOR_LOCATION_PADDING = 10
WIREFRAME_THICKNESS = 0.008
ORIGIN  = (0,0,0)
props = []
CUBES = []
YELLOW = (1, 0.7, 0.1, 1)
GREY = (0.2, 0.2, 0.2 ,1)
BLUE = (0.1, 0.1, 0.8, 1)
WORDS = ['SEX', 'BLOOD', 'BITCOIN', 'PSKL', 'LOVE', 'SINGULARITY']

context = bpy.context
bpy.ops.mesh.primitive_cube_add(location=(-50, -50, -50),radius=1)
CUBE = bpy.data.objects['Cube']

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
    return './renders/' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '_' + str(datetime.date.today()) + '.png'

def rotate(model_object, index):
    model_object.rotation_euler[2] = math.radians(index * (360.0 / shots_number))

def rand_color_value():
    return round(random.uniform(0.1, 1.0), 10)

def rand_location():
    return (rand_location_value(), rand_location_value(), rand_location_value())

def rand_rotation():
    return (rand_rotation_value(), rand_rotation_value(), rand_rotation_value())

def rand_rotation_value():
    return round(random.uniform(0, 1), 10)

def rand_location_value():
    return round(random.uniform(-4, 4), 10)

def rand_color_vector():
    return (rand_color_value(), rand_color_value(), rand_color_value(), 1)

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
    emission_node.inputs[0].default_value = rand_color_vector()
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
    WORDS.remove(chosen_word)
    return chosen_word

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
    reflector1.data.materials[-1].node_tree.nodes['Emission'].inputs[0].default_value = rand_color_vector()
    reflector2.data.materials[-1].node_tree.nodes['Emission'].inputs[0].default_value = rand_color_vector()

def add_cube(x,y,z,radius):
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z),radius=radius)
    CUBES.append(bpy.data.objects[-1])

def build_composite_cube(size, radius):
    build_grid_cube(size, -size, radius)
    for z in range(0, size):
        build_grid_cube(size, CUBES[-1].location.z + 2 * radius, radius)

def build_grid_cube(size, z_index, radius):
    build_cube_line(size, z_index, -size, radius)
    for y in range(0, size): 
        build_cube_line(size, z_index, CUBES[-1].location.y + 2 * radius, radius)  

def build_cube_line(size, z_index, y_index, radius):
    add_cube(-size, y_index, z_index, radius)
    for x in range(0, size):
        new_cube=duplicate_object(CUBES[-1])
        CUBES.append(new_cube)
        new_cube.location = ((CUBES[-1].location.x + 2 * radius), y_index, z_index)

def displace(vector):
    return mathutils.Vector((vector.x + random.uniform(-0.08, 0.08), vector.y + random.uniform(-0.08, 0.08), vector.z + random.uniform(-0.08, 0.08)))    

def glitch(object):
    bpy.ops.object.mode_set(mode='OBJECT')
    assert object.type == 'MESH'    
    for vertex in object.data.vertices:
        vertex.co = displace(vertex.co)
    
def subdivide(object, cuts):
    assert context.scene.objects.active == object
    bpy.ops.object.mode_set(mode='EDIT')
    for index in range(0, cuts):  
        bpy.ops.mesh.subdivide(cuts)

def add_ocean(spatial_size, resolution):
    add_cube(0,0,0,1)
    ocean = CUBES[-1]
    context.scene.objects.active = ocean
    bpy.ops.object.modifier_add(type='OCEAN')
    ocean.modifiers["Ocean"].spatial_size = spatial_size
    ocean.modifiers["Ocean"].resolution = resolution
    make_object_transparent(ocean, BLUE)
    ocean.name = 'Chillwaves~'
    return ocean



