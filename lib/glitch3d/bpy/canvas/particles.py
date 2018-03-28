import bpy, sys, code, random, os, math

sys.path.append(os.path.dirname(__file__) + '/canvas.py')
canvas = __import__('canvas')

class Particles(canvas.Canvas):
  def spawn_particles_system(self, base, object):
    base.modifiers.new("Particles", type='PARTICLE_SYSTEM')
    settings = bpy.data.particles[-1]
    settings.emit_from = 'VERT'
    settings.physics_type = 'NO'
    settings.count = 2000 #default 1000
    settings.particle_size = 0.01
    settings.render_type = 'OBJECT'
    settings.dupli_object = bpy.data.objects['Cube']
    settings.show_unborn = True
    settings.use_dead = True
    settings.size_random = 0.5
    bpy.ops.object.duplicates_make_real()

  def render(self):
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 100),radius=1)
    cube = self.last_added_object('Cube')
    self.assign_material(cube, self.random_material(['emission']))
    self.spawn_particles_system(self.SUBJECT, cube)

