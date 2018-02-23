import sys, code, random, os, math, bpy, mathutils, uuid

sys.path.append(os.path.dirname(__file__) + '/canvas.py')
canvas = __import__('canvas')

class Aether(canvas.Canvas):
  def spawn_emitter_fuild(self, location, emission_vector):
    bpy.ops.mesh.primitive_uv_sphere_add(location=location)
    emitter = self.last_added_object('Sphere')
    emitter.cycles_visibility.camera = False
    emitter.name = 'fluid_emitter' + str(uuid.uuid1())
    emitter.modifiers.new(name='emitter', type='FLUID_SIMULATION')
    emitter.modifiers['emitter'].settings.type = 'INFLOW'
    emitter.modifiers['emitter'].settings.inflow_velocity = emission_vector
    emitter.scale = (0.5, 0.5, 0.5)
    self.BAKED.append(emitter)
    return emitter

  def make_object_fluid_collider(self, obj):
      obj.modifiers.new(name='obstacle', type='FLUID_SIMULATION')
      obj.modifiers['obstacle'].settings.type = 'OBSTACLE'
      obj.modifiers['obstacle'].settings.volume_initialization = 'BOTH'
      obj.modifiers['obstacle'].settings.partial_slip_factor = 0.15

  def spawn_emitter_smoke(self, location, obj = None):
    if obj:
      emitter = obj
    else:
      bpy.ops.mesh.primitive_uv_sphere_add(location=location)
      emitter = self.last_added_object('Sphere')
    emitter.cycles_visibility.camera = False
    self.BAKED.append(emitter)
    emitter.name = 'smoke_emitter_' + str(uuid.uuid1())
    emitter.modifiers.new(name='emitter', type='SMOKE')
    emitter.modifiers['emitter'].smoke_type = 'FLOW'
    emitter.modifiers['emitter'].flow_settings.smoke_color = (self.rand_color_value(), self.rand_color_value(), self.rand_color_value())
    emitter.modifiers['emitter'].flow_settings.temperature = 1
    emitter.scale = (3,3,3)
    return emitter

  def make_object_smoke_collider(self, obj):
      obj.modifiers.new(name='obstacle', type='SMOKE')
      obj.modifiers['obstacle'].smoke_type = 'COLLISION'

  def render(self):
    ######################
    ## FLUID SIMULATION ##
    ######################
    self.SCENE.frame_end = self.NUMBER_OF_FRAMES

    RADIUS=20

    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 17),radius=RADIUS)
    container = self.last_added_object('CUBE')
    container.name = 'fluid_container'
    container.modifiers.new(name='container', type='FLUID_SIMULATION')
    container.modifiers.new(name='smooth_container', type='SMOOTH')
    container.modifiers['container'].settings.type = 'DOMAIN'
    container.modifiers['container'].settings.generate_particles = 5
    container.modifiers['container'].settings.surface_subdivisions = 100
    container.modifiers['container'].settings.viscosity_exponent = 6
    container.modifiers['container'].settings.viscosity_base = 1.0
    container.modifiers['container'].settings.resolution = 100
    container.modifiers['container'].settings.simulation_scale = 1
    container.modifiers['container'].settings.simulation_rate = 5
    self.BAKED.append(container)


    self.spawn_emitter_fuild((-2,-2,10),mathutils.Vector((-0.5, -0.5, -2)))
    self.spawn_emitter_fuild((2,2,10),mathutils.Vector((0.5, 0.5, -2)))

    self.assign_material(container, self.fetch_material('colorshift'))

    ######################
    ## SMOKE SIMULATION ##
    ######################

    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 17),radius=RADIUS)
    container = self.last_added_object('CUBE')
    container.name = 'smoke_container'
    container.modifiers.new(name='container', type='SMOKE')
    container.modifiers['container'].smoke_type = 'DOMAIN'
    container.modifiers['container'].domain_settings.use_high_resolution = True
    container.modifiers['container'].domain_settings.vorticity = 5
    self.BAKED.append(container)

    self.spawn_emitter_smoke(self.ORIGIN)

    # Bake animation
    print("*** Baking commence *** (you might see a bunch of gibberish popping up cause baking is not supposed to be used headlessly")
    bpy.ops.ptcache.free_bake_all() # free bake cache
    bpy.ops.ptcache.bake_all(bake = True)
    print("*** Baking finished ***")


