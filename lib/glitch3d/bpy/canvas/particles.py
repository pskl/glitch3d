def spawn_particles_system(base, object):
  particles = base.modifiers.new("Particles", type='PARTICLE_SYSTEM')
  settings = bpy.data.particles[-1]
  settings.emit_from = 'VERT'
  settings.physics_type = 'NO'
  settings.count = 10000 #default 1000
  settings.particle_size = 0.01
  settings.render_type = 'OBJECT'
  settings.dupli_object = bpy.data.objects['Cube']
  settings.show_unborn = True
  settings.use_dead = True
  settings.size_random = 0.5
  bpy.ops.object.duplicates_make_real()

bpy.ops.mesh.primitive_cube_add(location=(0, 0, 100),radius=1)
cube = last_added_object('CUBE')
assign_material(cube, random_material(['emission']))
spawn_particles_system(SUBJECT, cube)
