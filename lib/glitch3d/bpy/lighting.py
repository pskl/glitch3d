def add_spotlight(location, intensity, radians, name = 'spot'):
    bpy.ops.object.lamp_add(type='SPOT', radius=1.0, view_align=False, location=location)
    spot = last_added_object('Spot') # default name
    spot.name = name
    spot.data.node_tree.nodes['Emission'].inputs[1].default_value = intensity
    spot.data.spot_size = radians
    return spot

def let_there_be_light(scene):
  add_spotlight((0, 0, 12), 15000, math.radians(70), name = 'spot_1')
  spot1 = add_spotlight((0, 8, 4), 9000, math.radians(70), name = 'spot_2')
  spot2 = add_spotlight((0, -8, 4), 9000, math.radians(70), name = 'spot_3')
  spot1.rotation_euler.x -= math.radians(90)
  spot2.rotation_euler.x += math.radians(90)

  bpy.ops.mesh.primitive_plane_add(location=(0,8 + REFLECTOR_LOCATION_PADDING, 0))
  bpy.ops.mesh.primitive_plane_add(location=(8 + REFLECTOR_LOCATION_PADDING,0,0))
  bpy.ops.mesh.primitive_plane_add(location=(0, 0, 30))

  reflector1 = bpy.data.objects['Plane']
  reflector1.name = 'reflector_1'
  reflector2 = bpy.data.objects['Plane.001']
  reflector2.name = 'reflector_2'
  reflector3 = bpy.data.objects['Plane.002']
  reflector3.name = 'reflector_3'

  for r in [reflector1, reflector2, reflector3]:
    r.cycles_visibility.camera = False
    bpy.data.groups['reflectors'].objects.link(r)

  reflector2.rotation_euler.x += math.radians(90)
  reflector1.rotation_euler.x += math.radians(90)
  reflector2.rotation_euler.z += math.radians(90)

  make_object_reflector(reflector1)
  make_object_reflector(reflector2)
  make_object_reflector(reflector3)

  world = bpy.data.worlds.new('A Brave New World')
  world.use_nodes = True
  make_world_volumetric(world)
  scene.world = world

