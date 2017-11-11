######################
## FLUID SIMULATION ##
######################
SCENE.frame_end = NUMBER_OF_FRAMES

RADIUS=20

# Container
bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.4),radius=RADIUS)
container = last_added_object('CUBE')
container.name = 'Container'
container.modifiers.new(name='container', type='FLUID_SIMULATION')
container.modifiers['container'].settings.type = 'DOMAIN'
container.modifiers['container'].settings.generate_particles = 1
container.modifiers['container'].settings.surface_subdivisions = 100
container.modifiers['container'].settings.viscosity_exponent = 6
container.modifiers['container'].settings.viscosity_base = 1.0
container.modifiers['container'].settings.simulation_scale = 1

container.location = (0, 0, 0)

# Emitter of fluid
bpy.ops.mesh.primitive_uv_sphere_add(location=(0,0,((RADIUS/2) - 2)))
emitter = bpy.data.objects['Sphere']
emitter.cycles_visibility.camera = False
emitter.name = 'Emitter'
emitter.modifiers.new(name='emitter', type='FLUID_SIMULATION')
emitter.modifiers['emitter'].settings.type = 'INFLOW'
emitter.modifiers['emitter'].settings.inflow_velocity = mathutils.Vector((0, 0.5, -2))
emitter.scale = (0.5, 0.5, 0.5)

def spawn_emitter_fuild(location, emission_vector):
  bpy.ops.mesh.primitive_uv_sphere_add(location=location)
  emitter = bpy.data.objects['Sphere']
  emitter.cycles_visibility.camera = False
  emitter.name = 'Emitter'
  emitter.modifiers.new(name='emitter', type='FLUID_SIMULATION')
  emitter.modifiers['emitter'].settings.type = 'INFLOW'
  emitter.modifiers['emitter'].settings.inflow_velocity = emission_vector
  emitter.scale = (0.5, 0.5, 0.5)

spawn_emitter_fuild((0,0,((RADIUS/2) - 2)),mathutils.Vector((0.5, 0.5, -2)))
spawn_emitter_fuild((0,0,((RADIUS/2) - 5)),mathutils.Vector((0., -0.5, -0.5)))

# make_object_transparent(container)
make_object_gradient_fabulous(container, rand_color(), rand_color())
make_object_fluid_collider(SUBJECT)
make_object_fluid_collider(OCEAN[0])

# Bake animation
print("*** Baking commence *** (you might see a bunch of gibberish popping up cause baking is not supposed to be used headlessly")
bpy.ops.fluid.bake({'scene': context.scene, 'active_object': container})
print("*** Baking finished ***")