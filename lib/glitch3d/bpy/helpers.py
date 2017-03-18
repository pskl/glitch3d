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
PROPS_NUMBER = 100
SHADERS = ['ShaderNodeBsdfGlossy', 'ShaderNodeBsdfDiffuse', 'ShaderNodeBsdfVelvet', 'ShaderNodeEmission']
props = []
YELLOW = (1,0.7,0.1,1)
WORDS = ['POWER', 'MONEY', 'SEX', 'BLOOD', 'DOLLARS', 'PSKL', 'SKYNET', 'LOVE']

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
    look_at(camera, model_object)
    print('Camera now at location: ' + camera_location_string(camera) + ' / rotation: ' + camera_rotation_string(camera))
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

def output_name(index, model_path):
    return './' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '_' + str(datetime.date.today()) + '.png'

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
    return round(random.uniform(-5, 5), 10)

def rand_color_vector():
    return (rand_color_value(), rand_color_value(), rand_color_value(), 1)

def rand_scale():
    return round(random.uniform(0, 0.2), 10)

def rand_scale_vector():
    scale = rand_scale()
    return(scale, scale, scale)

def unwrap_model(obj):
    if obj == camera_object or obj.name.startswith('Text'):
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
    texture_path = texture_folder_path + random.choice(os.listdir(texture_folder_path))
    logging.info('---------')
    logging.info(texture_folder_path)
    logging.info('---------')
    return bpy.data.images.load(texture_path)

def assign_texture_to_material(material, texture):
    assert material.use_nodes == True
    # If its a default material
    bsdf_node = material.node_tree.nodes['Diffuse BSDF']
    texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
    texture_node.image = texture
    material.node_tree.links.new(texture_node.outputs['Color'], bsdf_node.inputs['Color'])

def make_object_gold(obj):
    material = bpy.data.materials.new('Gold Material - ' + str(uuid.uuid1()))
    material.use_nodes = True
    glossy_node = material.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    glossy_node.inputs[0].default_value = YELLOW
    # roughness
    glossy_node.inputs[1].default_value = 0.2
    assign_node_to_output(material, glossy_node)
    assign_material(obj, material)

def make_object_reflector(obj):
    obj.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
    emissive_material = bpy.data.materials.new('Emissive Material #' + str(index))
    emissive_material.use_nodes = True
    emission_node = emissive_material.node_tree.nodes.new('ShaderNodeEmission')
    # Set color
    emission_node.inputs[0].default_value = rand_color_vector()
    # Set strength
    emission_node.inputs[1].default_value = REFLECTOR_STRENGTH
    assign_node_to_output(emissive_material, emission_node)
    assign_material(obj, emissive_material)

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
    return random.choice(WORDS)

def spawn_text():
    identifier = str(uuid.uuid1())
    new_curve = bpy.data.curves.new(type="FONT",name="Curve - " + identifier)
    new_curve.extrude = 0.15
    new_text = bpy.data.objects.new("Text - " + identifier, new_curve)
    new_text.data.body = random_text()
    bpy.context.scene.objects.link(new_text)
    return new_text

def shuffle(obj):
    obj.location = rand_location()
    obj.scale = rand_scale_vector()
    obj.rotation_euler = rand_rotation()
