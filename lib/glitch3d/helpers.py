# Helper methods
def look_at(camera_object, point):
    location_camera = camera_object.matrix_world.to_translation()
    location_point = point.matrix_world.to_translation()
    direction = location_point - location_camera
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera_object.rotation_euler = rot_quat.to_euler()

def shoot(camera, model_object, filepath):
    look_at(camera, model_object)
    print('Camera now at location: ' + camera_location_string(camera) + ' / rotation: ' + camera_rotation_string(camera))
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

def output_name(index, model_path):
    return 'renders/' + os.path.splitext(model_path)[0].split('/')[1] + '_' + str(index) + '_' + str(datetime.date.today()) + '.png'

def rotate(model_object):
    model_object.rotation_euler.z = model_object.rotation_euler.z + 0.5

def rand_color_value():
    return randint(0, 1)

def randomize_material(model_object):
    model_material = bpy.data.materials.new('Model Material')
    model_material.use_shadeless = True
    model_material.emit = 0.8
    model_material.diffuse_color = (rand_color_value(), rand_color_value(), rand_color_value())
    model_material.diffuse_shader = 'TOON'
    model_object.data.materials.append(model_material)

# Reposition camera until the model object is within the frustum
def reposition(camera_object, model_object):
    ""
def get_args():
  parser = argparse.ArgumentParser()

  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]

  # add parser rules
  parser.add_argument('-f', '--file', help="obj file to render")
  parser.add_argument('-u', '--furthest_vertex', help="furthest vertice")
  parser.add_argument('-n', '--shots_number', help="number of shots")
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args

def camera_rotation_string(camera):
    return str(int(camera.rotation_euler.x)) + ' ' + str(int(camera.rotation_euler.y)) + ' ' + str(int(camera.rotation_euler.z))

def camera_location_string(camera):
    return str(int(camera.location.x)) + ' ' + str(int(camera.location.y)) + ' ' + str(int(camera.location.z))

def check_object_within_frustum(scene, model_object, camera):
    bpy.context.scene.objects.active = model_object
    bpy.ops.object.mode_set(mode = 'EDIT')
    mesh = model_object.data
    mat_world = model_object.matrix_world
    cs, ce = camera.data.clip_start, camera.data.clip_end
    # assert model_object.mode == "EDIT"
    bm = bmesh.from_edit_mesh(mesh)
    for v in bm.verts:
        co_ndc = world_to_camera_view(scene, camera, mat_world * v.co)
        if (0.0 < co_ndc.x < 1.0 and
            0.0 < co_ndc.y < 1.0 and
             cs < co_ndc.z <  ce):
            v.select = True
        else:
            v.select = False
    bmesh.update_edit_mesh(mesh, False, False)
    return v.select
