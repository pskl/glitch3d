import sys, code, random, os, math, bpy, mathutils, uuid, canvas

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import helpers

class Aether(canvas.Canvas):
  def render(self):
    ######################
    ## FLUID SIMULATION ##
    ######################
    RADIUS=20

    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 17),radius=RADIUS)
    container = bpy.context.object
    container.name = 'fluid_container'
    container.modifiers.new(name='container', type='FLUID_SIMULATION')
    container.modifiers.new(name='smooth_container', type='SMOOTH')
    container.modifiers['container'].settings.type = 'DOMAIN'
    container.modifiers['container'].settings.generate_particles = 5
    container.modifiers['container'].settings.surface_subdivisions = 50
    container.modifiers['container'].settings.viscosity_exponent = 6
    container.modifiers['container'].settings.viscosity_base = 1.0
    container.modifiers['container'].settings.resolution = 25
    container.modifiers['container'].settings.simulation_scale = 1
    container.modifiers['container'].settings.simulation_rate = 5

    self.spawn_emitter_fluid((-2,-2,10),mathutils.Vector((-0.5, -0.5, -2)))
    self.spawn_emitter_fluid((2,2,10),mathutils.Vector((0.5, 0.5, -2)))

    helpers.assign_material(container, helpers.random_material(self.MATERIALS_NAMES))

    ######################
    ## SMOKE SIMULATION ##
    ######################

    # bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 17),radius=RADIUS)
    # container = bpy.context.object
    # container.name = 'smoke_container'
    # container.modifiers.new(name='container', type='SMOKE')
    # container.modifiers['container'].smoke_type = 'DOMAIN'
    # container.modifiers['container'].domain_settings.use_high_resolution = True
    # container.modifiers['container'].domain_settings.vorticity = 3
    # self.spawn_emitter_smoke(self.ORIGIN)
    # self.make_object_smoke_collider(self.SUBJECT)

    # Bake animation
    print("*** Baking commence *** (you might see a bunch of gibberish popping up cause baking is not supposed to be used headlessly")
    bpy.ops.ptcache.free_bake_all() # free bake cache
    bpy.ops.ptcache.bake_all(bake = True)
    print("*** Baking finished ***")

  def spawn_emitter_fluid(self, location, emission_vector):
    bpy.ops.mesh.primitive_uv_sphere_add(location=location)
    emitter = bpy.context.object
    emitter.cycles_visibility.camera = False
    emitter.name = 'fluid_emitter_' + str(uuid.uuid1())
    emitter.modifiers.new(name='emitter', type='FLUID_SIMULATION')
    emitter.modifiers['emitter'].settings.type = 'INFLOW'
    emitter.modifiers['emitter'].settings.inflow_velocity = emission_vector
    emitter.scale = (0.5, 0.5, 0.5)
    return emitter

  def make_object_fluid_collider(self, obj):
      obj.modifiers.new(name='obstacle', type='FLUID_SIMULATION')
      obj.modifiers['obstacle'].settings.type = 'OBSTACLE'
      obj.modifiers['obstacle'].settings.volume_initialization = 'BOTH'
      obj.modifiers['obstacle'].settings.partial_slip_factor = 0.15

  def spawn_emitter_smoke(self, location, obj = None):
    bpy.ops.mesh.primitive_uv_sphere_add(location=location)
    emitter = bpy.context.object
    emitter.cycles_visibility.camera = False
    emitter.name = 'smoke_emitter_' + str(uuid.uuid1())
    emitter.modifiers.new(name='emitter', type='SMOKE')
    emitter.modifiers['emitter'].smoke_type = 'FLOW'
    emitter.modifiers['emitter'].flow_settings.smoke_color = (helpers.rand_color_value(), helpers.rand_color_value(), helpers.rand_color_value())
    emitter.modifiers['emitter'].flow_settings.temperature = 1
    emitter.scale = (3,3,3)
    return emitter

  def make_object_smoke_collider(self, obj):
      obj.modifiers.new(name='obstacle', type='SMOKE')
      obj.modifiers['obstacle'].smoke_type = 'COLLISION'

