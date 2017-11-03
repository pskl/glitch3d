def let_there_be_light(scene):
  add_spotlight((0, 0, 12), 15000, math.radians(70))
  spot1 = add_spotlight((0, 8, 4), 9000, math.radians(70))
  spot2 = add_spotlight((0, -8, 4), 9000, math.radians(70))
  spot1.rotation_euler.x -= math.radians(90)
  spot2.rotation_euler.x += math.radians(90)

  bpy.ops.mesh.primitive_plane_add(location=(0,8 + REFLECTOR_LOCATION_PADDING, 0))
  bpy.ops.mesh.primitive_plane_add(location=(8 + REFLECTOR_LOCATION_PADDING,0,0))
  bpy.ops.mesh.primitive_plane_add(location=(0, 0, 30))

  reflector1 = bpy.data.objects['Plane']
  reflector2 = bpy.data.objects['Plane.001']
  reflector3 = bpy.data.objects['Plane.002']

  for r in [reflector1, reflector2, reflector3]:
    r.cycles_visibility.camera = False
    bpy.data.groups['Planes'].objects.link(r)
    bpy.data.groups['Reflectors'].objects.link(r)

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