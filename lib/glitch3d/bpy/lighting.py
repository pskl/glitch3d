def let_there_be_light(scene):
  add_spotlight((0, 0, 12), 14000, math.radians(60))
  spot1 = add_spotlight((0, 8, 4), 8000, math.radians(60))
  spot2 = add_spotlight((0, -8, 4), 8000, math.radians(60))
  spot1.rotation_euler.x -= math.radians(90)
  spot2.rotation_euler.x += math.radians(90)

  bpy.ops.mesh.primitive_plane_add(location=(0,8 + REFLECTOR_LOCATION_PADDING, 0))
  bpy.ops.mesh.primitive_plane_add(location=(8 + REFLECTOR_LOCATION_PADDING,0,0))
  bpy.ops.mesh.primitive_plane_add(location=(0, 0, 30))

  reflector1 = bpy.data.objects['Plane']
  reflector2 = bpy.data.objects['Plane.001']
  reflector3 = bpy.data.objects['Plane.002']

  bpy.data.groups.new('Plane')
  bpy.data.groups['Plane'].objects.link(reflector1)
  bpy.data.groups['Plane'].objects.link(reflector2)
  bpy.data.groups['Plane'].objects.link(reflector3)

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