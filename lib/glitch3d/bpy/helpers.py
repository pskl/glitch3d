YELLOW = (1,0.7,0.1,1)

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
    return 'renders/' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '_' + str(datetime.date.today()) + '.png'

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
    return round(random.uniform(-8, 8), 10)

def rand_color_vector():
    return (rand_color_value(), rand_color_value(), rand_color_value(), 1)

def rand_scale():
    return round(random.uniform(0, 0.15), 10)

def rand_scale_vector():
    return(rand_scale(), rand_scale(), rand_scale())

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
    # nodes = material.node_tree.nodes
    # new_node = nodes.new(random.choice(SHADERS))
    # assign_node_to_output(material, new_node)
    return material

def random_texture():
    texture_path = os.path.expanduser('fixtures/textures/checkered_texture.jpg')
    # new_texture = bpy.data.textures.new('ColorTex', type = 'IMAGE')
    return bpy.data.images.load(texture_path)
    # rand.choice()

def assign_texture_to_material(material, texture):
    assert material.use_nodes == True
    # If its a default material
    bsdf_node = material.node_tree.nodes['Diffuse BSDF']
    assign_node_to_output(material, bsdf_node)
    texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
    uv_node = material.node_tree.nodes.new('ShaderNodeUVMap')
    uv_node.uv_map = 'UV'
    texture_node.image = texture
    material.node_tree.links.new(texture_node.outputs[0], bsdf_node.inputs[0])
    material.node_tree.links.new(texture_node.inputs['Vector'], uv_node.outputs['UV'])

def make_object_gold(object):
    material = bpy.data.materials.new('Gold Material - ' + str(uuid.uuid1()))
    material.use_nodes = True
    glossy_node = material.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    glossy_node.inputs[0].default_value = YELLOW
    # roughness
    glossy_node.inputs[1].default_value = 0.1
    assign_node_to_output(material, glossy_node)
    assign_material(object, material)

def make_object_reflector(object):
    object.scale = (REFLECTOR_SCALE, REFLECTOR_SCALE, REFLECTOR_SCALE)
    emissive_material = bpy.data.materials.new('Emissive Material #' + str(index))
    emissive_material.use_nodes = True
    emission_node = emissive_material.node_tree.nodes.new('ShaderNodeEmission')
    # Set color
    emission_node.inputs[0].default_value = rand_color_vector()
    # Set strength
    emission_node.inputs[1].default_value = REFLECTOR_STRENGTH
    assign_node_to_output(emissive_material, emission_node)
    assign_material(object, emissive_material)
