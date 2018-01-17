######################
## FLUID SIMULATION ##
######################
SCENE.frame_end = NUMBER_OF_FRAMES

RADIUS=20

bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.4),radius=RADIUS)
container = last_added_object('CUBE')
container.name = 'fluid_container'
container.modifiers.new(name='container', type='FLUID_SIMULATION')
container.modifiers['container'].settings.type = 'DOMAIN'
container.modifiers['container'].settings.generate_particles = 1
container.modifiers['container'].settings.surface_subdivisions = 100
container.modifiers['container'].settings.viscosity_exponent = 6
container.modifiers['container'].settings.viscosity_base = 1.0
container.modifiers['container'].settings.simulation_scale = 1
container.location = (0, 0, 0)

def spawn_emitter_fuild(location, emission_vector):
  bpy.ops.mesh.primitive_uv_sphere_add(location=location)
  emitter = last_added_object('Sphere')
  emitter.cycles_visibility.camera = False
  emitter.name = 'Fluid Emitter' + str(uuid.uuid1())
  emitter.modifiers.new(name='emitter', type='FLUID_SIMULATION')
  emitter.modifiers['emitter'].settings.type = 'INFLOW'
  emitter.modifiers['emitter'].settings.inflow_velocity = emission_vector
  emitter.scale = (0.5, 0.5, 0.5)
  return emitter

def make_object_fluid_collider(obj):
    obj.modifiers.new(name='obstacle', type='FLUID_SIMULATION')
    obj.modifiers['obstacle'].settings.type = 'OBSTACLE'
    obj.modifiers['obstacle'].settings.volume_initialization = 'BOTH'
    obj.modifiers['obstacle'].settings.partial_slip_factor = 0.15

spawn_emitter_fuild((0,0,((RADIUS/2) - 2)),mathutils.Vector((0.5, 0.5, -2)))
spawn_emitter_fuild((0,3,((RADIUS/2) - 2)),mathutils.Vector((0., -0.5, -0.5)))

make_object_gradient_fabulous(container, rand_color(), rand_color())
container.modifiers.new(name='Container Subsurf', type='SUBSURF')
make_object_fluid_collider(SUBJECT)

if OCEAN:
  make_object_fluid_collider(OCEAN[1])

# Bake animation
print("*** Baking commence *** (you might see a bunch of gibberish popping up cause baking is not supposed to be used headlessly")
bpy.ops.fluid.bake({'scene': context.scene, 'active_object': container})
print("*** Baking finished ***")