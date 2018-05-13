import bpy, sys, code, random, os, math, canvas, operator, mathutils

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Particles(canvas.Canvas):
  def render(self):
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 100),radius=1)
    cube = bpy.context.object
    helpers.assign_material(cube, helpers.random_material(self.MATERIALS_NAMES))
    self.spawn_particles_system(self.SUBJECT, cube)

    for f in range(self.NUMBER_OF_FRAMES):
      bpy.context.scene.frame_set(f)
      self.SUBJECT.particle_systems["ParticleSystem"].seed += 1
      self.SUBJECT.scale += mathutils.Vector((0.1,0.1,0.1))
      helpers.add_frame([self.SUBJECT], ['particle_systems["ParticleSystem"].seed', 'scale'])

  def spawn_particles_system(self, base, obj):
    base.modifiers.new("Particles", type='PARTICLE_SYSTEM')
    settings = bpy.data.particles[-1]
    settings.emit_from = 'VERT'
    settings.physics_type = 'NO'
    settings.count = 2000 # default 1000
    settings.particle_size = 0.01
    settings.render_type = 'OBJECT'
    settings.dupli_object = obj
    settings.show_unborn = True
    settings.use_dead = True
    settings.size_random = 0.5
    bpy.ops.object.duplicates_make_real()


